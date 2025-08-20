"""
DotsOCRを使用したPDF処理モジュール
既存のPDFOCRProcessorと互換性のあるインターフェースを提供
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import json

from .dots_ocr_handler import DotsOCRHandler
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class DotsOCRPDFProcessor:
    """DotsOCRを使用したPDF処理クラス"""
    
    def __init__(self, model_path: Optional[str] = None, use_gpu: bool = True, dpi: int = 300):
        """
        初期化
        
        Args:
            model_path: DotsOCRモデルのパス
            use_gpu: GPUを使用するか
            dpi: PDF変換時の解像度（互換性のため）
        """
        self.dots_ocr = DotsOCRHandler(
            model_path=model_path or "./weights/DotsOCR",
            use_gpu=use_gpu
        )
        self.pdf_processor = PDFProcessor(dpi=dpi)
        self.dpi = dpi
        
    def process_pdf(self, pdf_path: Path, 
                   save_images: bool = False,
                   output_dir: Optional[Path] = None,
                   use_cli: bool = True) -> Dict[str, Any]:
        """
        PDFファイルをDotsOCRで処理してテキストと構造を抽出
        
        Args:
            pdf_path: PDFファイルのパス
            save_images: 変換した画像を保存するか（互換性のため）
            output_dir: 画像保存先ディレクトリ（save_images=Trueの場合）
            use_cli: CLIインターフェースを使用するか
            
        Returns:
            OCR結果の辞書（既存フォーマットと互換）
        """
        try:
            logger.info(f"DotsOCR PDF処理開始: {pdf_path}")
            
            if use_cli:
                # CLIインターフェースを使用（推奨）
                result = self.dots_ocr.process_pdf(pdf_path, num_threads=4)
            else:
                # Pythonインターフェースを使用（ページごとに処理）
                result = self._process_pdf_with_python_api(pdf_path, save_images, output_dir)
                
            # 既存フォーマットに変換
            compatible_result = self._convert_to_compatible_format(result)
            
            return compatible_result
            
        except Exception as e:
            logger.error(f"DotsOCR PDF処理エラー: {e}")
            # フォールバック: 従来のOCR処理を試みる
            logger.info("DotsOCRが利用できないため、代替処理を試みます")
            raise
            
    def _process_pdf_with_python_api(self, pdf_path: Path, 
                                    save_images: bool,
                                    output_dir: Optional[Path]) -> Dict[str, Any]:
        """
        PythonインターフェースでPDFを処理（ページごと）
        
        Args:
            pdf_path: PDFファイルのパス
            save_images: 画像を保存するか
            output_dir: 画像保存先
            
        Returns:
            処理結果
        """
        # PDFを画像に変換
        images = self.pdf_processor.convert_pdf_to_images(pdf_path)
        
        # 画像を保存（オプション）
        if save_images and output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            for i, image in enumerate(images, 1):
                image_path = output_dir / f"page_{i:03d}.png"
                image.save(image_path)
                logger.info(f"画像を保存: {image_path}")
                
        # 各ページを処理
        results = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'total_pages': len(images),
            'pages': [],
            'full_text': '',
            'layout_elements': []
        }
        
        all_text = []
        
        for i, image in enumerate(images, 1):
            logger.info(f"ページ {i}/{len(images)} を処理中...")
            
            # 画像の前処理
            processed_image = self.pdf_processor.preprocess_image(image)
            
            # DotsOCRで処理
            page_result = self.dots_ocr.process_image(processed_image)
            
            # ページ結果を保存
            page_info = {
                'page_number': i,
                'text': page_result.get('text', ''),
                'layout_elements': page_result.get('layout_elements', []),
                'confidence': 0.95,  # DotsOCRは信頼度を直接提供しないため固定値
                'is_vertical': self._detect_vertical_text(page_result.get('text', ''))
            }
            
            results['pages'].append(page_info)
            all_text.append(page_info['text'])
            results['layout_elements'].extend(page_info['layout_elements'])
            
        results['full_text'] = '\n\n'.join(all_text)
        
        # 入試問題の構造を検出
        results['exam_structure'] = self.dots_ocr._extract_exam_structure(results)
        
        return results
        
    def _convert_to_compatible_format(self, dots_result: Dict) -> Dict[str, Any]:
        """
        DotsOCRの結果を既存フォーマットに変換
        
        Args:
            dots_result: DotsOCRの結果
            
        Returns:
            互換フォーマットの結果
        """
        compatible = {
            'file_path': dots_result.get('file_path', ''),
            'file_name': dots_result.get('file_name', ''),
            'total_pages': dots_result.get('total_pages', 0),
            'pages': [],
            'full_text': dots_result.get('full_text', '')
        }
        
        # ページ情報を変換
        for page in dots_result.get('pages', []):
            compatible_page = {
                'page_number': page.get('page_number', len(compatible['pages']) + 1),
                'text': page.get('text', ''),
                'confidence': 0.95,  # 固定値
                'is_vertical': self._detect_vertical_text(page.get('text', ''))
            }
            compatible['pages'].append(compatible_page)
            
        # レイアウト情報を追加（拡張情報として）
        compatible['layout_elements'] = dots_result.get('layout_elements', [])
        compatible['exam_structure'] = dots_result.get('exam_structure', {})
        
        return compatible
        
    def _detect_vertical_text(self, text: str) -> bool:
        """
        テキストが縦書きかどうかを検出
        
        Args:
            text: テキスト
            
        Returns:
            縦書きの場合True
        """
        # 簡易的な縦書き検出
        # 実際の実装では、レイアウト情報から判断する方が正確
        vertical_indicators = ['。', '、', '「', '」', '『', '』']
        horizontal_indicators = ['.', ',', '(', ')']
        
        vertical_count = sum(1 for char in vertical_indicators if char in text)
        horizontal_count = sum(1 for char in horizontal_indicators if char in text)
        
        return vertical_count > horizontal_count * 2
        
    def detect_exam_structure(self, text: str) -> Dict[str, Any]:
        """
        入試問題の構造を検出（互換性メソッド）
        
        Args:
            text: 抽出されたテキスト
            
        Returns:
            構造情報
        """
        # DotsOCRの結果から構造を抽出
        temp_result = {'full_text': text, 'layout_elements': []}
        return self.dots_ocr._extract_exam_structure(temp_result)
        
    def process_with_fallback(self, pdf_path: Path) -> Dict[str, Any]:
        """
        DotsOCRを試み、失敗した場合は従来のOCRにフォールバック
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            OCR結果
        """
        try:
            # まずDotsOCRを試みる
            return self.process_pdf(pdf_path, use_cli=True)
        except Exception as e:
            logger.warning(f"DotsOCR処理失敗: {e}")
            
            try:
                # Pythonインターフェースでリトライ
                return self.process_pdf(pdf_path, use_cli=False)
            except Exception as e2:
                logger.error(f"DotsOCR Pythonインターフェースも失敗: {e2}")
                
                # 従来のGoogle Cloud Vision APIにフォールバック
                logger.info("Google Cloud Vision APIにフォールバックします")
                from .pdf_ocr_processor import PDFOCRProcessor
                fallback_processor = PDFOCRProcessor()
                return fallback_processor.process_pdf(pdf_path)