#!/usr/bin/env python3
"""
入試問題テキスト分析アプリケーション
テキストファイルを選択 → 学校名・年度を抽出・確認 → 分析 → Excel出力
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import re
import os
import sys
from datetime import datetime

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter


class TextAnalyzerApp:
    """テキスト分析アプリケーション"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("入試問題テキスト分析システム")
        self.root.geometry("700x600")
        
        # 分析対象のテキストファイル
        self.text_files = []
        self.current_text = ""
        
        # BunkoOCR結果フォルダ
        self.bunko_results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        
        self.setup_ui()
        
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="入試問題テキスト分析", 
                               font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # ファイル選択セクション
        ttk.Label(main_frame, text="1. テキストファイルを選択", 
                 font=('Helvetica', 14, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(20, 10))
        
        # ファイル選択ボタン
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(file_frame, text="ファイルを選択", 
                  command=self.select_text_files).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="BunkoOCR結果から選択", 
                  command=self.select_from_bunko).pack(side=tk.LEFT, padx=5)
        
        # 選択されたファイルリスト
        self.file_listbox = tk.Listbox(main_frame, height=5, width=60)
        self.file_listbox.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical")
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 情報抽出セクション
        ttk.Label(main_frame, text="2. 抽出された情報を確認", 
                 font=('Helvetica', 14, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(20, 10))
        
        # 抽出情報フレーム
        info_frame = ttk.LabelFrame(main_frame, text="抽出情報", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 学校名
        ttk.Label(info_frame, text="学校名:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.school_var = tk.StringVar()
        self.school_entry = ttk.Entry(info_frame, textvariable=self.school_var, width=30)
        self.school_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 年度
        ttk.Label(info_frame, text="年度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_var = tk.StringVar()
        self.year_entry = ttk.Entry(info_frame, textvariable=self.year_var, width=30)
        self.year_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 抽出ボタン
        ttk.Button(info_frame, text="情報を自動抽出", 
                  command=self.extract_info).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 分析開始ボタン
        ttk.Label(main_frame, text="3. 分析を開始", 
                 font=('Helvetica', 14, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=(20, 10))
        
        analyze_btn = ttk.Button(main_frame, text="分析開始", 
                                command=self.start_analysis,
                                style='Accent.TButton')
        analyze_btn.grid(row=7, column=0, columnspan=3, pady=20)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # ステータスラベル
        self.status_var = tk.StringVar(value="テキストファイルを選択してください")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('Helvetica', 10))
        status_label.grid(row=9, column=0, columnspan=3, pady=10)
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 14, 'bold'))
        
    def select_text_files(self):
        """テキストファイルを選択"""
        files = filedialog.askopenfilenames(
            title="テキストファイルを選択",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if files:
            self.text_files = [Path(f) for f in files]
            self.update_file_list()
            self.status_var.set(f"{len(files)}個のファイルが選択されました")
            
    def select_from_bunko(self):
        """BunkoOCR結果フォルダから選択"""
        if not self.bunko_results_dir.exists():
            messagebox.showerror("エラー", "BunkoOCR結果フォルダが見つかりません")
            return
            
        # 最新のフォルダを表示
        folders = sorted(self.bunko_results_dir.iterdir(), 
                        key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not folders:
            messagebox.showinfo("情報", "BunkoOCR結果が見つかりません")
            return
            
        # 選択ダイアログ
        dialog = tk.Toplevel(self.root)
        dialog.title("BunkoOCR結果を選択")
        dialog.geometry("600x400")
        
        # リストボックス
        listbox = tk.Listbox(dialog, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # フォルダ情報を表示
        folder_map = {}
        for i, folder in enumerate(folders[:20]):  # 最新20件
            timestamp = datetime.fromtimestamp(folder.stat().st_mtime)
            text_files = list(folder.glob("text*.txt"))
            if text_files:
                display_text = f"{timestamp.strftime('%Y-%m-%d %H:%M')} - {folder.name} ({len(text_files)}ファイル)"
                listbox.insert(tk.END, display_text)
                folder_map[i] = folder
                
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_folder = folder_map[selection[0]]
                self.text_files = sorted(selected_folder.glob("text*.txt"))
                self.update_file_list()
                self.status_var.set(f"BunkoOCR結果を選択しました: {selected_folder.name}")
                dialog.destroy()
                
        ttk.Button(dialog, text="選択", command=on_select).pack(pady=10)
        
    def update_file_list(self):
        """ファイルリストを更新"""
        self.file_listbox.delete(0, tk.END)
        for file in self.text_files:
            self.file_listbox.insert(tk.END, file.name)
            
    def extract_info(self):
        """選択されたファイルから学校名と年度を抽出"""
        if not self.text_files:
            messagebox.showwarning("警告", "ファイルが選択されていません")
            return
            
        # 最初のファイルを読み込む
        try:
            self.current_text = self.text_files[0].read_text(encoding='utf-8')
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル読み込みエラー: {str(e)}")
            return
            
        # ファイルパスから情報を抽出
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
                match = re.search(pattern, self.current_text[:500])  # 最初の500文字
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
                    
        # 抽出結果を表示
        self.school_var.set(school)
        self.year_var.set(year)
        
        if school and year:
            self.status_var.set(f"情報を抽出しました: {school} {year}年")
        else:
            self.status_var.set("情報の自動抽出に失敗しました。手動で入力してください")
            
    def start_analysis(self):
        """分析を開始"""
        # 入力チェック
        if not self.text_files:
            messagebox.showerror("エラー", "テキストファイルを選択してください")
            return
            
        school_name = self.school_var.get()
        year = self.year_var.get()
        
        if not school_name or not year:
            messagebox.showerror("エラー", "学校名と年度を入力してください")
            return
            
        # 確認ダイアログ
        file_count = len(self.text_files)
        result = messagebox.askyesno(
            "確認",
            f"以下の内容で分析を開始します:\n\n"
            f"学校: {school_name}\n"
            f"年度: {year}年\n"
            f"ファイル数: {file_count}個\n\n"
            f"よろしいですか？"
        )
        
        if not result:
            return
            
        # プログレスバー開始
        self.progress.start()
        self.status_var.set("分析中...")
        
        # 分析を実行
        self.root.after(100, lambda: self.execute_analysis(school_name, year))
        
    def execute_analysis(self, school_name, year):
        """分析を実行"""
        try:
            # テキストを結合
            if len(self.text_files) > 1:
                # 複数ファイルの場合は結合
                combined_text = ""
                for txt_file in sorted(self.text_files):
                    combined_text += txt_file.read_text(encoding='utf-8')
                    combined_text += "\n\n"  # ファイル間の区切り
            else:
                combined_text = self.text_files[0].read_text(encoding='utf-8')
                
            # テキスト分析
            self.status_var.set("テキストを分析中...")
            analyzer = TextAnalyzer()
            result = analyzer.analyze_exam_structure(combined_text)
            
            # 出典情報を抽出
            extractor = PatternExtractor()
            sources = extractor.extract_sources(combined_text)
            
            # 結果に情報を追加
            result['school_name'] = school_name
            result['year'] = year
            result['sources'] = sources
            result['raw_text'] = combined_text
            
            # Excelに保存
            self.status_var.set("Excelデータベースに保存中...")
            self.save_to_database(result, school_name, year)
            
            # 完了
            self.progress.stop()
            self.status_var.set("分析が完了しました！")
            
            # 結果の概要を表示
            summary = f"""分析が完了しました！

学校: {school_name}
年度: {year}年
総文字数: {result.get('total_characters', 0):,}文字
大問数: {len(result.get('sections', []))}問
総設問数: {len(result.get('questions', []))}問

結果はExcelファイルに保存されました。"""
            
            messagebox.showinfo("完了", summary)
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("エラー", f"分析中にエラーが発生しました:\n{str(e)}")
            self.status_var.set("エラーが発生しました")
            
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
            
            # 生テキストも別シートに保存（オプション）
            if 'raw_text' in analysis_result:
                raw_sheet_name = f"{school_name}_{year}_raw"
                raw_df = pd.DataFrame([{
                    '年度': year,
                    'テキスト': analysis_result['raw_text'][:30000]  # 最大30000文字
                }])
                raw_df.to_excel(writer, sheet_name=raw_sheet_name[:31], index=False)  # シート名は最大31文字
                
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
    app = TextAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()