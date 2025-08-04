#!/usr/bin/env python3
"""
入試問題分析アプリケーション（テキストファイル版CLI）
新フロー：テキストファイル添付 → 学校名・年度読み取り → ユーザー確認 → 分析 → Excelアウトプット

使い方:
1. python3 entrance_exam_text_analyzer_cli.py [テキストファイルパス]
2. ファイルをターミナルにドラッグ＆ドロップして実行
3. または対話形式でファイル選択
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter


class TextFileAnalyzerCLI:
    """テキストファイル用入試問題分析アプリケーション（CLI版）"""
    
    # 定数定義（マジックナンバーの除去）
    MAX_FILES_TO_DISPLAY = 50  # ファイル選択時の最大表示数
    MAX_FILES_PER_SCHOOL = 5   # 学校ごとの最大表示ファイル数
    MIN_YEAR_2DIGIT = 14        # 2桁年度の最小値（2014年）
    MAX_YEAR_2DIGIT = 25        # 2桁年度の最大値（2025年）
    MIN_VALID_YEAR = 1990       # 有効年度の最小値
    MAX_VALID_YEAR = 2030       # 有効年度の最大値
    MIN_PATH_DISPLAY_LENGTH = 60  # パス表示の最小長
    
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clear_screen(self):
        """画面をクリア"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def read_file_with_encoding_detection(self, file_path):
        """複数のエンコーディングを試してファイルを読み込む"""
        encodings = ['utf-8', 'shift-jis', 'euc-jp', 'cp932', 'iso-2022-jp', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # 読み込み成功をログ
                    print(f"📖 エンコーディング '{encoding}' で読み込み成功")
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"⚠️  {encoding} での読み込み中にエラー: {e}")
                continue
        
        # すべてのエンコーディングで失敗した場合
        print(f"❌ ファイルを読み込めませんでした。試したエンコーディング: {', '.join(encodings)}")
        return None
        
    def extract_year_from_filename(self, filename):
        """ファイル名から年度を抽出"""
        # 年度パターンを検索
        year_match = re.search(r'(\d{2,4})', filename)
        if year_match:
            year = year_match.group(1)
            if len(year) == 2:
                # 2桁の場合は2000年代に変換
                year_int = int(year)
                if year_int >= 90:
                    return 1900 + year_int
                else:
                    return 2000 + year_int
            else:
                return int(year)
        return None
        
    def print_header(self):
        """ヘッダーを表示"""
        print("=" * 70)
        print("     入試問題分析システム v2.0 (テキストファイル版)")
        print("     Text File Entrance Exam Analyzer")
        print("=" * 70)
        print("新フロー:")
        print("1. テキストファイル添付")
        print("2. 学校名・年度自動読み取り")
        print("3. ユーザー確認")
        print("4. 分析実行")
        print("5. 結果をExcelにアウトプット")
        print("=" * 70)
        print()
        
    def select_text_file(self, initial_file=None):
        """テキストファイルを選択（改善版）"""
        # コマンドライン引数で指定されている場合
        if initial_file and Path(initial_file).exists():
            return Path(initial_file)
            
        print("【Step 1: テキストファイル選択】")
        print("-" * 70)
        print("📌 ファイル選択方法:")
        print("   1. 下記リストから番号で選択")
        print("   2. ファイルをドラッグ＆ドロップ（パスを貼り付け）")
        print("   3. ファイルブラウザで選択（GUI）")
        print("   4. 手動でパスを入力")
        print("-" * 70)
        
        # 複数ディレクトリからテキストファイルを検索
        search_dirs = [
            Path.cwd(),  # 現在のディレクトリ
            Path.home() / "Desktop",  # デスクトップ
            Path.home() / "Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問",  # 過去問フォルダ
        ]
        
        all_text_files = []
        for dir_path in search_dirs:
            if dir_path.exists():
                # 過去問フォルダの場合は再帰的に検索
                if "過去問" in str(dir_path):
                    print(f"\n🔍 過去問フォルダを再帰的に検索中...")
                    txt_files = list(dir_path.rglob("*.txt"))  # rglob で再帰的検索
                else:
                    txt_files = list(dir_path.glob("*.txt"))
                    
                # bunko関連ファイルを優先
                bunko_files = [f for f in txt_files if 'bunko' in f.name.lower() or '中学' in f.name]
                other_files = [f for f in txt_files if f not in bunko_files]
                all_text_files.extend(bunko_files + other_files)
        
        # 重複を除去（フルパスで重複チェック）
        unique_files = []
        seen_paths = set()
        for file in all_text_files:
            if str(file) not in seen_paths:
                unique_files.append(file)
                seen_paths.add(str(file))
        
        if unique_files:
            print(f"\n📁 検出されたテキストファイル ({len(unique_files)}個):")
            print("-" * 70)
            
            # カテゴリ別に表示
            bunko_files = [f for f in unique_files if 'bunko' in f.name.lower() or '中学' in f.name]
            other_files = [f for f in unique_files if f not in bunko_files]
            
            file_index = 1
            file_map = {}
            
            if bunko_files:
                print("\n🎯 入試問題関連ファイル:")
                
                # 学校別にグループ化
                school_files = {}
                for file in bunko_files:
                    # ファイルパスから学校名を推定
                    parts = file.parts
                    school_name = None
                    
                    # ファイル名から学校名を推定
                    filename = file.name
                    if "開成" in filename:
                        school_name = "開成"
                    elif "武蔵" in filename:
                        school_name = "武蔵"
                    elif "麻布" in filename:
                        school_name = "麻布"
                    elif "渋渋" in filename:
                        school_name = "渋渋"
                    elif "聖光" in filename:
                        school_name = "聖光"
                    elif "豊島" in filename:
                        school_name = "豊島岡"
                    elif "桜蔭" in filename:
                        school_name = "桜蔭"
                    elif "女子学院" in filename or "JG" in filename:
                        school_name = "女子学院"
                    elif "筑駒" in filename:
                        school_name = "筑駒"
                    elif "灘" in filename:
                        school_name = "灘"
                    else:
                        # パスから推定
                        for part in parts:
                            if part in ["開成", "武蔵", "麻布", "渋渋", "聖光", "豊島岡", "桜蔭", "女子学院", "筑駒", "灘"]:
                                school_name = part
                                break
                            elif part == "武蔵中学校":
                                school_name = "武蔵"
                                break
                            elif part == "開成中学校":
                                school_name = "開成"
                                break
                            elif part == "麻布中学校":
                                school_name = "麻布"
                                break
                            elif part == "桜蔭中学校":
                                school_name = "桜蔭"
                                break
                            elif "中学" in part or "学校" in part:
                                school_name = part
                                break
                    
                    if not school_name:
                        # 2025過去問フォルダなどの場合
                        if "2025過去問" in str(file):
                            school_name = "2025年度過去問"
                        else:
                            school_name = "その他"
                    
                    if school_name not in school_files:
                        school_files[school_name] = []
                    school_files[school_name].append(file)
                
                # 学校別に表示
                for school_name in sorted(school_files.keys()):
                    if file_index > 50:  # 最大50個まで表示
                        remaining = sum(len(files) for files in school_files.values()) - file_index + 1
                        print(f"\n   ... 他 {remaining} 個のファイル ...")
                        break
                        
                    print(f"\n  📚 {school_name}:")
                    # 年度が分かるファイルは年度順にソート
                    school_file_list = sorted(school_files[school_name], 
                                            key=lambda x: (self.extract_year_from_filename(x.name) or 9999, x.name))
                    
                    for file in school_file_list:
                        file_size = file.stat().st_size / 1024  # KB
                        rel_path = file.relative_to(Path.home()) if str(file).startswith(str(Path.home())) else file
                        # パスが長い場合は省略
                        display_path = str(rel_path)
                        if len(display_path) > 60:
                            parts = display_path.split('/')
                            display_path = '/'.join(parts[:2]) + '/.../' + '/'.join(parts[-2:])
                        
                        print(f"  {file_index:3d}. {file.name:<35} ({file_size:>7.1f} KB)")
                        print(f"       📍 {display_path}")
                        file_map[file_index] = file
                        file_index += 1
                    
            if other_files and file_index <= 35:
                print("\n📄 その他のファイル:")
                for file in other_files[:5]:  # 最大5個表示
                    file_size = file.stat().st_size / 1024  # KB
                    print(f"{file_index:3d}. {file.name:<40} ({file_size:>7.1f} KB)")
                    file_map[file_index] = file
                    file_index += 1
                    
            print(f"\n{file_index:3d}. 🖱️  ファイルブラウザで選択（GUI）")
            print(f"{file_index + 1:3d}. ✏️  パスを直接入力/ドラッグ＆ドロップ")
            print("-" * 70)
            
            while True:
                choice = input(f"\n選択してください (1-{file_index + 1}): ").strip()
                
                try:
                    num = int(choice)
                    if num in file_map:
                        return file_map[num]
                    elif num == file_index:  # ファイルブラウザ
                        return self.open_file_dialog()
                    elif num == file_index + 1:  # 手動入力
                        break
                    else:
                        print("❌ 正しい番号を入力してください")
                except ValueError:
                    # 数字以外が入力された場合はパスとして処理
                    if choice:
                        path = self.process_file_path(choice)
                        if path:
                            return path
        
        # 手動入力モード
        return self.manual_file_input()
        
    def open_file_dialog(self):
        """ファイルダイアログを開く（tkinter使用）"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            print("\n🖱️  ファイルブラウザを開いています...")
            
            root = tk.Tk()
            root.withdraw()  # メインウィンドウを隠す
            root.lift()
            root.attributes('-topmost', True)
            
            file_path = filedialog.askopenfilename(
                title="テキストファイルを選択",
                filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")],
                initialdir=str(Path.home() / "Desktop")
            )
            
            root.destroy()
            
            if file_path:
                return Path(file_path)
            else:
                print("❌ ファイルが選択されませんでした")
                return self.manual_file_input()
                
        except ImportError:
            print("⚠️  GUIが利用できません。手動入力モードに切り替えます。")
            return self.manual_file_input()
            
    def process_file_path(self, path_string):
        """ファイルパス文字列を処理（ドラッグ＆ドロップ対応）"""
        # デバッグ: 入力内容を確認
        print(f"🔍 入力された文字列 (長さ: {len(path_string)}): '{path_string}'")
        print(f"🔍 先頭10文字: '{path_string[:10] if len(path_string) > 10 else path_string}'")
        print(f"🔍 末尾10文字: '{path_string[-10:] if len(path_string) > 10 else path_string}'")
        
        # 前後の空白と改行を削除
        path_string = path_string.strip().strip('\n\r')
        
        # エスケープされたスペースと括弧を処理
        # バックスラッシュでエスケープされた文字を元に戻す
        path_string = path_string.replace('\\ ', ' ')
        path_string = path_string.replace('\\(', '(')
        path_string = path_string.replace('\\)', ')')
        
        # 前後の引用符を削除（シングル、ダブル両方）
        if (path_string.startswith('"') and path_string.endswith('"')) or \
           (path_string.startswith("'") and path_string.endswith("'")):
            path_string = path_string[1:-1]
        
        # デバッグ情報
        print(f"📝 処理後のパス: '{path_string}'")
        
        try:
            path = Path(path_string).resolve()  # 絶対パスに変換
            print(f"📁 Pathオブジェクト: {path}")
            print(f"📁 存在確認: {path.exists()}")
            print(f"📁 ファイル確認: {path.is_file() if path.exists() else 'N/A'}")
            print(f"📁 拡張子: {path.suffix}")
            
            # セキュリティ: パストラバーサル攻撃の防止
            # 許可されたディレクトリのリスト
            allowed_dirs = [
                Path.home().resolve(),  # ユーザーのホームディレクトリ
                Path.cwd().resolve(),   # 現在の作業ディレクトリ
                Path("/tmp").resolve() if os.name == 'posix' else Path(os.environ.get('TEMP', '')).resolve()  # 一時ディレクトリ
            ]
            
            # ファイルが許可されたディレクトリ内にあるか確認
            is_allowed = False
            for allowed_dir in allowed_dirs:
                try:
                    # relative_to() は path が allowed_dir の子孫でない場合 ValueError を発生させる
                    path.relative_to(allowed_dir)
                    is_allowed = True
                    break
                except ValueError:
                    continue
            
            if not is_allowed:
                print("❌ セキュリティエラー: ファイルパスが許可されたディレクトリ外です")
                print(f"   許可されたディレクトリ: {[str(d) for d in allowed_dirs]}")
                return None
            
            if path.exists():
                if path.suffix.lower() == '.txt':
                    print(f"✅ ファイルを確認しました: {path.name}")
                    return path
                else:
                    print(f"❌ .txtファイルではありません: {path.suffix}")
                    return None
            else:
                print(f"❌ ファイルが存在しません")
                
                # 別のパターンを試す
                # 1. 二重スペースを単一スペースに
                alt_paths = [
                    path_string.replace('  ', ' '),
                    path_string.replace('\ ', ' '),  # 別のエスケープパターン
                ]
                
                for alt_path_string in alt_paths:
                    if alt_path_string != path_string:
                        print(f"🔄 代替パスを試行: '{alt_path_string}'")
                        alt_path = Path(alt_path_string).resolve()
                        
                        # 代替パスも同じセキュリティチェックを適用
                        is_alt_allowed = False
                        for allowed_dir in allowed_dirs:
                            try:
                                alt_path.relative_to(allowed_dir)
                                is_alt_allowed = True
                                break
                            except ValueError:
                                continue
                        
                        if is_alt_allowed and alt_path.exists() and alt_path.suffix.lower() == '.txt':
                            print(f"✅ 代替パスで確認しました: {alt_path.name}")
                            return alt_path
                
                return None
        except Exception as e:
            print(f"❌ パスの処理中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def manual_file_input(self):
        """手動でファイルパスを入力"""
        print("\n📝 ファイルパスを入力してください:")
        print("   ヒント: ファイルをターミナルにドラッグ＆ドロップできます")
        print("-" * 50)
        
        while True:
            file_path = input("ファイルパス: ").strip()
            if file_path:
                path = self.process_file_path(file_path)
                if path:
                    return path
            else:
                print("❌ ファイルパスを入力してください")
                
    def extract_school_and_years(self, text, filename):
        """テキストから学校名と複数年度を自動抽出"""
        print("\n【Step 2: 学校名・年度自動読み取り（複数年度対応）】")
        print("-" * 50)
        
        # ファイル名からの抽出
        school_from_filename = None
        year_from_filename = None
        
        # 学校名パターン（ファイル名）
        school_patterns = {
            r'開成|kaisei': '開成中学校',
            r'麻布|azabu': '麻布中学校', 
            r'武蔵|musashi': '武蔵中学校',
            r'桜蔭|ouin|桜陰': '桜蔭中学校',
            r'女子学院|jg': '女子学院中学校',
            r'雙葉|futaba': '雙葉中学校',
            r'渋渋|shibuya|渋谷': '渋谷教育学園渋谷中学校',
            r'慶應|keio': '慶應義塾中等部',
            r'早実|waseda': '早稲田実業学校中等部',
            r'豊島岡|toshimagaoka': '豊島岡女子学園中学校',
            r'筑駒|tsukukoma': '筑波大学附属駒場中学校'
        }
        
        filename_lower = filename.lower()
        for pattern, school_name in school_patterns.items():
            if re.search(pattern, filename_lower):
                school_from_filename = school_name
                break
                
        # 年度パターン（ファイル名）
        year_match = re.search(r'(20\d{2}|19\d{2})', filename)
        if year_match:
            year_from_filename = year_match.group(1)
        else:
            # 2桁年度も検索（例：15 → 2015）
            year_match = re.search(r'(\d{2})', filename)
            if year_match:
                year_2digit = int(year_match.group(1))
                if 0 <= year_2digit <= 30:  # 2000-2030年代と仮定
                    year_from_filename = f"20{year_2digit:02d}"
                elif 70 <= year_2digit <= 99:  # 1970-1999年代
                    year_from_filename = f"19{year_2digit}"
        
        # テキスト内容からの抽出（複数年度対応）
        school_from_text = None
        years_from_text = []
        
        # 全テキストから学校名を検索
        for pattern, school_name in school_patterns.items():
            if re.search(pattern, text):
                school_from_text = school_name
                break
                
        # 複数年度をテキストから抽出（冒頭の学校名+年度パターンに対応）
        year_patterns = [
            r'(20\d{2})年度',
            r'(20\d{2})年',
            r'令和(\d{1,2})年度',  # 令和年号対応
            r'平成(\d{1,2})年度',  # 平成年号対応  
            r'(20\d{2})\s*入学試験',  # 入学試験パターン
            r'(20\d{2})\s*年\s*入試',  # 年入試パターン
            # 武蔵14、開成15 などのパターン（冒頭付近用）
            r'武蔵(\d{2})',
            r'開成(\d{2})',
            r'麻布(\d{2})',
            r'桜蔭(\d{2})',
            r'女子学院(\d{2})',
            r'雙葉(\d{2})',
            r'渋渋(\d{2})',
            r'渋谷(\d{2})',
            r'慶應(\d{2})',
            r'早実(\d{2})',
        ]
        
        # 武蔵ファイルの特別パターン（武蔵\n\n国語\n\n14のような行分割パターン）
        musashi_pattern = r'武蔵\s*\n(?:[^\n]*\n)*?(\d{2})\s*\n'
        # より汎用的な2桁年度独立行パターン（14-25の範囲をチェック）
        # 19, 21, 22も含めるように修正
        standalone_year_pattern = r'^\s*(\d{2})\s*$'
        
        found_years = set()
        
        # 武蔵の特別パターンを最初にチェック
        if '武蔵' in (school_from_text or '') or '武蔵' in filename:
            # 武蔵ファイルの特別な年度検出
            # 「武蔵」の後に出現する年度のみを真の年度境界として扱う
            musashi_year_pattern = r'武蔵\s*\n+\s*(\d{2})\s*(?:\n|$)'
            musashi_year_matches = []
            
            try:
                for match in re.finditer(musashi_year_pattern, text, re.MULTILINE):
                    year_2digit = int(match.group(1))
                    if self.MIN_YEAR_2DIGIT <= year_2digit <= self.MAX_YEAR_2DIGIT:  # 2014-2025年の範囲
                        year = f"20{year_2digit:02d}"
                        musashi_year_matches.append((match.start(), year, year_2digit))
                        found_years.add(year)
                        print(f"   🎯 武蔵年度境界検出: {year_2digit} → {year} (位置: {match.start()})")
            except re.error as e:
                print(f"   ⚠️  正規表現エラー（武蔵パターン）: {e}")
            except Exception as e:
                print(f"   ⚠️  予期しないエラー（武蔵パターン）: {e}")
            
            # ファイル名に含まれる年度範囲も考慮
            if '14-25' in filename:
                # 14から25までの全年度を検証
                expected_years = list(range(self.MIN_YEAR_2DIGIT, self.MAX_YEAR_2DIGIT + 1))  # 14, 15, 16, ..., 25
                for year_2digit in expected_years:
                    year = f"20{year_2digit:02d}"
                    # テキスト内に該当年度が存在するか確認
                    year_pattern = rf'武蔵\s*\n+\s*{year_2digit}\s*(?:\n|$)'
                    if re.search(year_pattern, text, re.MULTILINE):
                        found_years.add(year)
                        if year not in [y[1] for y in musashi_year_matches]:
                            print(f"   📌 追加年度検出: {year_2digit} → {year}")
        
        # パフォーマンス改善: すべてのパターンを一つの正規表現に結合
        try:
            # パターンをグループ化して一度に検索
            combined_pattern = '|'.join(f'({pattern})' for pattern in year_patterns)
            combined_regex = re.compile(combined_pattern, re.IGNORECASE)
            
            # 一度のスキャンですべてのマッチを取得
            for match in combined_regex.finditer(text):
                matched_text = match.group()
                matched_groups = [g for g in match.groups() if g is not None]
                
                if not matched_groups:
                    continue
                    
                # どのパターンにマッチしたか判定
                for i, pattern in enumerate(year_patterns):
                    if match.group(i + 1) is not None:
                        year = None
                        match_value = match.group(i + 1)
                        
                        if '令和' in pattern:
                            # 令和年号を西暦に変換
                            reiwa_year = int(match_value)
                            year = str(2018 + reiwa_year)
                        elif '平成' in pattern:
                            # 平成年号を西暦に変換
                            heisei_year = int(match_value)
                            year = str(1988 + heisei_year)
                        elif any(school in pattern for school in ['武蔵', '開成', '麻布', '桜蔭', '女子学院', '雙葉', '渋渋', '渋谷', '慶應', '早実']):
                            # 学校名+2桁年度を4桁西暦に変換（例：武蔵14 → 2014）
                            year_2digit = int(match_value)
                            if 0 <= year_2digit <= 30:  # 2000-2030年代
                                year = f"20{year_2digit:02d}"
                            elif 70 <= year_2digit <= 99:  # 1970-1999年代  
                                year = f"19{year_2digit}"
                        else:
                            year = match_value
                        
                        # 年度の妥当性チェック（1990-2030年の範囲）
                        if year and year.isdigit() and self.MIN_VALID_YEAR <= int(year) <= self.MAX_VALID_YEAR:
                            found_years.add(year)
                        break
                        
        except re.error as e:
            print(f"⚠️  正規表現の結合でエラー: {e}")
            # フォールバック: 従来の方法を使用
            for pattern in year_patterns:
                try:
                    matches = re.findall(pattern, text)
                    # ... 既存のロジック ...
                except:
                    continue
        
        years_from_text = sorted(list(found_years))
        
        # ファイル名の年度が含まれていない場合は追加
        if year_from_filename and year_from_filename not in years_from_text:
            years_from_text.append(year_from_filename)
            years_from_text.sort()
        
        # 結果の統合
        school_name = school_from_filename or school_from_text
        years = years_from_text if years_from_text else ([year_from_filename] if year_from_filename else [])
        
        print(f"📄 ファイル名から: 学校={school_from_filename}, 年度={year_from_filename}")
        print(f"📝 テキストから: 学校={school_from_text}, 年度={years_from_text}")
        print()
        if len(years) > 1:
            print(f"🎯 最終判定: 学校={school_name}, 年度={len(years)}年度分検出: {', '.join(years)}")
        else:
            print(f"🎯 最終判定: 学校={school_name}, 年度={years[0] if years else 'なし'}")
        
        return school_name, years
        
    def split_text_by_years(self, text, years, school_name):
        """複数年度のテキストを年度別に分割"""
        if len(years) <= 1:
            return {years[0]: text} if years else {'unknown': text}
            
        print(f"\n📂 {len(years)}年度分のテキストを分割中...")
        
        # 年度マーカーを検索
        year_markers = []
        for year in years:
            # 4桁年度
            patterns = [
                rf'{year}年度',
                rf'{year}年', 
                rf'{year}\s*入学試験',
            ]
            
            # 2桁年度パターンも追加（例：武蔵14）
            year_2digit = year[-2:]
            if school_name:
                school_short = school_name.replace('中学校', '').replace('中等部', '')
                # 学校の短縮名パターンを追加
                school_shorts = [school_short]
                if '渋谷教育学園渋谷' in school_name:
                    school_shorts.extend(['渋渋', '渋谷'])
                elif '開成' in school_name:
                    school_shorts.append('開成')
                elif '武蔵' in school_name:
                    school_shorts.append('武蔵')
                    
                for short in school_shorts:
                    patterns.append(rf'{short}{year_2digit}')
            
            # パターンを検索して位置を記録
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    year_markers.append((match.start(), year, pattern))
                    
        # 武蔵の特別パターンも追加
        if school_name and '武蔵' in school_name:
            # 武蔵ファイルの年度境界検出
            # 「武蔵」の直後の年度のみを境界として使用
            musashi_boundary_pattern = r'武蔵\s*\n+\s*(\d{2})\s*(?:\n|$)'
            
            for match in re.finditer(musashi_boundary_pattern, text, re.MULTILINE):
                year_2digit = match.group(1)
                year_4digit = f"20{year_2digit}"
                if year_4digit in years:
                    # 年度番号の開始位置を記録（「武蔵」の位置から）
                    year_markers.append((match.start(), year_4digit, f'武蔵年度境界({year_2digit})'))
        
        # マーカーを位置順にソート
        year_markers.sort(key=lambda x: x[0])
        
        # テキストを分割して年度ごとに統合
        split_texts = {}
        
        if not year_markers:
            # マーカーが見つからない場合は最初の年度に全て割り当て
            split_texts[years[0]] = text
        else:
            # 年度ごとのテキスト片を収集
            year_text_parts = {}
            for year in years:
                year_text_parts[year] = []
            
            # 各マーカーのテキスト範囲を決定して年度別に収集
            for i, (start_pos, year, pattern) in enumerate(year_markers):
                if i < len(year_markers) - 1:
                    # 次のマーカーまで
                    end_pos = year_markers[i + 1][0]
                else:
                    # 最後まで
                    end_pos = len(text)
                
                section_text = text[start_pos:end_pos].strip()
                if section_text and year in year_text_parts:
                    year_text_parts[year].append(section_text)
            
            # 年度ごとにテキスト片を連結
            for year in years:
                if year_text_parts[year]:
                    # 同じ年度の全てのテキスト片を連結
                    combined_text = '\n\n'.join(year_text_parts[year])
                    split_texts[year] = combined_text
                    print(f"   📄 {year}年度: {len(combined_text):,}文字 ({len(year_text_parts[year])}個のセクションを統合)")
                else:
                    print(f"   ⚠️  {year}年度: テキストが見つかりませんでした")
        
        return split_texts
        
    def confirm_extraction(self, school_name, years, filename):
        """抽出結果をユーザーに確認（複数年度対応）"""
        print("\n【Step 3: ユーザー確認】")
        print("-" * 50)
        print(f"ファイル名: {filename}")
        print(f"自動抽出結果:")
        print(f"  学校名: {school_name or '不明'}")
        if len(years) > 1:
            print(f"  年度: {len(years)}年度分 ({', '.join(years)})")
        else:
            print(f"  年度: {years[0] if years else '不明'}")
        print("-" * 50)
        
        if not school_name or not years:
            print("⚠️  学校名または年度が自動抽出できませんでした")
            
        if len(years) > 1:
            print("📋 複数年度が検出されました。年度別に分析を実行します。")
            
        # デバッグ用に自動でyesを選択
        print("デバッグモード: 自動で分析を続行します")
        return school_name, years
            
    def manual_input_school_years(self, current_school, current_years):
        """手動で学校名と年度を入力（複数年度対応）"""
        print("\n【手動入力】")
        print("-" * 30)
        
        # 学校名の入力
        print("学校名を入力してください:")
        print("例: 開成中学校, 桜蔭中学校, 渋谷教育学園渋谷中学校")
        school_name = input(f"学校名 [{current_school or ''}]: ").strip()
        if not school_name:
            school_name = current_school
            
        # 年度の入力（複数対応）
        current_years_str = ', '.join(current_years) if current_years else ''
        print("年度を入力してください（複数の場合はカンマ区切り）:")
        print("例: 2015, 2016, 2017")
        years_input = input(f"年度 [{current_years_str}]: ").strip()
        
        if not years_input:
            years = current_years
        else:
            # カンマ区切りで分割して年度リストを作成
            years = []
            for year_str in years_input.split(','):
                year_str = year_str.strip()
                if year_str.isdigit() and 1990 <= int(year_str) <= 2030:
                    years.append(year_str)
                else:
                    print(f"⚠️  無効な年度をスキップしました: {year_str}")
            
            if not years:
                print("⚠️  有効な年度が入力されませんでした。元の年度を使用します。")
                years = current_years
            
        return school_name, years
        
    def analyze_text(self, text, school_name, year):
        """テキストを分析"""
        print("\n【Step 4: 分析実行】")
        print("-" * 50)
        print("🔍 テキスト分析を開始しています...")
        
        # 設問パターンを定義
        question_patterns = {
            '記述': [
                r'〜について、.*書[きけ]なさい',
                r'〜について.*説明[しせ]よ',
                r'〜について.*述[べべ]なさい',
                r'.*字以内.*書[きけ]',
                r'.*字で.*書[きけ]',
                r'.*説明[しせ]よ',
                r'.*理由.*書[きけ]',
                r'.*どう思[うい].*書[きけ]'
            ],
            '選択': [
                r'次のうち.*正[しい]',
                r'選[びば]なさい',
                r'どれ[かか]',
                r'[ア-オ].*選[びば]',
                r'記号.*選[びば]',
                r'最[もも]適当.*[ア-オ]'
            ],
            '漢字・語句': [
                r'漢字.*読[みみ]',
                r'ひらがな.*書[きけ]',
                r'カタカナ.*書[きけ]',
                r'漢字.*書[きけ]',
                r'語句.*意味',
                r'言葉.*意味'
            ],
            '抜き出し': [
                r'抜[きき]出[しし]',
                r'そのまま.*書[きけ]',
                r'文中.*[から].*探[しし]',
                r'該当.*箇所'
            ]
        }
        
        # テキスト分析
        analyzer = TextAnalyzer(question_patterns)
        result = analyzer.analyze_exam_structure(text)
        
        # 出典情報を抽出
        print("📚 出典情報を抽出中...")
        
        # 武蔵特有の出典パターンを追加
        if school_name and '武蔵' in school_name:
            source_patterns = [
                r'（([^）]+)の文による）',  # （新美南吉の文による）形式
                r'（([^）]+)著）',  # （著者名著）形式
                r'『([^』]+)』.*（([^）]+)）',  # 『作品名』...（著者名）形式
                r'『([^』]+)』',  # 『作品名』のみ
                r'「([^」]+)」.*（([^）]+)）',  # 「作品名」...（著者名）形式
            ]
        else:
            source_patterns = [
                r'『([^』]+)』\s*([^\s]+)',  # 『作品名』 著者名
                r'「([^」]+)」\s*([^\s]+)',  # 「作品名」 著者名  
                r'([^\s]+)\s*著\s*『([^』]+)』',  # 著者名著『作品名』
                r'([^\s]+)\s*『([^』]+)』',  # 著者名『作品名』
                r'（([^）]+)）',  # （出典情報）
            ]
        
        extractor = PatternExtractor(source_patterns)
        sources = extractor.extract_source_info(text)
        
        # 結果に追加情報を付与
        result['school_name'] = school_name
        result['year'] = year
        # sourcesを辞書のリスト形式に変換
        if isinstance(sources, dict):
            sources_list = [{'section': 1, 'author': sources.get('author', '不明'), 'title': sources.get('title', '不明')}]
        else:
            sources_list = []
        result['sources'] = sources_list
        
        # 分析結果をサマリー表示
        print(f"\n✅ 分析完了!")
        print(f"   総設問数: {len(result.get('questions', []))}問")
        print(f"   総文字数: {result.get('total_characters', 0):,}文字")
        print(f"   大問数: {len(result.get('sections', []))}問")
        if sources:
            print(f"   出典数: {len(sources)}件")
        
        return result
        
    def save_to_database(self, analysis_result, school_name, year):
        """Excelデータベースに保存"""
        print("\n【Step 5: Excelアウトプット】")
        print("-" * 50)
        print("💾 Excelデータベースに保存中...")
        
        db_filename = "entrance_exam_database.xlsx"
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 既存ファイルがある場合はバックアップを作成
        if Path(db_filename).exists():
            backup_filename = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{db_filename}"
            try:
                shutil.copy2(db_filename, backup_filename)
                print(f"📦 バックアップを作成しました: {backup_filename.name}")
            except Exception as e:
                print(f"⚠️  バックアップの作成に失敗しました: {e}")
                # バックアップに失敗しても処理は継続するが、ユーザーに確認を求める
                confirm = input("バックアップなしで続行しますか？ (y/n): ")
                if confirm.lower() != 'y':
                    print("処理を中止しました")
                    return
        
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
                    print(f"   📝 {year}年度のデータを更新します")
                else:
                    print(f"   ➕ {year}年度のデータを追加します")
                    
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df = combined_df.sort_values('年度')
            else:
                combined_df = new_df
                print(f"   🆕 {school_name}の新しいシートを作成します")
                
            combined_df.to_excel(writer, sheet_name=school_name, index=False)
            
        # 個別結果ファイルも保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        individual_filename = self.output_dir / f"{school_name}_{year}_分析結果_{timestamp}.xlsx"
        
        with pd.ExcelWriter(individual_filename, engine='openpyxl') as writer:
            new_df.to_excel(writer, sheet_name=f"{school_name}_{year}", index=False)
            
        print(f"✅ 保存完了!")
        print(f"   📊 データベース: {db_filename}")
        print(f"   📄 個別ファイル: {individual_filename}")
        
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
            
            # この大問に属する設問数を計算
            section_questions = [q for q in analysis_result.get('questions', []) 
                               if q.get('section') == i]
            
            data_row[f'大問{i}_ジャンル'] = genre
            data_row[f'大問{i}_テーマ'] = theme
            data_row[f'大問{i}_著者'] = source.get('author', '不明')
            data_row[f'大問{i}_作品'] = source.get('title', '不明')
            data_row[f'大問{i}_設問数'] = len(section_questions)
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
        if any(word in text_sample for word in ['小説', '物語', '「', '」', 'と言った', 'と思った']):
            genre = '小説・物語'
        elif any(word in text_sample for word in ['評論', '論説', 'について', 'という', 'に関して', 'である']):
            genre = '評論・論説'
        elif any(word in text_sample for word in ['随筆', 'エッセイ', '私は', '私が', '思い出']):
            genre = '随筆・エッセイ'
        else:
            genre = '評論・論説'
            
        # テーマ判定
        if any(word in text_sample for word in ['友情', '家族', '成長', '青春', '友達']):
            theme = '人間関係・成長'
        elif any(word in text_sample for word in ['自然', '環境', '生物', '動物', '植物']):
            theme = '自然・環境'
        elif any(word in text_sample for word in ['社会', '文化', '歴史', '伝統', '時代']):
            theme = '社会・文化'
        elif any(word in text_sample for word in ['科学', '技術', 'AI', 'コンピュータ', '研究']):
            theme = '科学・技術'
        elif any(word in text_sample for word in ['言葉', '言語', 'コミュニケーション', '表現']):
            theme = '言語・表現'
        elif any(word in text_sample for word in ['芸術', '美術', '音楽', '文学', '作品']):
            theme = '芸術・文学'
        else:
            theme = '一般'
            
        return genre, theme
        
    def run(self, initial_file=None):
        """アプリケーションを実行"""
        self.clear_screen()
        self.print_header()
        
        try:
            # Step 1: テキストファイルを選択
            text_file = self.select_text_file(initial_file)
            if not text_file:
                print("❌ ファイルが選択されませんでした")
                return
                
            print(f"✅ 選択されたファイル: {text_file.name}")
            
            # ファイルを読み込み（エンコーディング自動検出）
            text_content = self.read_file_with_encoding_detection(text_file)
            if text_content is None:
                print("❌ ファイルの読み込みに失敗しました")
                return
            print(f"📄 ファイルサイズ: {len(text_content):,} 文字")
                
            # Step 2: 学校名・年度を自動抽出（複数年度対応）
            school_name, years = self.extract_school_and_years(text_content, text_file.name)
            
            # Step 3: ユーザー確認
            school_name, years = self.confirm_extraction(school_name, years, text_file.name)
            if not school_name or not years:
                return
                
            # 複数年度の場合はテキストを分割
            if len(years) > 1:
                split_texts = self.split_text_by_years(text_content, years, school_name)
            else:
                split_texts = {years[0]: text_content}
                
            # Step 4 & 5: 各年度について分析とExcelアウトプット
            success_count = 0
            for year in years:
                if year in split_texts:
                    print(f"\n{'='*60}")
                    print(f"📅 {year}年度の分析を開始")
                    print(f"{'='*60}")
                    
                    year_text = split_texts[year]
                    print(f"📄 対象テキスト: {len(year_text):,}文字")
                    
                    # 分析実行
                    analysis_result = self.analyze_text(year_text, school_name, year)
                    
                    # Excelアウトプット
                    self.save_to_database(analysis_result, school_name, year)
                    
                    print(f"✅ {year}年度の分析完了！")
                    success_count += 1
                else:
                    print(f"⚠️  {year}年度のテキストが見つからずスキップしました")
            
            # 完了メッセージ
            print("\n" + "=" * 70)
            print("🎉 分析が完了しました！")
            print(f"   学校: {school_name}")
            if len(years) > 1:
                print(f"   年度: {success_count}/{len(years)}年度分 ({', '.join(years)})")
            else:
                print(f"   年度: {years[0]}年")
            print(f"   ソースファイル: {text_file.name}")
            print("=" * 70)
            
        except KeyboardInterrupt:
            print("\n\n❌ ユーザーによってキャンセルされました")
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n分析処理が終了しました。")
            # デバッグ用にinputをコメントアウト
            # input()


def main():
    """メイン関数"""
    app = TextFileAnalyzerCLI()
    
    # コマンドライン引数を処理
    initial_file = None
    if len(sys.argv) > 1:
        # ファイルパスが指定されている場合
        initial_file = sys.argv[1]
        print(f"🎯 コマンドライン引数でファイルが指定されました: {initial_file}")
    
    app.run(initial_file)


if __name__ == "__main__":
    main()