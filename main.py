#!/usr/bin/env python3
"""
国語入試問題分析システム
メインプログラム
"""
import os
import sys
import logging
import argparse
import re
from pathlib import Path
from tqdm import tqdm

# プロジェクトのモジュールをインポート
from config import *
from modules.pdf_processor import PDFProcessor
from modules.ocr_handler import OCRHandler
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EntranceExamAnalyzer:
    """入試問題分析システムのメインクラス"""
    
    def __init__(self, credentials_path: str = None):
        """
        初期化
        
        Args:
            credentials_path: Google Cloud認証情報のパス
        """
        self.pdf_processor = PDFProcessor(dpi=IMAGE_DPI)
        self.ocr_handler = OCRHandler(credentials_path)
        self.text_analyzer = TextAnalyzer(QUESTION_PATTERNS)
        self.pattern_extractor = PatternExtractor(SOURCE_PATTERNS)
        self.excel_writer = ExcelWriter(OUTPUT_DIR)
        
    def analyze_exam(self, exam_pdf_path: Path, answer_pdf_path: Path = None,
                    school_name: str = None, year: str = None) -> Path:
        """
        入試問題を分析
        
        Args:
            exam_pdf_path: 問題PDFのパス
            answer_pdf_path: 解答用紙PDFのパス（オプション）
            school_name: 学校名
            year: 年度
            
        Returns:
            分析結果のExcelファイルパス
        """
        logger.info(f"分析開始: {exam_pdf_path}")
        
        # 学校名と年度の推定
        if not school_name or not year:
            # ファイル名から学校名と年度を抽出
            filename = exam_pdf_path.stem  # 拡張子を除いたファイル名
            
            # 年度の抽出（4桁の数字を探す）
            year_match = re.search(r'(\d{4})', filename)
            if year_match and not year:
                year = year_match.group(1)
            elif not year:
                # 2桁の年度表記（例：15開成）
                year_match = re.search(r'^(\d{2})', filename)
                if year_match:
                    # 2000年代か1900年代かを推定
                    two_digit = int(year_match.group(1))
                    if two_digit > 50:
                        year = f"19{year_match.group(1)}"
                    else:
                        year = f"20{year_match.group(1)}"
            
            # 学校名の抽出
            if not school_name:
                # パターン1: 「学校名」を含む（例：麻布中学校）
                school_match = re.search(r'([^_\d]+(?:中学校|中学|中等部|学園|学院))', filename)
                if school_match:
                    school_name = school_match.group(1)
                else:
                    # パターン2: 年度の後の文字列（例：15開成 → 開成）
                    school_match = re.search(r'^\d+(.+?)(?:\.pdf)?$', filename)
                    if school_match:
                        school_name = school_match.group(1).strip()
                        # 一般的な学校名の補完
                        if school_name and not any(suffix in school_name for suffix in ['中学校', '中学', '中等部', '学園', '学院']):
                            school_name = f"{school_name}中学校"
                    else:
                        # パターン3: 最初の単語
                        parts = filename.split('_')
                        if parts:
                            school_name = parts[0]
            
        # 問題用紙の処理
        logger.info("問題用紙の処理を開始")
        exam_result = self._process_pdf(exam_pdf_path, is_answer_sheet=False)
        
        # 解答用紙の処理（存在する場合）
        answer_result = None
        if answer_pdf_path and answer_pdf_path.exists():
            logger.info("解答用紙の処理を開始")
            answer_result = self._process_pdf(answer_pdf_path, is_answer_sheet=True)
            exam_result['answer_sheet_info'] = answer_result
            
        # 結果をExcelに出力
        output_path = self.excel_writer.write_analysis_results(
            exam_result, school_name, year
        )
        
        logger.info(f"分析完了: {output_path}")
        return output_path
        
    def _process_pdf(self, pdf_path: Path, is_answer_sheet: bool = False) -> dict:
        """
        PDFファイルを処理
        
        Args:
            pdf_path: PDFファイルのパス
            is_answer_sheet: 解答用紙かどうか
            
        Returns:
            処理結果の辞書
        """
        # PDFを画像に変換
        images = self.pdf_processor.convert_pdf_to_images(pdf_path)
        
        # 全ページのテキストを結合
        all_text = ""
        ocr_results = []
        
        logger.info(f"OCR処理を開始（{len(images)}ページ）")
        for i, image in enumerate(tqdm(images, desc="OCR処理")):
            # 画像の前処理
            processed_image = self.pdf_processor.preprocess_image(image)
            
            # OCR実行
            ocr_result = self.ocr_handler.extract_text_from_image(processed_image)
            ocr_results.append(ocr_result)
            all_text += ocr_result['full_text'] + "\n"
            
        if is_answer_sheet:
            # 解答用紙の分析
            logger.info("解答用紙の分析を実行")
            return self.pattern_extractor.extract_answer_sheet_info(all_text)
        else:
            # 問題用紙の分析
            logger.info("問題構造の分析を実行")
            
            # テキスト分析
            analysis_result = self.text_analyzer.analyze_exam_structure(all_text)
            
            # 各設問の詳細情報を追加
            for question in analysis_result['questions']:
                # 選択肢数の抽出
                choice_count = self.pattern_extractor.extract_choice_count(
                    question['text']
                )
                if choice_count:
                    question['choice_count'] = choice_count
                    
                # 文字数制限の抽出
                char_limit = self.pattern_extractor.extract_character_limit(
                    question['text']
                )
                if char_limit:
                    question['character_limit'] = char_limit
                    
            # 各大問の出典情報を抽出
            for section in analysis_result['sections']:
                source_info = self.pattern_extractor.extract_source_info(
                    section['text']
                )
                section['source_info'] = source_info
                
            return analysis_result
            
    def batch_analyze(self, input_dir: Path, output_summary: bool = True):
        """
        複数のPDFファイルをバッチ処理
        
        Args:
            input_dir: 入力ディレクトリ
            output_summary: サマリーファイルを出力するか
        """
        pdf_files = list(input_dir.glob("*.pdf"))
        exam_files = [f for f in pdf_files if '解答' not in f.name]
        
        logger.info(f"{len(exam_files)}個の問題ファイルを処理します")
        
        results = []
        for exam_file in tqdm(exam_files, desc="バッチ処理"):
            # 対応する解答用紙を探す
            answer_file = None
            base_name = exam_file.stem.replace('問題', '')
            for pdf in pdf_files:
                if '解答' in pdf.name and base_name in pdf.name:
                    answer_file = pdf
                    break
                    
            try:
                output_path = self.analyze_exam(exam_file, answer_file)
                results.append({
                    'file': exam_file.name,
                    'output': output_path,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"処理エラー: {exam_file.name} - {e}")
                results.append({
                    'file': exam_file.name,
                    'error': str(e),
                    'status': 'error'
                })
                
        logger.info(f"バッチ処理完了: {len(results)}ファイル")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='国語入試問題分析システム'
    )
    parser.add_argument(
        'input_path',
        type=Path,
        help='分析対象のPDFファイルまたはディレクトリ'
    )
    parser.add_argument(
        '--answer',
        type=Path,
        help='解答用紙のPDFファイル'
    )
    parser.add_argument(
        '--school',
        type=str,
        help='学校名'
    )
    parser.add_argument(
        '--year',
        type=str,
        help='年度'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        default=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        help='Google Cloud認証情報のパス'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='バッチ処理モード'
    )
    
    args = parser.parse_args()
    
    # 認証情報の確認
    if not args.credentials:
        logger.error("Google Cloud認証情報が設定されていません")
        logger.error("環境変数GOOGLE_APPLICATION_CREDENTIALSを設定するか、--credentialsオプションを使用してください")
        sys.exit(1)
        
    # アナライザーの初期化
    analyzer = EntranceExamAnalyzer(credentials_path=args.credentials)
    
    # 処理の実行
    if args.batch or args.input_path.is_dir():
        # バッチ処理
        analyzer.batch_analyze(args.input_path)
    else:
        # 単一ファイル処理
        if not args.input_path.exists():
            logger.error(f"ファイルが見つかりません: {args.input_path}")
            sys.exit(1)
            
        analyzer.analyze_exam(
            args.input_path,
            args.answer,
            args.school,
            args.year
        )


if __name__ == '__main__':
    main()