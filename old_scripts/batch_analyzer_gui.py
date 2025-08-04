#!/usr/bin/env python3
"""
入試問題テキスト分析 バッチ処理GUI版
複数の学校・年度のテキストファイルを一括で処理するGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import json
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from batch_analyzer import BatchAnalyzer


class BatchAnalyzerGUI:
    """バッチ処理GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("入試問題分析 バッチ処理")
        self.root.geometry("800x600")
        
        # 処理中フラグ
        self.processing = False
        self.analyzer = None
        
        # 設定を読み込み
        self.load_config()
        
        self.setup_ui()
        
    def load_config(self):
        """設定ファイルを読み込み"""
        try:
            with open('batch_config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'batch_processing': {
                    'parallel_mode': True,
                    'max_workers': 4
                }
            }
            
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="入試問題分析 バッチ処理", 
                               font=('Helvetica', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # 処理対象選択セクション
        ttk.Label(main_frame, text="処理対象の選択", 
                 font=('Helvetica', 14, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(20, 10))
        
        # ディレクトリ選択フレーム
        dir_frame = ttk.LabelFrame(main_frame, text="ディレクトリ", padding="10")
        dir_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # ラジオボタンで選択
        self.dir_var = tk.StringVar(value="bunko")
        
        ttk.Radiobutton(dir_frame, text="BunkoOCR結果フォルダ", 
                       variable=self.dir_var, value="bunko").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(dir_frame, text="過去問フォルダ", 
                       variable=self.dir_var, value="kakomon").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(dir_frame, text="カスタムディレクトリ", 
                       variable=self.dir_var, value="custom").grid(row=2, column=0, sticky=tk.W, padx=5)
        
        # カスタムディレクトリ入力
        self.custom_dir_var = tk.StringVar()
        self.custom_entry = ttk.Entry(dir_frame, textvariable=self.custom_dir_var, width=40)
        self.custom_entry.grid(row=2, column=1, padx=5)
        
        ttk.Button(dir_frame, text="参照...", 
                  command=self.browse_directory).grid(row=2, column=2, padx=5)
        
        # 処理オプションセクション
        ttk.Label(main_frame, text="処理オプション", 
                 font=('Helvetica', 14, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(20, 10))
        
        options_frame = ttk.LabelFrame(main_frame, text="オプション", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 並列処理
        self.parallel_var = tk.BooleanVar(value=self.config['batch_processing']['parallel_mode'])
        ttk.Checkbutton(options_frame, text="並列処理を使用", 
                       variable=self.parallel_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # ワーカー数
        ttk.Label(options_frame, text="ワーカー数:").grid(row=0, column=1, padx=5)
        self.workers_var = tk.IntVar(value=self.config['batch_processing']['max_workers'])
        workers_spin = ttk.Spinbox(options_frame, from_=1, to=8, width=10,
                                  textvariable=self.workers_var)
        workers_spin.grid(row=0, column=2, padx=5)
        
        # 既存データの処理
        self.skip_existing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="既存データをスキップ", 
                       variable=self.skip_existing_var).grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # バックアップ作成
        self.create_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="バックアップを作成", 
                       variable=self.create_backup_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 実行ボタン
        self.start_button = ttk.Button(main_frame, text="バッチ処理を開始", 
                                      command=self.start_batch_processing,
                                      style='Accent.TButton')
        self.start_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # プログレスセクション
        progress_frame = ttk.LabelFrame(main_frame, text="進捗状況", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # プログレスバー
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # ステータス表示
        self.status_var = tk.StringVar(value="待機中...")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        # 詳細ログ
        self.log_text = tk.Text(progress_frame, height=10, width=70)
        self.log_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        
        # スクロールバー
        log_scroll = ttk.Scrollbar(progress_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        # 結果ボタン（初期は無効）
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.view_db_button = ttk.Button(button_frame, text="データベースを開く", 
                                        command=self.open_database, state='disabled')
        self.view_db_button.pack(side=tk.LEFT, padx=5)
        
        self.view_report_button = ttk.Button(button_frame, text="レポートを表示", 
                                           command=self.open_report, state='disabled')
        self.view_report_button.pack(side=tk.LEFT, padx=5)
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'))
        
    def browse_directory(self):
        """ディレクトリを選択"""
        directory = filedialog.askdirectory(title="処理対象ディレクトリを選択")
        if directory:
            self.custom_dir_var.set(directory)
            self.dir_var.set("custom")
            
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_batch_processing(self):
        """バッチ処理を開始"""
        if self.processing:
            messagebox.showwarning("警告", "処理が実行中です")
            return
            
        # ディレクトリを決定
        if self.dir_var.get() == "bunko":
            target_dir = None  # デフォルト
        elif self.dir_var.get() == "kakomon":
            target_dir = Path.home() / "Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
        else:
            if not self.custom_dir_var.get():
                messagebox.showerror("エラー", "カスタムディレクトリを選択してください")
                return
            target_dir = Path(self.custom_dir_var.get())
            
        # 確認ダイアログ
        dir_name = str(target_dir) if target_dir else "BunkoOCR結果フォルダ"
        result = messagebox.askyesno(
            "確認",
            f"以下の設定でバッチ処理を開始します:\n\n"
            f"対象: {dir_name}\n"
            f"並列処理: {'有効' if self.parallel_var.get() else '無効'}\n"
            f"ワーカー数: {self.workers_var.get()}\n\n"
            f"よろしいですか？"
        )
        
        if not result:
            return
            
        # 処理を別スレッドで実行
        self.processing = True
        self.start_button.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(
            target=self.run_batch_processing,
            args=(target_dir,)
        )
        thread.daemon = True
        thread.start()
        
    def run_batch_processing(self, target_dir):
        """バッチ処理を実行（別スレッド）"""
        try:
            self.log_message("バッチ処理を開始します...")
            self.status_var.set("ディレクトリをスキャン中...")
            
            # アナライザーを初期化
            self.analyzer = BatchAnalyzer()
            
            # ファイルをスキャン
            file_groups = self.analyzer.scan_directories(target_dir)
            
            if not file_groups:
                self.log_message("処理対象のファイルが見つかりませんでした", "WARNING")
                return
                
            self.log_message(f"{len(file_groups)}個のグループが見つかりました")
            
            # プログレスバーを設定
            self.progress['maximum'] = len(file_groups)
            self.progress['value'] = 0
            
            # 処理を実行
            for i, file_group in enumerate(file_groups, 1):
                self.status_var.set(f"処理中... [{i}/{len(file_groups)}]")
                
                result = self.analyzer.process_file_group(file_group)
                self.analyzer.results.append(result)
                
                if result['status'] == 'success':
                    self.log_message(
                        f"✅ {result['school_name']} {result['year']}年 - 処理完了"
                    )
                else:
                    self.log_message(
                        f"❌ {result.get('school_name', '不明')} {result.get('year', '不明')}年 - エラー: {result.get('error', '不明')}",
                        "ERROR"
                    )
                    
                self.progress['value'] = i
                self.root.update()
                
            # データベースに保存
            if self.create_backup_var.get():
                self.status_var.set("バックアップを作成中...")
                self.create_backup()
                
            self.status_var.set("データベースに保存中...")
            self.analyzer.save_to_database(self.analyzer.results)
            
            # レポートを生成
            self.status_var.set("レポートを生成中...")
            self.report_file = self.analyzer.generate_summary_report()
            
            # 完了
            self.log_message("=" * 50)
            self.log_message("バッチ処理が完了しました！")
            self.log_message(f"処理件数: {self.analyzer.stats['processed']}/{self.analyzer.stats['total_files']}")
            self.log_message(f"エラー件数: {self.analyzer.stats['failed']}")
            self.log_message("=" * 50)
            
            self.status_var.set("完了！")
            
            # ボタンを有効化
            self.view_db_button.config(state='normal')
            self.view_report_button.config(state='normal')
            
            # 完了通知
            messagebox.showinfo(
                "完了",
                f"バッチ処理が完了しました！\n\n"
                f"処理件数: {self.analyzer.stats['processed']}\n"
                f"エラー件数: {self.analyzer.stats['failed']}"
            )
            
        except Exception as e:
            self.log_message(f"エラーが発生しました: {str(e)}", "ERROR")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")
        finally:
            self.processing = False
            self.start_button.config(state='normal')
            
    def create_backup(self):
        """データベースのバックアップを作成"""
        import shutil
        db_file = Path("entrance_exam_database.xlsx")
        if db_file.exists():
            backup_file = f"entrance_exam_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            shutil.copy(db_file, backup_file)
            self.log_message(f"バックアップを作成: {backup_file}")
            
    def open_database(self):
        """データベースファイルを開く"""
        import subprocess
        import platform
        
        db_file = "entrance_exam_database.xlsx"
        if Path(db_file).exists():
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', db_file])
            elif platform.system() == 'Windows':
                subprocess.run(['start', db_file], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', db_file])
        else:
            messagebox.showerror("エラー", "データベースファイルが見つかりません")
            
    def open_report(self):
        """レポートファイルを開く"""
        import subprocess
        import platform
        
        if hasattr(self, 'report_file') and Path(self.report_file).exists():
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.report_file])
            elif platform.system() == 'Windows':
                subprocess.run(['start', self.report_file], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.report_file])
        else:
            messagebox.showerror("エラー", "レポートファイルが見つかりません")
            
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


def main():
    """メイン関数"""
    app = BatchAnalyzerGUI()
    app.run()


if __name__ == "__main__":
    main()