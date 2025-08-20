#!/usr/bin/env python3
"""
複数の入試問題テキストファイルを一括分析してExcelに保存
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor
from modules.flexible_excel_formatter import FlexibleExcelFormatter

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchAnalyzer:
    """複数の入試問題を一括分析するクラス"""
    
    def __init__(self, excel_path: str = None):
        """
        初期化
        
        Args:
            excel_path: 出力先のExcelファイルパス（Noneの場合はデフォルトパスを使用）
        """
        # デフォルトの出力先を設定
        if excel_path is None:
            excel_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database.xlsx"
            
        self.excel_path = excel_path
        self.extractor = FinalContentExtractor()
        self.formatter = FlexibleExcelFormatter(excel_path)
        self.results = []
        
    def extract_school_year_from_filename(self, filename: str) -> Tuple[str, int]:
        """
        ファイル名から学校名と年度を抽出
        
        Args:
            filename: ファイル名（例: 25開成.txt, 2025桜蔭.txt）
            
        Returns:
            (学校名, 年度)のタプル
        """
        # 拡張子を除去
        name = Path(filename).stem
        
        # パターン1: 数字2桁+学校名 (例: 25開成)
        match1 = re.match(r'^(\d{2})(.+)$', name)
        if match1:
            year = 2000 + int(match1.group(1))
            school = match1.group(2)
            return (school + "中学校", year)
        
        # パターン2: 4桁年度+学校名 (例: 2025開成)
        match2 = re.match(r'^(\d{4})(.+)$', name)
        if match2:
            year = int(match2.group(1))
            school = match2.group(2)
            return (school + "中学校", year)
        
        # パターン3: 学校名+年度 (例: 開成25, 開成2025)
        match3 = re.match(r'^(.+?)(\d{2,4})$', name)
        if match3:
            school = match3.group(1)
            year_str = match3.group(2)
            if len(year_str) == 2:
                year = 2000 + int(year_str)
            else:
                year = int(year_str)
            return (school + "中学校", year)
        
        # デフォルト
        return (name + "中学校", 2025)
    
    def analyze_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        単一ファイルを分析
        
        Args:
            file_path: 分析するファイルのパス
            
        Returns:
            分析結果の辞書
        """
        logger.info(f"分析開始: {file_path}")
        
        # ファイル名から学校名と年度を抽出
        filename = os.path.basename(file_path)
        school_name, year = self.extract_school_year_from_filename(filename)
        
        # テキストを読み込み
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {file_path} - {e}")
            return None
        
        # 内容を抽出
        result = self.extractor.extract_all_content(text)
        
        # 基本情報
        analysis_data = {
            'file_path': file_path,
            'filename': filename,
            'school_name': school_name,
            'year': year,
            'total_characters': result['total_characters'],
            'total_questions': result['total_questions'],
            'sections': result['sections'],
            'question_types': result['question_types']
        }
        
        # 選択肢数の分析
        choice_counts = self._analyze_choice_counts(text)
        analysis_data['choice_counts'] = choice_counts
        
        # 記述問題の字数分析
        description_limits = self._analyze_description_limits(text)
        analysis_data['description_limits'] = description_limits
        
        logger.info(f"分析完了: {school_name} {year}年 - {len(result['sections'])}大問, {result['total_questions']}設問")
        
        return analysis_data
    
    def _analyze_choice_counts(self, text: str) -> Dict[str, int]:
        """
        選択肢数を分析
        
        Args:
            text: 問題文テキスト
            
        Returns:
            選択肢数の集計辞書
        """
        counts = {
            '3択': 0,
            '4択': 0,
            '5択': 0,
            '6択': 0,
            '複数選択': 0
        }
        
        # 選択肢パターンを検索
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # 問題文を検出
            if re.search(r'問[一二三四五六七八九十0-9]', line):
                # 次の10行をチェック
                check_lines = lines[i:min(i+15, len(lines))]
                check_text = '\n'.join(check_lines)
                
                # 選択肢を数える
                if 'ア' in check_text and 'イ' in check_text:
                    if 'カ' in check_text:
                        if '二つ選' in check_text or '２つ選' in check_text:
                            counts['複数選択'] += 1
                        else:
                            counts['6択'] += 1
                    elif 'オ' in check_text:
                        counts['5択'] += 1
                    elif 'エ' in check_text:
                        counts['4択'] += 1
                    elif 'ウ' in check_text:
                        counts['3択'] += 1
        
        return counts
    
    def _analyze_description_limits(self, text: str) -> Dict[str, Any]:
        """
        記述問題の字数制限を分析
        
        Args:
            text: 問題文テキスト
            
        Returns:
            字数制限の分析結果
        """
        limits = {
            'min': None,
            'max': None,
            'all_limits': []
        }
        
        # 字数指定パターン
        patterns = [
            r'(\d+)字以上(\d+)字以内',
            r'(\d+)字〜(\d+)字',
            r'(\d+)字程度',
            r'(\d+)字で',
            r'(\d+)字以内'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        # 範囲指定
                        limits['all_limits'].append((int(match[0]), int(match[1])))
                    else:
                        # 単一指定
                        num = int(match[0]) if isinstance(match[0], str) else int(match)
                        limits['all_limits'].append(num)
                else:
                    num = int(match)
                    limits['all_limits'].append(num)
        
        # 最小・最大を計算
        if limits['all_limits']:
            flat_limits = []
            for limit in limits['all_limits']:
                if isinstance(limit, tuple):
                    flat_limits.extend(limit)
                else:
                    flat_limits.append(limit)
            
            if flat_limits:
                limits['min'] = min(flat_limits)
                limits['max'] = max(flat_limits)
        
        return limits
    
    def analyze_folder(self, folder_path: str, pattern: str = "*.txt") -> List[Dict[str, Any]]:
        """
        フォルダ内の複数ファイルを分析
        
        Args:
            folder_path: 分析するフォルダのパス
            pattern: ファイルパターン（デフォルト: *.txt）
            
        Returns:
            分析結果のリスト
        """
        folder = Path(folder_path)
        if not folder.exists():
            logger.error(f"フォルダが存在しません: {folder_path}")
            return []
        
        # 対象ファイルを取得
        files = list(folder.glob(pattern))
        logger.info(f"{len(files)}個のファイルを検出")
        
        # 各ファイルを分析
        results = []
        for file_path in files:
            result = self.analyze_single_file(str(file_path))
            if result:
                results.append(result)
                self.results.append(result)
        
        return results
    
    def save_to_excel(self, results: List[Dict[str, Any]] = None) -> bool:
        """
        分析結果をExcelに保存
        
        Args:
            results: 保存する分析結果のリスト（省略時は内部の結果を使用）
            
        Returns:
            成功した場合True
        """
        if results is None:
            results = self.results
        
        if not results:
            logger.warning("保存するデータがありません")
            return False
        
        success_count = 0
        failed_count = 0
        
        for result in results:
            try:
                # 分析結果を整形
                analysis_result = {
                    'total_characters': result['total_characters'],
                    'total_questions': result['total_questions'],
                    'sections': result['sections'],
                    'question_types': result['question_types']
                }
                
                # 追加情報
                additional_info = {
                    'OCRファイル名': result['filename'],
                    '選択_3択': result['choice_counts'].get('3択', 0),
                    '選択_4択': result['choice_counts'].get('4択', 0),
                    '選択_5択': result['choice_counts'].get('5択', 0),
                    '選択_6択': result['choice_counts'].get('6択', 0),
                    '選択_複数選択': result['choice_counts'].get('複数選択', 0),
                }
                
                # 記述字数制限
                if result['description_limits']['min']:
                    additional_info['記述_最小字数'] = result['description_limits']['min']
                if result['description_limits']['max']:
                    additional_info['記述_最大字数'] = result['description_limits']['max']
                
                # データを整形
                row_data = self.formatter.format_analysis_data(
                    school_name=result['school_name'],
                    year=result['year'],
                    analysis_result=analysis_result,
                    ocr_filename=result['filename'],
                    additional_info=additional_info
                )
                
                # Excelに保存
                success = self.formatter.save_to_excel(
                    school_name=result['school_name'],
                    row_data=row_data,
                    backup=(success_count == 0)  # 最初だけバックアップ
                )
                
                if success:
                    success_count += 1
                    logger.info(f"保存成功: {result['school_name']} {result['year']}年")
                else:
                    failed_count += 1
                    logger.error(f"保存失敗: {result['school_name']} {result['year']}年")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"エラー: {result.get('school_name', '不明')} - {e}")
        
        logger.info(f"保存完了: 成功 {success_count}件, 失敗 {failed_count}件")
        return failed_count == 0
    
    def print_summary(self):
        """分析結果のサマリーを表示"""
        if not self.results:
            print("分析結果がありません")
            return
        
        print("\n" + "="*80)
        print("【一括分析結果サマリー】")
        print("="*80)
        
        print(f"\n分析ファイル数: {len(self.results)}件")
        
        # 学校別に整理
        schools = {}
        for result in self.results:
            school = result['school_name']
            if school not in schools:
                schools[school] = []
            schools[school].append(result)
        
        print(f"学校数: {len(schools)}校")
        
        # 各学校の詳細
        for school_name in sorted(schools.keys()):
            school_results = schools[school_name]
            print(f"\n【{school_name}】")
            
            for result in sorted(school_results, key=lambda x: x['year']):
                print(f"  {result['year']}年:")
                print(f"    - 文字数: {result['total_characters']:,}文字")
                print(f"    - 大問数: {len(result['sections'])}問")
                print(f"    - 総設問数: {result['total_questions']}問")
                
                # 選択肢数の情報
                choices = result['choice_counts']
                choice_info = []
                for choice_type, count in choices.items():
                    if count > 0:
                        choice_info.append(f"{choice_type}:{count}問")
                if choice_info:
                    print(f"    - 選択問題: {', '.join(choice_info)}")
        
        print("\n" + "="*80)


