#!/usr/bin/env python3
"""
入試問題テキスト分析アプリケーション（CLI版）
テキストファイルを選択 → 学校名・年度を抽出・確認 → 分析 → Excel出力
"""

import os
import sys
import re
from pathlib import Path
import pandas as pd
from datetime import datetime

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter


class TextAnalyzerCLI:
    """テキスト分析アプリケーション（CLI版）"""
    
    def __init__(self):
        # BunkoOCR結果フォルダ
        self.bunko_results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.text_files = []
        self.current_text = ""
        
    def clear_screen(self):
        """画面をクリア"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """ヘッダーを表示"""
        print("=" * 60)
        print("     入試問題テキスト分析システム")
        print("     Text Analysis System")
        print("=" * 60)
        print()
        
    def select_text_files(self):
        """テキストファイルを選択"""
        print("【テキストファイル選択】")
        print("1. 手動でファイルパスを入力")
        print("2. BunkoOCR結果から選択")
        print("3. 過去問フォルダから検索")
        print("-" * 40)
        
        choice = input("選択方法 (1-3): ")
        
        if choice == "1":
            self.manual_file_selection()
        elif choice == "2":
            self.select_from_bunko()
        elif choice == "3":
            self.search_from_kakomon()
        else:
            print("❌ 無効な選択です")
            return False
            
        return len(self.text_files) > 0
        
    def manual_file_selection(self):
        """手動でファイルパスを入力"""
        print("\nテキストファイルのパスを入力してください")
        print("複数ファイルの場合は改行で区切って入力（空行で終了）")
        
        files = []
        while True:
            path = input("ファイルパス: ").strip()
            if not path:
                break
                
            file_path = Path(path)
            if file_path.exists() and file_path.suffix == '.txt':
                files.append(file_path)
                print(f"✅ {file_path.name}")
            else:
                print(f"❌ ファイルが見つかりません: {path}")
                
        self.text_files = files
        
    def select_from_bunko(self):
        """BunkoOCR結果から選択"""
        if not self.bunko_results_dir.exists():
            print("❌ BunkoOCR結果フォルダが見つかりません")
            return
            
        # 最新のフォルダを表示
        folders = sorted(self.bunko_results_dir.iterdir(), 
                        key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not folders:
            print("❌ BunkoOCR結果が見つかりません")
            return
            
        print("\n【BunkoOCR結果一覧】")
        print("-" * 60)
        
        folder_list = []
        for i, folder in enumerate(folders[:20], 1):  # 最新20件
            timestamp = datetime.fromtimestamp(folder.stat().st_mtime)
            text_files = list(folder.glob("text*.txt"))
            if text_files:
                print(f"{i:2d}. {timestamp.strftime('%Y-%m-%d %H:%M')} - {folder.name}")
                print(f"    ({len(text_files)}個のテキストファイル)")
                folder_list.append(folder)
                
        print("-" * 60)
        
        try:
            choice = int(input("\n番号を選択 (1-{}): ".format(len(folder_list))))
            if 1 <= choice <= len(folder_list):
                selected_folder = folder_list[choice - 1]
                self.text_files = sorted(selected_folder.glob("text*.txt"))
                print(f"\n✅ 選択: {selected_folder.name}")
            else:
                print("❌ 無効な番号です")
        except ValueError:
            print("❌ 数字を入力してください")
            
    def search_from_kakomon(self):
        """過去問フォルダから検索"""
        kakomon_dir = Path.home() / "Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
        
        if not kakomon_dir.exists():
            print("❌ 過去問フォルダが見つかりません")
            return
            
        print("\n検索キーワードを入力（例：女子学院 2023）")
        keyword = input("キーワード: ")
        
        if not keyword:
            return
            
        print("\n検索中...")
        found_files = []
        
        # テキストファイルを検索
        for txt_file in kakomon_dir.glob("**/*.txt"):
            if keyword.lower() in str(txt_file).lower():
                found_files.append(txt_file)
                
        if found_files:
            print(f"\n{len(found_files)}個のファイルが見つかりました")
            for i, file in enumerate(found_files[:10], 1):  # 最大10件表示
                print(f"{i:2d}. {file.relative_to(kakomon_dir)}")
                
            try:
                choice = int(input("\n番号を選択 (1-{}): ".format(min(10, len(found_files)))))
                if 1 <= choice <= min(10, len(found_files)):
                    self.text_files = [found_files[choice - 1]]
                    print(f"\n✅ 選択: {self.text_files[0].name}")
            except ValueError:
                print("❌ 数字を入力してください")
        else:
            print("❌ ファイルが見つかりませんでした")
            
    def extract_info(self):
        """学校名と年度を抽出"""
        if not self.text_files:
            return None, None
            
        # 最初のファイルを読み込む
        try:
            self.current_text = self.text_files[0].read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {str(e)}")
            return None, None
            
        file_path = str(self.text_files[0])
        
        # 学校名の抽出
        school_patterns = [
            r'(開成|麻布|武蔵|桜蔭|女子学院|雙葉|渋谷教育学園渋谷|渋渋|慶應義塾|早稲田実業)',
            r'(\w+中学校)',
            r'(\w+中等部)',
        ]
        
        school = ""
        for pattern in school_patterns:
            match = re.search(pattern, file_path)
            if match:
                school = match.group(1)
                if '中学校' not in school and '中等部' not in school:
                    school += '中学校'
                break
                
        # テキストからも学校名を探す
        if not school:
            for pattern in school_patterns:
                match = re.search(pattern, self.current_text[:500])
                if match:
                    school = match.group(1)
                    if '中学校' not in school and '中等部' not in school:
                        school += '中学校'
                    break
                    
        # 年度の抽出
        year_patterns = [
            r'(20\d{2})年',
            r'(20\d{2})',
            r'(\d{2})年度',
            r'令和(\d+)年',
            r'平成(\d+)年',
        ]
        
        year = ""
        for pattern in year_patterns:
            match = re.search(pattern, file_path)
            if match:
                if '令和' in pattern:
                    year = str(2018 + int(match.group(1)))
                elif '平成' in pattern:
                    year = str(1988 + int(match.group(1)))
                else:
                    year = match.group(1)
                    if len(year) == 2:
                        year = '20' + year
                break
                
        # テキストからも年度を探す
        if not year:
            for pattern in year_patterns:
                match = re.search(pattern, self.current_text[:500])
                if match:
                    if '令和' in pattern:
                        year = str(2018 + int(match.group(1)))
                    elif '平成' in pattern:
                        year = str(1988 + int(match.group(1)))
                    else:
                        year = match.group(1)
                        if len(year) == 2:
                            year = '20' + year
                    break
                    
        return school, year
        
    def confirm_info(self, school, year):
        """抽出した情報を確認"""
        print("\n【抽出された情報】")
        print("-" * 40)
        print(f"学校名: {school if school else '不明'}")
        print(f"年度: {year if year else '不明'}年")
        print("-" * 40)
        
        # 修正が必要か確認
        print("\n情報は正しいですか？")
        print("1. 正しい")
        print("2. 修正する")
        
        choice = input("選択 (1-2): ")
        
        if choice == "2":
            # 手動入力
            print("\n正しい情報を入力してください")
            school = input(f"学校名 [{school}]: ").strip() or school
            year = input(f"年度 [{year}]: ").strip() or year
            
        return school, year
        
    def execute_analysis(self, school_name, year):
        """分析を実行"""
        try:
            print("\n📊 分析を開始します...")
            
            # テキストを結合
            if len(self.text_files) > 1:
                print(f"   {len(self.text_files)}個のファイルを結合中...")
                combined_text = ""
                for txt_file in sorted(self.text_files):
                    combined_text += txt_file.read_text(encoding='utf-8')
                    combined_text += "\n\n"
            else:
                combined_text = self.text_files[0].read_text(encoding='utf-8')
                
            # テキスト分析
            print("   テキストを分析中...")
            analyzer = TextAnalyzer()
            result = analyzer.analyze_exam_structure(combined_text)
            
            # 出典情報を抽出
            print("   出典情報を抽出中...")
            extractor = PatternExtractor()
            sources = extractor.extract_sources(combined_text)
            
            # 結果に情報を追加
            result['school_name'] = school_name
            result['year'] = year
            result['sources'] = sources
            
            # 分析結果を表示
            print("\n【分析結果】")
            print("-" * 60)
            print(f"総文字数: {result.get('total_characters', 0):,}文字")
            print(f"大問数: {len(result.get('sections', []))}問")
            print(f"総設問数: {len(result.get('questions', []))}問")
            print("-" * 60)
            
            # 大問ごとの情報
            for i, section in enumerate(result.get('sections', []), 1):
                print(f"\n大問{i}:")
                print(f"  文字数: {len(section.get('text', '')):,}文字")
                print(f"  設問数: {section.get('question_count', 0)}問")
                
            # Excelに保存
            print("\n💾 Excelデータベースに保存中...")
            self.save_to_database(result, school_name, year)
            
            print("\n✅ 分析が完了しました！")
            print(f"   結果は entrance_exam_database.xlsx に保存されました")
            
            return True
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {str(e)}")
            return False
            
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
        
        # ファイル選択
        if not self.select_text_files():
            print("\nファイルが選択されませんでした")
            return
            
        print(f"\n✅ {len(self.text_files)}個のファイルが選択されました")
        for file in self.text_files[:5]:  # 最初の5個を表示
            print(f"   - {file.name}")
        if len(self.text_files) > 5:
            print(f"   ... 他{len(self.text_files) - 5}個")
            
        # 情報抽出
        print("\n📋 ファイルから情報を抽出中...")
        school, year = self.extract_info()
        
        # 情報確認
        school, year = self.confirm_info(school, year)
        
        if not school or not year:
            print("\n❌ 学校名または年度が不明です")
            return
            
        # 最終確認
        print("\n" + "=" * 60)
        print("【分析内容の確認】")
        print(f"学校: {school}")
        print(f"年度: {year}年")
        print(f"ファイル数: {len(self.text_files)}個")
        print("=" * 60)
        
        confirm = input("\nこの内容で分析を開始しますか？ (y/n): ")
        if confirm.lower() != 'y':
            print("\n分析をキャンセルしました")
            return
            
        # 分析実行
        self.execute_analysis(school, year)
        
        print("\n処理が完了しました。Enterキーを押して終了してください...")
        input()


def main():
    """メイン関数"""
    app = TextAnalyzerCLI()
    app.run()


if __name__ == "__main__":
    main()