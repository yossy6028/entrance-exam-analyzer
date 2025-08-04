#!/usr/bin/env python3
"""
入試問題テキスト分析 バッチ処理版
複数の学校・年度のテキストファイルを一括で処理
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import List, Dict, Tuple
import concurrent.futures
from collections import defaultdict

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter


class BatchAnalyzer:
    """バッチ処理アナライザー"""
    
    def __init__(self):
        # 処理対象のルートディレクトリ
        self.bunko_results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.kakomon_dir = Path.home() / "Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
        
        # 処理結果を格納
        self.results = []
        self.errors = []
        
        # 統計情報
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'schools': defaultdict(int),
            'years': defaultdict(int)
        }
        
    def scan_directories(self, target_dir: Path = None, pattern: str = "**/text*.txt") -> List[Dict]:
        """ディレクトリをスキャンして処理対象ファイルを収集"""
        if target_dir is None:
            target_dir = self.bunko_results_dir
            
        print(f"📂 ディレクトリをスキャン中: {target_dir}")
        file_groups = []
        
        # BunkoOCR結果フォルダの構造を考慮
        if target_dir == self.bunko_results_dir and target_dir.exists():
            # 各結果フォルダをグループとして扱う
            for result_folder in sorted(target_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                if result_folder.is_dir():
                    text_files = sorted(result_folder.glob("text*.txt"))
                    if text_files:
                        # フォルダ名から情報を抽出
                        school, year = self.extract_info_from_path(result_folder)
                        file_groups.append({
                            'files': text_files,
                            'folder': result_folder,
                            'school': school,
                            'year': year,
                            'timestamp': datetime.fromtimestamp(result_folder.stat().st_mtime)
                        })
        else:
            # 通常のディレクトリスキャン
            all_files = list(target_dir.glob(pattern))
            
            # ファイルをグループ化（同じ親ディレクトリのtext*.txtをグループ化）
            groups = defaultdict(list)
            for file in all_files:
                if file.name.startswith('text') and file.suffix == '.txt':
                    groups[file.parent].append(file)
                else:
                    # 単独のテキストファイル
                    school, year = self.extract_info_from_path(file)
                    file_groups.append({
                        'files': [file],
                        'folder': file.parent,
                        'school': school,
                        'year': year,
                        'timestamp': datetime.fromtimestamp(file.stat().st_mtime)
                    })
            
            # グループ化されたファイルを追加
            for folder, files in groups.items():
                school, year = self.extract_info_from_path(folder)
                file_groups.append({
                    'files': sorted(files),
                    'folder': folder,
                    'school': school,
                    'year': year,
                    'timestamp': datetime.fromtimestamp(folder.stat().st_mtime)
                })
                
        self.stats['total_files'] = len(file_groups)
        return file_groups
        
    def extract_info_from_path(self, path: Path) -> Tuple[str, str]:
        """パスから学校名と年度を抽出"""
        path_str = str(path)
        
        # 学校名の抽出
        school_patterns = [
            r'(開成|麻布|武蔵|桜蔭|女子学院|雙葉|渋谷教育学園渋谷|渋渋|慶應義塾|早稲田実業)',
            r'(\w+中学校)',
            r'(\w+中等部)',
        ]
        
        school = ""
        for pattern in school_patterns:
            match = re.search(pattern, path_str)
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
            match = re.search(pattern, path_str)
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
        
    def process_file_group(self, file_group: Dict) -> Dict:
        """ファイルグループを処理"""
        try:
            files = file_group['files']
            school = file_group['school']
            year = file_group['year']
            
            # テキストを結合
            combined_text = ""
            for txt_file in files:
                try:
                    combined_text += txt_file.read_text(encoding='utf-8')
                    combined_text += "\n\n"
                except Exception as e:
                    print(f"  ⚠️  ファイル読み込みエラー: {txt_file.name} - {str(e)}")
                    continue
                    
            if not combined_text.strip():
                raise ValueError("テキストが空です")
                
            # テキストから情報を補完
            if not school or not year:
                school_from_text, year_from_text = self.extract_info_from_text(combined_text)
                school = school or school_from_text
                year = year or year_from_text
                
            if not school or not year:
                raise ValueError(f"学校名または年度が特定できません")
                
            # テキスト分析
            analyzer = TextAnalyzer()
            result = analyzer.analyze_exam_structure(combined_text)
            
            # 出典情報を抽出
            extractor = PatternExtractor()
            sources = extractor.extract_sources(combined_text)
            
            # 結果をまとめる
            analysis_result = {
                'school_name': school,
                'year': year,
                'folder': str(file_group['folder']),
                'file_count': len(files),
                'timestamp': file_group['timestamp'],
                'analysis': result,
                'sources': sources,
                'status': 'success'
            }
            
            # 統計情報を更新
            self.stats['processed'] += 1
            self.stats['schools'][school] += 1
            self.stats['years'][year] += 1
            
            return analysis_result
            
        except Exception as e:
            self.stats['failed'] += 1
            error_result = {
                'folder': str(file_group['folder']),
                'school_name': file_group.get('school', '不明'),
                'year': file_group.get('year', '不明'),
                'error': str(e),
                'status': 'failed'
            }
            self.errors.append(error_result)
            return error_result
            
    def extract_info_from_text(self, text: str) -> Tuple[str, str]:
        """テキスト内容から学校名と年度を抽出"""
        # 最初の500文字から抽出
        text_sample = text[:500]
        
        # 学校名の抽出
        school_patterns = [
            r'(開成|麻布|武蔵|桜蔭|女子学院|雙葉|渋谷教育学園渋谷|渋渋|慶應義塾|早稲田実業)',
            r'(\w+中学校)',
            r'(\w+中等部)',
        ]
        
        school = ""
        for pattern in school_patterns:
            match = re.search(pattern, text_sample)
            if match:
                school = match.group(1)
                if '中学校' not in school and '中等部' not in school:
                    school += '中学校'
                break
                
        # 年度の抽出
        year_patterns = [
            r'(20\d{2})年',
            r'(\d{2})年度',
            r'令和(\d+)年',
            r'平成(\d+)年',
        ]
        
        year = ""
        for pattern in year_patterns:
            match = re.search(pattern, text_sample)
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
        
    def save_to_database(self, results: List[Dict]):
        """処理結果をデータベースに保存"""
        db_filename = "entrance_exam_database.xlsx"
        
        # 既存ファイルがあるかチェック
        try:
            existing_sheets = pd.ExcelFile(db_filename, engine='openpyxl').sheet_names
        except FileNotFoundError:
            existing_sheets = []
            
        # 学校別にグループ化
        school_data = defaultdict(list)
        for result in results:
            if result['status'] == 'success':
                school_name = result['school_name']
                data_row = self.prepare_data_row(result)
                school_data[school_name].append(data_row)
                
        # Excelファイルに書き込み
        with pd.ExcelWriter(db_filename, engine='openpyxl', 
                           mode='a' if existing_sheets else 'w', 
                           if_sheet_exists='replace') as writer:
            for school_name, rows in school_data.items():
                new_df = pd.DataFrame(rows)
                
                if school_name in existing_sheets:
                    # 既存シートに追加
                    existing_df = pd.read_excel(db_filename, sheet_name=school_name)
                    existing_df['年度'] = pd.to_numeric(existing_df['年度'], errors='coerce')
                    
                    # 重複を避けるため、新しいデータの年度で既存データを削除
                    years_to_update = new_df['年度'].unique()
                    existing_df = existing_df[~existing_df['年度'].isin(years_to_update)]
                    
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    combined_df = combined_df.sort_values('年度')
                else:
                    combined_df = new_df.sort_values('年度')
                    
                combined_df.to_excel(writer, sheet_name=school_name, index=False)
                
    def prepare_data_row(self, result: Dict) -> Dict:
        """データベース用のデータ行を準備"""
        analysis = result['analysis']
        sources = result['sources']
        
        data_row = {
            '年度': int(result['year']),
            '総設問数': len(analysis.get('questions', [])),
            '総文字数': analysis.get('total_characters', 0),
            '大問数': len(analysis.get('sections', [])),
            '処理日時': result['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'ファイル数': result['file_count']
        }
        
        # 各大問のデータ
        for i, section in enumerate(analysis.get('sections', []), 1):
            # ジャンルとテーマを判定
            genre, theme = self.determine_genre_and_theme(section.get('text', ''))
            
            # 出典情報を取得
            source = next((s for s in sources if s.get('section') == i), {})
            
            data_row[f'大問{i}_ジャンル'] = genre
            data_row[f'大問{i}_テーマ'] = theme
            data_row[f'大問{i}_著者'] = source.get('author', '不明')
            data_row[f'大問{i}_作品'] = source.get('title', '不明')
            data_row[f'大問{i}_設問数'] = section.get('question_count', 0)
            data_row[f'大問{i}_文字数'] = len(section.get('text', ''))
            
        # 設問タイプ別集計
        for q_type, count in analysis.get('question_types', {}).items():
            data_row[f'{q_type}_問題数'] = count
            
        return data_row
        
    def determine_genre_and_theme(self, text: str) -> Tuple[str, str]:
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
        
    def generate_summary_report(self):
        """処理結果のサマリーレポートを生成"""
        report_filename = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("入試問題分析 バッチ処理レポート\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"処理日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"処理対象: {self.stats['total_files']}件\n")
            f.write(f"成功: {self.stats['processed']}件\n")
            f.write(f"失敗: {self.stats['failed']}件\n")
            f.write(f"成功率: {self.stats['processed'] / self.stats['total_files'] * 100:.1f}%\n\n")
            
            f.write("【学校別処理件数】\n")
            for school, count in sorted(self.stats['schools'].items()):
                f.write(f"  {school}: {count}件\n")
                
            f.write("\n【年度別処理件数】\n")
            for year, count in sorted(self.stats['years'].items()):
                f.write(f"  {year}年: {count}件\n")
                
            if self.errors:
                f.write("\n【エラー詳細】\n")
                for error in self.errors:
                    f.write(f"\nフォルダ: {error['folder']}\n")
                    f.write(f"学校: {error['school_name']}\n")
                    f.write(f"年度: {error['year']}\n")
                    f.write(f"エラー: {error['error']}\n")
                    f.write("-" * 40 + "\n")
                    
        return report_filename
        
    def run_batch_processing(self, target_dir: Path = None, parallel: bool = True, max_workers: int = 4):
        """バッチ処理を実行"""
        print("🚀 バッチ処理を開始します...\n")
        
        # ファイルをスキャン
        file_groups = self.scan_directories(target_dir)
        
        if not file_groups:
            print("❌ 処理対象のファイルが見つかりませんでした")
            return
            
        print(f"📊 {len(file_groups)}個のグループが見つかりました\n")
        
        # 処理を実行
        if parallel:
            print(f"⚡ 並列処理モード（最大{max_workers}ワーカー）\n")
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for i, file_group in enumerate(file_groups, 1):
                    future = executor.submit(self.process_file_group, file_group)
                    futures.append((i, file_group, future))
                    
                for i, file_group, future in futures:
                    try:
                        result = future.result(timeout=60)  # 1分でタイムアウト
                        self.results.append(result)
                        
                        status = "✅" if result['status'] == 'success' else "❌"
                        print(f"{status} [{i}/{len(file_groups)}] {result['school_name']} {result['year']}年")
                        
                    except concurrent.futures.TimeoutError:
                        print(f"⏱️  [{i}/{len(file_groups)}] タイムアウト: {file_group['folder']}")
                        self.stats['failed'] += 1
                    except Exception as e:
                        print(f"❌ [{i}/{len(file_groups)}] エラー: {str(e)}")
                        self.stats['failed'] += 1
        else:
            print("🔄 逐次処理モード\n")
            for i, file_group in enumerate(file_groups, 1):
                result = self.process_file_group(file_group)
                self.results.append(result)
                
                status = "✅" if result['status'] == 'success' else "❌"
                print(f"{status} [{i}/{len(file_groups)}] {result.get('school_name', '不明')} {result.get('year', '不明')}年")
                
        # データベースに保存
        if self.results:
            print("\n💾 データベースに保存中...")
            self.save_to_database(self.results)
            
        # サマリーレポートを生成
        print("\n📄 レポートを生成中...")
        report_file = self.generate_summary_report()
        
        # 完了メッセージ
        print("\n" + "=" * 60)
        print("✅ バッチ処理が完了しました！")
        print("=" * 60)
        print(f"処理件数: {self.stats['processed']}/{self.stats['total_files']}")
        print(f"エラー件数: {self.stats['failed']}")
        print(f"データベース: entrance_exam_database.xlsx")
        print(f"レポート: {report_file}")
        print("=" * 60)


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='入試問題テキスト分析 バッチ処理')
    parser.add_argument('--dir', type=str, help='処理対象ディレクトリ（デフォルト: BunkoOCR結果フォルダ）')
    parser.add_argument('--sequential', action='store_true', help='逐次処理モード（デフォルト: 並列処理）')
    parser.add_argument('--workers', type=int, default=4, help='並列処理時のワーカー数（デフォルト: 4）')
    parser.add_argument('--kakomon', action='store_true', help='過去問フォルダを処理対象にする')
    
    args = parser.parse_args()
    
    # バッチアナライザーを初期化
    analyzer = BatchAnalyzer()
    
    # 処理対象ディレクトリを決定
    if args.dir:
        target_dir = Path(args.dir)
    elif args.kakomon:
        target_dir = analyzer.kakomon_dir
    else:
        target_dir = None  # デフォルト（BunkoOCR結果フォルダ）
        
    # バッチ処理を実行
    analyzer.run_batch_processing(
        target_dir=target_dir,
        parallel=not args.sequential,
        max_workers=args.workers
    )


if __name__ == "__main__":
    main()