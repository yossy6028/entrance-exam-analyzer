#!/usr/bin/env python3
"""
入試問題分析アプリケーション
統合ワークフロー：学校・年度選択 → BunkoOCR → 分析 → Excel記録
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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


class EntranceExamAnalyzerApp:
    """入試問題分析アプリケーション"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("入試問題分析システム")
        self.root.geometry("600x500")
        
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
        
        # 選択された年度を保存するリスト
        self.selected_years = []
        
        self.setup_ui()
    
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
                "武蔵中学校",
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
        
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="入試問題分析システム", 
                               font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 学校選択
        ttk.Label(main_frame, text="学校名:", font=('Helvetica', 12)).grid(
            row=1, column=0, sticky=tk.W, pady=10)
        
        self.school_var = tk.StringVar()
        school_combo = ttk.Combobox(main_frame, textvariable=self.school_var, 
                                   values=self.schools, width=30, font=('Helvetica', 11))
        school_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)
        school_combo.current(0)
        
        # 学校選択時のコールバック
        school_combo.bind('<<ComboboxSelected>>', self.on_school_selected)
        
        # 年度選択フレーム
        ttk.Label(main_frame, text="年度:", font=('Helvetica', 12)).grid(
            row=2, column=0, sticky=(tk.W, tk.N), pady=10)
        
        # 年度リストボックスのフレーム
        year_frame = ttk.Frame(main_frame)
        year_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        
        # スクロールバー付きリストボックス
        scrollbar = ttk.Scrollbar(year_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.year_listbox = tk.Listbox(year_frame, selectmode=tk.MULTIPLE, 
                                      height=5, width=20, font=('Helvetica', 11),
                                      yscrollcommand=scrollbar.set)
        self.year_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.year_listbox.yview)
        
        # 年度選択の説明
        year_label = ttk.Label(main_frame, text="(Ctrl/Cmd+クリックで複数選択可能)", 
                              font=('Helvetica', 9))
        year_label.grid(row=3, column=1, sticky=tk.W, pady=0)
        
        # PDFファイル選択部分は削除（自動特定するため）
        
        # 実行ボタン
        execute_btn = ttk.Button(main_frame, text="分析開始", 
                                command=self.start_analysis,
                                style='Accent.TButton')
        execute_btn.grid(row=4, column=0, columnspan=2, pady=30)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # ステータスラベル
        self.status_var = tk.StringVar(value="学校を選択してください")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('Helvetica', 10))
        status_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # 初期状態で最初の学校の年度を表示
        if self.schools:
            self.update_year_list(self.schools[0])
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 14, 'bold'))
    
    def on_school_selected(self, event):
        """学校が選択されたときのコールバック"""
        selected_school = self.school_var.get()
        self.update_year_list(selected_school)
        self.status_var.set("年度を選択してください")
    
    def update_year_list(self, school_name):
        """選択された学校の利用可能な年度を更新"""
        self.year_listbox.delete(0, tk.END)
        
        if school_name in self.school_years:
            years = sorted(self.school_years[school_name], reverse=True)
            for year in years:
                self.year_listbox.insert(tk.END, f"{year}年")
            
            if years:
                # 最新年度を自動選択
                self.year_listbox.selection_set(0)
        else:
            # 利用可能な年度がない場合はデフォルト年度を表示
            for year in range(2025, 2019, -1):
                self.year_listbox.insert(tk.END, f"{year}年")
        
    # PDFファイル選択機能は削除（自動特定するため）
            
    def start_analysis(self):
        """分析処理を開始"""
        # 年度選択チェック
        selected_indices = self.year_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("エラー", "年度を選択してください")
            return
        
        # 選択された年度を取得
        self.selected_years = []
        for index in selected_indices:
            year_text = self.year_listbox.get(index)
            year = year_text.replace('年', '')
            self.selected_years.append(year)
        
        # PDFファイルの自動特定
        pdf_files_to_process = []
        school_name = self.school_var.get()
        
        for year in self.selected_years:
            pdf_file = self.find_pdf_for_school_year(school_name, year)
            if pdf_file:
                pdf_files_to_process.append((year, pdf_file))
            
        if not pdf_files_to_process:
            messagebox.showerror("エラー", f"{school_name}のPDFファイルが見つかりませんでした")
            return
            
        # プログレスバー開始
        self.progress.start()
        
        # PDFファイルリストを保存
        self.pdf_files_to_process = pdf_files_to_process
        
        # 別スレッドで処理を実行
        self.root.after(100, self.execute_workflow)
        
    def execute_workflow(self):
        """ワークフローを実行（複数年度対応）"""
        try:
            school_name = self.school_var.get()
            success_count = 0
            
            # 複数年度を処理
            for year, pdf_path in self.pdf_files_to_process:
                self.status_var.set(f"{year}年度を処理中...")
                self.root.update()
                
                # Step 1: BunkoOCRを起動
                self.status_var.set(f"{year}年度: BunkoOCRを起動しています...")
                self.launch_bunko_with_file(str(pdf_path))
                
                # Step 2: ユーザーにOCR実行を促す
                self.show_ocr_instructions(year, pdf_path.name)
                
                # Step 3: OCR結果を待機・取得
                self.status_var.set(f"{year}年度: OCR結果を待機中...")
                ocr_text = self.wait_for_ocr_result()
                
                if not ocr_text:
                    messagebox.showerror("エラー", f"{year}年度のOCR結果が取得できませんでした")
                    continue  # 次の年度へ
                    
                # Step 4: テキスト分析
                self.status_var.set(f"{year}年度: テキストを分析中...")
                analysis_result = self.analyze_text(ocr_text, school_name, year)
                
                # Step 5: Excelデータベースに保存
                self.status_var.set(f"{year}年度: Excelデータベースに保存中...")
                self.save_to_database(analysis_result, school_name, year)
                
                success_count += 1
                self.status_var.set(f"{year}年度の分析が完了しました！")
                
            # 完了メッセージ
            if success_count > 0:
                self.status_var.set("すべての分析が完了しました！")
                messagebox.showinfo("完了", f"{school_name} {success_count}件の分析が完了しました")
            else:
                self.status_var.set("分析を完了できませんでした")
                messagebox.showerror("エラー", "分析を完了できませんでした")
            
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")
        finally:
            self.progress.stop()
            
    def launch_bunko_with_file(self, pdf_path):
        """BunkoOCRでファイルを開く（修正版：キーボードナビゲーション使用）"""
        import pyautogui
        import pyperclip
        
        # 現在の結果フォルダ数を記録
        self.before_count = len(list(self.results_dir.iterdir())) if self.results_dir.exists() else 0
        
        self.status_var.set("BunkoOCRでファイルを開いています...")
        
        # 1. BunkoOCRをアクティブ化
        subprocess.run(["open", "-a", self.bunko_app])
        time.sleep(3)  # アプリ起動を待つ
        
        # 2. キーボードナビゲーションで「ファイルから選択」を開く
        self.status_var.set("「ファイルから選択」を開いています...")
        self._navigate_to_file_select()
        
        # 3. ファイルダイアログでPDFを選択
        self.status_var.set("PDFファイルを選択中...")
        self._select_pdf_file(pdf_path)
        
        self.status_var.set("BunkoOCRでPDFが開かれました！")
    
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
        
    def _select_pdf_file(self, pdf_path):
        """ファイルダイアログでPDFファイルを選択"""
        import pyautogui
        import pyperclip
        from pathlib import Path
        
        pdf_path = Path(pdf_path)
        folder_path = str(pdf_path.parent)
        filename = pdf_path.name
        
        # 1. フォルダに移動
        pyperclip.copy(folder_path)
        pyautogui.hotkey('cmd', 'shift', 'g')
        time.sleep(0.5)
        pyautogui.hotkey('cmd', 'v')
        time.sleep(0.5)
        pyautogui.press('return')
        time.sleep(2)
        
        # 2. 右上の検索ウィンドウでファイル名を検索
        # Tabキーを3回押して検索ウィンドウに移動
        for _ in range(3):
            pyautogui.press('tab')
            time.sleep(0.2)
        
        # ファイル名から検索キーワードを決定
        search_term = ""
        if "kokugo-mondai" in filename:
            search_term = "kokugo-mondai"
        elif "国語" in filename:
            search_term = "国語"
        elif filename.startswith("23"):
            search_term = "23"
        elif filename.startswith("24"):
            search_term = "24"
        elif filename.startswith("25"):
            search_term = "25"
        else:
            # ファイル名の最初の部分を使用
            search_term = filename.split('.')[0][:6]
        
        # 検索キーワードを入力
        pyautogui.typewrite(search_term)
        time.sleep(1.5)
        
        # 最初の検索結果を選択（下矢印キーで移動）
        pyautogui.press('down')
        time.sleep(0.5)
        
        # 3. ファイルを選択して開く
        pyautogui.press('return')  # ファイル選択
        time.sleep(0.5)
        pyautogui.press('return')  # 開く
        time.sleep(1)
        
    def show_ocr_instructions(self, year, filename):
        """OCR実行手順を表示"""
        instructions = f"""{year}年度 - {filename}

BunkoOCRでの操作手順：

1. BunkoOCRが起動し、PDFが表示されます
2. 画面下部の「OCR」ボタンをクリックしてください
3. 処理が完了するまでお待ちください（数分かかる場合があります）
4. 処理が完了したら、このダイアログの「OK」をクリックしてください

※ 処理中はBunkoOCRを閉じないでください"""
        
        messagebox.showinfo("OCR実行", instructions)
        
    def wait_for_ocr_result(self):
        """OCR結果を待機して取得"""
        # 最大待機時間（60秒）
        max_wait = 60
        check_interval = 2
        
        for _ in range(max_wait // check_interval):
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
        self.root.mainloop()


def main():
    """メイン関数"""
    app = EntranceExamAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()