def main():
    """メイン処理"""
    import argparse
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description='入試問題テキストファイルを一括分析してExcelに保存'
    )
    parser.add_argument(
        'folder',
        help='分析するフォルダのパス'
    )
    parser.add_argument(
        '--pattern',
        default='*.txt',
        help='ファイルパターン（デフォルト: *.txt）'
    )
    parser.add_argument(
        '--output',
        default='/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database.xlsx',
        help='出力Excelファイル（デフォルト: /Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database.xlsx）'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Excelに保存しない（分析のみ）'
    )
    
    args = parser.parse_args()
    
    # アナライザーを初期化
    analyzer = BatchAnalyzer(args.output)
    
    # フォルダを分析
    print(f"フォルダを分析中: {args.folder}")
    print(f"パターン: {args.pattern}")
    
    results = analyzer.analyze_folder(args.folder, args.pattern)
    
    if not results:
        print("分析可能なファイルが見つかりませんでした")
        return
    
    # サマリーを表示
    analyzer.print_summary()
    
    # Excelに保存
    if not args.no_save:
        print(f"\nExcelファイルに保存中: {args.output}")
        success = analyzer.save_to_excel()
        if success:
            print("✅ 保存完了")
        else:
            print("⚠️ 一部のファイルの保存に失敗しました")


if __name__ == "__main__":
    # 引数がない場合はサンプル実行
    if len(sys.argv) == 1:
        print("使用方法:")
        print("  python batch_analyzer.py <フォルダパス> [オプション]")
        print("\n例:")
        print('  python batch_analyzer.py "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"')
        print('  python batch_analyzer.py "./texts" --pattern "25*.txt"')
        print('  python batch_analyzer.py "./texts" --output "results.xlsx"')
        print('  python batch_analyzer.py "./texts" --no-save  # 分析のみ')
    else:
        main()