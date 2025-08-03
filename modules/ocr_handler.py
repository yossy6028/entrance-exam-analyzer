"""
OCR処理モジュール
Google Cloud Vision APIを使用してテキスト抽出を行う
"""
import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from google.cloud import vision
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRHandler:
    """Google Cloud Vision APIを使用したOCR処理クラス"""
    
    def __init__(self, credentials_path: str = None):
        """
        初期化
        
        Args:
            credentials_path: サービスアカウントキーのパス（省略可）
        """
        # Application Default Credentials (ADC) を使用
        # gcloud auth application-default login で設定された認証情報を自動的に使用
        self.client = vision.ImageAnnotatorClient()
            
    def extract_text_from_image(self, image: Image.Image, 
                              language_hints: List[str] = ['ja']) -> Dict[str, Any]:
        """
        画像からテキストを抽出
        
        Args:
            image: PIL Image
            language_hints: 言語ヒント
            
        Returns:
            OCR結果の辞書
        """
        # PIL ImageをGoogle Vision API用のバイト列に変換
        byte_io = io.BytesIO()
        image.save(byte_io, format='PNG')
        content = byte_io.getvalue()
        
        # Vision APIのImageオブジェクトを作成
        vision_image = vision.Image(content=content)
        
        # OCR実行（DOCUMENT_TEXT_DETECTIONで高精度な文書解析）
        image_context = vision.ImageContext(language_hints=language_hints)
        
        try:
            response = self.client.document_text_detection(
                image=vision_image,
                image_context=image_context
            )
            
            if response.error.message:
                raise Exception(f"OCRエラー: {response.error.message}")
                
            return self._parse_ocr_response(response)
            
        except Exception as e:
            logger.error(f"OCR処理エラー: {e}")
            raise
            
    def _parse_ocr_response(self, response) -> Dict[str, Any]:
        """
        OCRレスポンスを解析
        
        Args:
            response: Google Vision APIのレスポンス
            
        Returns:
            解析結果の辞書
        """
        result = {
            'full_text': '',
            'pages': [],
            'blocks': [],
            'paragraphs': [],
            'words': [],
            'symbols': []
        }
        
        # 全文テキスト
        if response.text_annotations:
            result['full_text'] = response.text_annotations[0].description
            
        # 詳細な構造解析
        if response.full_text_annotation:
            annotation = response.full_text_annotation
            
            for page in annotation.pages:
                page_info = {
                    'page_number': len(result['pages']) + 1,
                    'width': page.width,
                    'height': page.height,
                    'blocks': []
                }
                
                for block in page.blocks:
                    block_info = {
                        'type': block.block_type,
                        'confidence': block.confidence,
                        'bounding_box': self._get_bounding_box(block.bounding_box),
                        'paragraphs': []
                    }
                    
                    for paragraph in block.paragraphs:
                        para_info = {
                            'confidence': paragraph.confidence,
                            'bounding_box': self._get_bounding_box(paragraph.bounding_box),
                            'text': self._get_text_from_paragraph(paragraph)
                        }
                        block_info['paragraphs'].append(para_info)
                        result['paragraphs'].append(para_info)
                        
                    page_info['blocks'].append(block_info)
                    result['blocks'].append(block_info)
                    
                result['pages'].append(page_info)
                
        return result
        
    def _get_bounding_box(self, bounding_poly) -> Dict[str, int]:
        """
        境界ボックスの座標を取得
        
        Args:
            bounding_poly: Google Vision APIのBoundingPoly
            
        Returns:
            座標の辞書
        """
        vertices = bounding_poly.vertices
        return {
            'x_min': min(v.x for v in vertices),
            'y_min': min(v.y for v in vertices),
            'x_max': max(v.x for v in vertices),
            'y_max': max(v.y for v in vertices)
        }
        
    def _get_text_from_paragraph(self, paragraph) -> str:
        """
        段落からテキストを抽出
        
        Args:
            paragraph: Google Vision APIのParagraph
            
        Returns:
            段落のテキスト
        """
        text = ''
        for word in paragraph.words:
            for symbol in word.symbols:
                text += symbol.text
                if hasattr(symbol.property, 'detected_break'):
                    break_type = symbol.property.detected_break.type_
                    if break_type in [1, 3]:  # SPACE or LINE_BREAK
                        text += ' '
                    elif break_type == 5:  # EOL_SURE_SPACE
                        text += '\n'
        return text.strip()
        
    def detect_vertical_text(self, ocr_result: Dict[str, Any]) -> bool:
        """
        縦書きテキストかどうかを検出
        
        Args:
            ocr_result: OCR結果
            
        Returns:
            縦書きの場合True
        """
        # ブロックの配置から縦書きを判定
        if not ocr_result['blocks']:
            return False
            
        # 最初のいくつかのブロックの位置関係から判定
        blocks = ocr_result['blocks'][:10]  # 最初の10ブロック
        
        vertical_count = 0
        horizontal_count = 0
        
        for i in range(len(blocks) - 1):
            curr_box = blocks[i]['bounding_box']
            next_box = blocks[i + 1]['bounding_box']
            
            # X座標の差とY座標の差を比較
            x_diff = abs(next_box['x_min'] - curr_box['x_min'])
            y_diff = abs(next_box['y_min'] - curr_box['y_min'])
            
            if x_diff > y_diff:
                horizontal_count += 1
            else:
                vertical_count += 1
                
        return vertical_count > horizontal_count