#!/usr/bin/env python3
"""
入試問題分析アプリケーション（CLIバージョン）
統合ワークフロー：学校・年度選択 → BunkoOCR → 分析 → Excel記録
"""

import subprocess
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
import os
import sys

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter


class EntranceExamAnalyzerCLI:
    """入試問題分析アプリケーション（CLI版）"""
    
    def __init__(self):
        # BunkoOCR関連設定
        self.bunko_app = "/Applications/bunkoOCR.app"
        self.results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 過去問フォルダのパス
        self.kakomon_dir = Path.home() / "Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
        
        # 学校リストを動的に生成
        self.schools = self.get_schools_from_kakomon_folder()
        
        # 学校別の利用可能な年度を収集
        self.school_years = self.get_available_years_by_school()
        
    def get_schools_from_kakomon_folder(self):
        """過去問フォルダから学校名を自動的に取得（年度フォルダ内も含む）"""
        import re
        
        schools = set()  # 重複を避けるためセットを使用
        
        if not self.kakomon_dir.exists():
            # フォルダが存在しない場合はデフォルトリストを返す
            return [
                "開成中学校",
                "麻布中学校",
                "武蔵中学校",
                "桜蔭中学校",
                "女子学院中学校",
                "雙葉中学校",
                "渋谷教育学園渋谷中学校",
                "慶應義塾中等部",
                "早稲田実業学校中等部"
            ]
        
        # 年度パターンを定義
        year_pattern = re.compile(r'^(19|20)\d{2}')
        
        def extract_school_name(name):
            """学校名を正規化"""
            # 年度プレフィックスを削除（例：23開成 → 開成）
            name = re.sub(r'^\d{2}', '', name)
            # 中学校が付いていない場合は追加
            if '中学校' not in name and '中等部' not in name and '駒場' not in name:
                name = name + '中学校'
            return name
        
        # 第1階層のフォルダを処理
        for item in self.kakomon_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 年度フォルダまたは「過去問」を含むフォルダの場合
                if year_pattern.match(item.name) or '過去問' in item.name:
                    # サブフォルダを確認
                    for subitem in item.iterdir():
                        if subitem.is_dir() and not subitem.name.startswith('.'):
                            school_name = extract_school_name(subitem.name)
                            schools.add(school_name)
                else:
                    # 直接の学校フォルダ
                    school_name = extract_school_name(item.name)
                    schools.add(school_name)
        
        # リストに変換してソート
        schools_list = sorted(list(schools))
        
        # 見つからない場合はデフォルトリストを返す
        if not schools_list:
            return [
                "開成中学校",
                "麻布中学校",
                "武蔴中学校",
                "桜蔭中学校",
                "女子学院中学校",
                "雙葉中学校",
                "渋谷教育学園渋谷中学校",
                "慶應義塾中等部",
                "早稲田実業学校中等部"
            ]
            
        return schools_list
    
    def get_available_years_by_school(self):
        """学校別に利用可能な年度を取得"""
        from collections import defaultdict
        import re
        
        school_years = defaultdict(set)
        
        if not self.kakomon_dir.exists():
            return school_years
        
        # 年度パターン
        year_patterns = [
            re.compile(r'(\d{4})年'),  # 2024年
            re.compile(r'(\d{4})'),    # 2024
        ]
        
        # PDFファイルを検索
        for pdf_file in self.kakomon_dir.glob('**/*.pdf'):
            # 解答ファイルは除外
            if '解答' in pdf_file.name or 'kaito' in pdf_file.name:
                continue
            
            # 年度を抽出
            year = None
            full_path = str(pdf_file)
            
            for pattern in year_patterns:
                matches = pattern.findall(full_path)
                for match in matches:
                    if match.isdigit() and 2000 <= int(match) <= 2030:
                        year = match
                        break
                if year:
                    break
            
            if year:
                # 学校名を推定
                for school in self.schools:
                    school_base = school.replace('中学校', '').replace('中等部', '')
                    if school_base in full_path:
                        school_years[school].add(year)
                        break
        
        return school_years
    
    def find_pdf_for_school_year(self, school_name, year):
        """指定された学校と年度のPDFを階層的に検索"""
        school_base = school_name.replace('中学校', '').replace('中等部', '')
        
        # 検索パターンを定義（優先度順）
        search_patterns = [
            # 直接的なパターン
            f"**/{year}年{school_name}*国語*.pdf",
            f"**/{school_name}*{year}*.pdf",
            f"**/{year}*{school_base}*.pdf",
            f"**/{school_base}*{year}*.pdf",
            # フォルダ構造を考慮
            f"**/{school_base}/**/*{year}*.pdf",
            f"**/{year}/**/*{school_base}*.pdf",
            f"**/{year}*/**/{school_base}*.pdf",
            # 短縮名パターン（23開成など）
            f"**/{year[-2:]}{school_base}*.pdf",
            f"**/{year[-2:]}{school_base}/*mondai*.pdf",
            f"**/{school_base}{year[-2:]}.pdf",
            # 一般的なパターン
            f"**/*{year[-2:]}*{school_base}*/*.pdf",
            f"**/{year[-2:]}{school_base}/kokugo*.pdf",
        ]
        
        for pattern in search_patterns:
            matches = list(self.kakomon_dir.glob(pattern))
            # 解答ファイルを除外
            pdf_files = [f for f in matches 
                        if '解答' not in f.name and 'kaito' not in f.name.lower()]
            
            if pdf_files:
                # 最も適切なファイルを選択（ファイル名に年度が含まれるもの優先）
                for pdf in pdf_files:
                    if year in pdf.name:
                        return pdf
                return pdf_files[0]
        
        return None
    
    def clear_screen(self):
        """画面をクリア"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """ヘッダーを表示"""
        print("=" * 60)
        print("     入試問題分析システム v1.0")
        print("     Entrance Exam Analyzer")
        print("=" * 60)
        print()
        
    def select_school(self):
        """学校を選択"""
        print("【学校選択】")
        print(f"過去問フォルダから{len(self.schools)}校を検出しました")
        print("-" * 40)
        for i, school in enumerate(self.schools, 1):
            print(f"{i:2d}. {school}")
        print("-" * 40)
        
        while True:
            try:
                choice = input("\n学校番号を入力してください (1-{}): ".format(len(self.schools)))
                index = int(choice) - 1
                if 0 <= index < len(self.schools):
                    return self.schools[index]
                else:
                    print("❌ 正しい番号を入力してください")
            except ValueError:
                print("❌ 数字を入力してください")
                
    def select_years(self, school_name):
        """年度を選択（複数選択可能）"""
        print("\n【年度選択】")
        print("-" * 40)
        
        # 利用可能な年度を取得
        available_years = []
        if school_name in self.school_years:
            available_years = sorted(self.school_years[school_name], reverse=True)
        
        if not available_years:
            # 利用可能な年度がない場合はデフォルト年度を表示
            print("⚠️  この学校のPDFファイルが見つかりません")
            print("デフォルト年度を表示します")
            available_years = [str(year) for year in range(2025, 2019, -1)]
        
        print(f"{school_name}の利用可能な年度：")
        for i, year in enumerate(available_years, 1):
            print(f"{i:2d}. {year}年")
        
        print("\n複数選択可能です。スペース区切りで番号を入力してください")
        print("例: 1 3 5 (全選択の場合は 'all' と入力)")
        print("-" * 40)
        
        while True:
            choice = input("年度番号を入力: ")
            
            if choice.lower() == 'all':
                return available_years
            
            try:
                indices = [int(x) - 1 for x in choice.split()]
                selected_years = []
                
                for index in indices:
                    if 0 <= index < len(available_years):
                        selected_years.append(available_years[index])
                    else:
                        raise ValueError()
                
                if selected_years:
                    return selected_years
                else:
                    print("❌ 少なくとも1つの年度を選択してください")
                    
            except ValueError:
                print("❌ 正しい番号を入力してください")
                
    # PDFファイル選択機能は削除（自動特定するため）
                
    def execute_workflow(self, school_name, pdf_files_to_process):
        """ワークフローを実行（複数年度対応）"""
        try:
            success_count = 0
            
            for year, pdf_path in pdf_files_to_process:
                print(f"\n━━━ {year}年度の処理を開始 ━━━")
                print(f"PDF: {pdf_path.name}")
                
                # Step 1: BunkoOCRを起動
                print("\n🚀 BunkoOCRを起動しています...")
                self.launch_bunko_with_file(str(pdf_path), year, school_name)
                
                # Step 2: ユーザーにOCR実行を促す
                self.show_ocr_instructions(year, pdf_path.name)
                
                # Step 3: OCR結果を待機・取得
                print("\n⏳ OCR結果を待機中...")
                ocr_text = self.wait_for_ocr_result()
                
                if not ocr_text:
                    print("❌ OCR結果が取得できませんでした")
                    continue  # 次の年度へ
                    
                # Step 4: テキスト分析
                print("\n🔍 テキストを分析中...")
                analysis_result = self.analyze_text(ocr_text, school_name, year)
                
                # Step 5: Excelデータベースに保存
                print("\n💾 Excelデータベースに保存中...")
                self.save_to_database(analysis_result, school_name, year)
                
                print(f"\n✅ {year}年度の分析が完了しました！")
                success_count += 1
            
            # 全体の完了メッセージ
            print("\n" + "=" * 60)
            print(f"🎉 すべての分析が完了しました！")
            print(f"   {school_name} - {success_count}年度分の分析結果を保存")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {str(e)}")
            return False
            
    def launch_bunko_with_file(self, pdf_path, year=None, school_name=None):
        """BunkoOCRでファイルを開く（修正版：キーボードナビゲーション使用）"""
        import pyautogui
        import pyperclip
        
        # 現在の結果フォルダ数を記録
        self.before_count = len(list(self.results_dir.iterdir())) if self.results_dir.exists() else 0
        
        print(f"📱 BunkoOCRでファイルを開きます: {pdf_path}")
        
        # 1. BunkoOCRをアクティブ化
        print("   🚀 BunkoOCRを起動中...")
        subprocess.run(["open", "-a", self.bunko_app])
        time.sleep(3)  # アプリ起動を待つ
        
        # 2. キーボードナビゲーションで「ファイルから選択」を開く
        print("   🎯 「ファイルから選択」を開く...")
        self._navigate_to_file_select()
        
        # 3. ファイルダイアログでPDFを選択
        print("   📂 ファイルを選択中...")
        self._select_pdf_file(pdf_path, year, school_name)
        
        print("   ✅ BunkoOCRでPDFが開かれました！")
        
    def _navigate_to_file_select(self):
        """キーボードナビゲーションで「ファイルから選択」メニューを開く"""
        import pyautogui
        
        # bunkoOCRをアクティブ化
        subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
        time.sleep(1.5)
        
        # Tab → 上5回 → 下2回 → スペースキー
        pyautogui.press('tab')
        time.sleep(0.5)
        
        # 上5回で最上部へ
        for i in range(5):
            pyautogui.press('up')
            time.sleep(0.2)
        
        # 下2回で「ファイルから選択」へ
        pyautogui.press('down')
        time.sleep(0.5)
        pyautogui.press('down')
        time.sleep(0.5)
        
        # 🔥 重要：スペースキーで開く（Enterキーは効かない！）
        pyautogui.press('space')
        time.sleep(2)
        
    def _select_pdf_file(self, pdf_path, year=None, school_name=None):
        """ファイルダイアログでPDFファイルを選択"""
        import pyautogui
        import pyperclip
        from pathlib import Path
        
        pdf_path = Path(pdf_path)
        full_path = str(pdf_path)
        filename = pdf_path.name
        
        # デバッグ情報を出力
        print(f"   📄 ファイル: {filename}")
        if year:
            print(f"   📅 年度: {year}")
        if school_name:
            print(f"   🏫 学校: {school_name}")
        
        # 選択方法を決定
        print("\n   🎯 ファイル選択方法を選択...")
        print("   1. フルパスで直接開く（推奨）")
        print("   2. デスクトップの過去問エイリアスから開く")
        
        # デフォルトはフルパス方式
        method = "1"
        
        if method == "1":
            # フルパス方式
            print("   📝 フルパスで直接開きます...")
            pyperclip.copy(full_path)
            pyautogui.hotkey('cmd', 'shift', 'g')
            time.sleep(1)
            pyautogui.hotkey('cmd', 'v')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(1.5)
            pyautogui.press('return')
            
        else:
            # エイリアス方式
            print("   📁 過去問エイリアスから開きます...")
            
            # デスクトップに移動
            desktop_path = str(Path.home() / "Desktop")
            pyperclip.copy(desktop_path)
            pyautogui.hotkey('cmd', 'shift', 'g')
            time.sleep(1)
            pyautogui.hotkey('cmd', 'v')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(1.5)
            
            # 過去問エイリアスを開く
            pyautogui.typewrite('過去問')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(2)
            
            # 年度フォルダへ
            if year:
                year_search = f"{year}過去問" if len(year) == 4 else f"{year}"
                pyautogui.typewrite(year_search[:4])
                time.sleep(0.5)
                pyautogui.press('return')
                time.sleep(1)
            
            # 学校フォルダへ
            if school_name:
                school_search = school_name.replace('中学校', '').replace('中等部', '')
                if year and len(year) == 4:
                    school_search = f"{year[-2:]}{school_search}"
                pyautogui.typewrite(school_search[:4])
                time.sleep(0.5)
                pyautogui.press('return')
                time.sleep(1)
            
            # ファイルを選択
            if "kokugo" in filename.lower():
                pyautogui.typewrite('kok')
            else:
                pyautogui.typewrite(filename[:3])
            time.sleep(0.5)
            pyautogui.press('return')  # 選択
            time.sleep(0.5)
            pyautogui.press('return')  # 開く
        
        time.sleep(1)
        print("   ✅ ファイルを開きました！")
        
    def show_ocr_instructions(self, year, filename):
        """OCR実行手順を表示"""
        print("\n" + "=" * 60)
        print(f"📝 {year}年度 - {filename}")
        print("=" * 60)
        print("1. BunkoOCRが起動し、PDFが表示されます")
        print("2. 画面下部の「OCR」ボタンをクリックしてください")
        print("3. 処理が完了するまでお待ちください（数分かかる場合があります）")
        print("4. 処理が完了したら、Enterキーを押してください")
        print("\n※ 処理中はBunkoOCRを閉じないでください")
        print("=" * 60)
        
        input("\nOCR処理が完了したらEnterキーを押してください...")
        
    def wait_for_ocr_result(self):
        """OCR結果を待機して取得"""
        # 最大待機時間（60秒）
        max_wait = 60
        check_interval = 2
        
        for i in range(max_wait // check_interval):
            if self.results_dir.exists():
                current_count = len(list(self.results_dir.iterdir()))
                if current_count > self.before_count:
                    # 新しいフォルダを検出
                    latest_folder = max(self.results_dir.iterdir(), 
                                      key=lambda p: p.stat().st_mtime)
                    
                    # テキストファイルを探す
                    text_files = list(latest_folder.glob("text*.txt"))
                    if text_files:
                        # すべてのテキストファイルを結合
                        combined_text = ""
                        for txt_file in sorted(text_files, 
                                             key=lambda f: int(f.stem.replace('text', ''))):
                            combined_text += txt_file.read_text(encoding='utf-8')
                            
                        return combined_text
                        
            # プログレス表示
            print(f"\r⏳ 待機中... ({i * check_interval}/{max_wait}秒)", end='', flush=True)
            time.sleep(check_interval)
            
        return None
        
    def analyze_text(self, text, school_name, year):
        """テキストを分析"""
        analyzer = TextAnalyzer()
        result = analyzer.analyze_exam_structure(text)
        
        # 出典情報を抽出
        extractor = PatternExtractor()
        sources = extractor.extract_sources(text)
        
        # 結果に追加情報を付与
        result['school_name'] = school_name
        result['year'] = year
        result['sources'] = sources
        
        return result
        
    def save_to_database(self, analysis_result, school_name, year):
        """Excelデータベースに保存"""
        db_filename = "entrance_exam_database.xlsx"
        
        # 既存ファイルがあるかチェック
        try:
            existing_sheets = pd.ExcelFile(db_filename, engine='openpyxl').sheet_names
        except FileNotFoundError:
            existing_sheets = []
            
        # データを準備
        data_row = self.prepare_data_row(analysis_result, school_name, year)
        
        # データフレーム作成
        new_df = pd.DataFrame([data_row])
        
        # Excelファイルに書き込み
        with pd.ExcelWriter(db_filename, engine='openpyxl', 
                           mode='a' if existing_sheets else 'w', 
                           if_sheet_exists='replace') as writer:
            if school_name in existing_sheets:
                # 既存シートに追加
                existing_df = pd.read_excel(db_filename, sheet_name=school_name)
                existing_df['年度'] = pd.to_numeric(existing_df['年度'], errors='coerce')
                
                # 同じ年度のデータがあれば更新
                year_int = int(year)
                if year_int in existing_df['年度'].values:
                    existing_df = existing_df[existing_df['年度'] != year_int]
                    
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df = combined_df.sort_values('年度')
            else:
                combined_df = new_df
                
            combined_df.to_excel(writer, sheet_name=school_name, index=False)
            
    def prepare_data_row(self, analysis_result, school_name, year):
        """データベース用のデータ行を準備"""
        data_row = {
            '年度': int(year),
            '総設問数': len(analysis_result.get('questions', [])),
            '総文字数': analysis_result.get('total_characters', 0),
            '大問数': len(analysis_result.get('sections', []))
        }
        
        # 各大問のデータ
        for i, section in enumerate(analysis_result.get('sections', []), 1):
            # ジャンルとテーマを判定
            genre, theme = self.determine_genre_and_theme(section.get('text', ''))
            
            # 出典情報を取得
            source = next((s for s in analysis_result.get('sources', []) 
                          if s.get('section') == i), {})
            
            data_row[f'大問{i}_ジャンル'] = genre
            data_row[f'大問{i}_テーマ'] = theme
            data_row[f'大問{i}_著者'] = source.get('author', '不明')
            data_row[f'大問{i}_作品'] = source.get('title', '不明')
            data_row[f'大問{i}_設問数'] = section.get('question_count', 0)
            data_row[f'大問{i}_文字数'] = len(section.get('text', ''))
            
        # 設問タイプ別集計
        for q_type, count in analysis_result.get('question_types', {}).items():
            data_row[f'{q_type}_問題数'] = count
            
        return data_row
        
    def determine_genre_and_theme(self, text):
        """文章のジャンルとテーマを判定"""
        # 簡易的な判定ロジック
        text_sample = text[:1000] if len(text) > 1000 else text
        
        # ジャンル判定
        if any(word in text_sample for word in ['小説', '物語', '「', '」', 'と言った']):
            genre = '小説・物語'
        elif any(word in text_sample for word in ['評論', '論説', 'について', 'という']):
            genre = '評論・論説'
        elif any(word in text_sample for word in ['随筆', 'エッセイ', '私は']):
            genre = '随筆・エッセイ'
        else:
            genre = '評論・論説'
            
        # テーマ判定
        if any(word in text_sample for word in ['友情', '家族', '成長']):
            theme = '人間関係・成長'
        elif any(word in text_sample for word in ['自然', '環境', '生物']):
            theme = '自然・環境'
        elif any(word in text_sample for word in ['社会', '文化', '歴史']):
            theme = '社会・文化'
        elif any(word in text_sample for word in ['科学', '技術', 'AI']):
            theme = '科学・技術'
        else:
            theme = '一般'
            
        return genre, theme
        
    def run(self):
        """アプリケーションを実行"""
        self.clear_screen()
        self.print_header()
        
        # 学校選択
        school_name = self.select_school()
        print(f"\n✅ 選択した学校: {school_name}")
        
        # 年度選択
        years = self.select_years(school_name)
        years_str = '、'.join(years)
        print(f"\n✅ 選択した年度: {years_str}年")
        
        # PDFファイルの自動特定
        print("\n🔍 PDFファイルを検索中...")
        pdf_files_to_process = []
        
        for year in years:
            pdf_file = self.find_pdf_for_school_year(school_name, year)
            if pdf_file:
                pdf_files_to_process.append((year, pdf_file))
                print(f"  ✅ {year}年: {pdf_file.name}")
            else:
                print(f"  ⚠️  {year}年: PDFファイルが見つかりません")
        
        if not pdf_files_to_process:
            print("\n❌ PDFファイルが1つも見つかりませんでした")
            return
        
        # 確認
        print("\n" + "=" * 60)
        print("【分析内容の確認】")
        print(f"学校: {school_name}")
        print(f"年度: {years_str}年")
        print(f"PDFファイル数: {len(pdf_files_to_process)}件")
        print("=" * 60)
        
        confirm = input("\nこの内容で分析を開始しますか？ (y/n): ")
        if confirm.lower() != 'y':
            print("\n分析をキャンセルしました")
            return
            
        # ワークフロー実行
        self.execute_workflow(school_name, pdf_files_to_process)
        
        print("\n処理が完了しました。Enterキーを押して終了してください...")
        input()


def main():
    """メイン関数"""
    app = EntranceExamAnalyzerCLI()
    app.run()


if __name__ == "__main__":
    main()