"""
Google Vision APIの精度を最大化するための設定
"""
from typing import Dict, Any
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImprovedOCRConfig:
    """OCR精度向上のための設定と前処理"""
    
    @staticmethod
    def get_optimized_vision_config() -> Dict[str, Any]:
        """最適化されたGoogle Vision API設定を取得"""
        return {
            "features": [
                {
                    "type": "DOCUMENT_TEXT_DETECTION",  # 文書用OCR（より構造的）
                    "maxResults": 1
                }
            ],
            "imageContext": {
                "languageHints": ["ja"],  # 日本語を明示的に指定
                "textDetectionParams": {
                    "enableTextDetectionConfidenceScore": True  # 信頼度スコアを有効化
                }
            }
        }
    
    @staticmethod
    def preprocess_image_for_ocr(image_path: str) -> np.ndarray:
        """OCR精度向上のための画像前処理"""
        # 画像を読み込み
        image = cv2.imread(image_path)
        
        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 2. 画像の拡大（3倍）
        height, width = denoised.shape[:2]
        enlarged = cv2.resize(denoised, (width * 3, height * 3), 
                             interpolation=cv2.INTER_CUBIC)
        
        # 3. 適応的閾値処理
        adaptive_thresh = cv2.adaptiveThreshold(
            enlarged, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 4. 歪み補正（de-skewing）
        coords = np.column_stack(np.where(adaptive_thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle
            
        if angle != 0:
            (h, w) = adaptive_thresh.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            adaptive_thresh = cv2.warpAffine(
                adaptive_thresh, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
        
        # 5. シャープ化
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(adaptive_thresh, -1, kernel)
        
        return sharpened
    
    @staticmethod
    def enhance_image_with_pil(image_path: str) -> Image:
        """PILを使用した画像強調"""
        img = Image.open(image_path)
        
        # コントラスト強調
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # シャープネス強調
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # エッジ強調フィルタ
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return img
    
    @staticmethod
    def post_process_ocr_result(text: str) -> str:
        """OCR結果の後処理（誤認識の修正）"""
        # よくある誤認識パターンの修正
        corrections = {
            '間一': '問一',
            '間二': '問二', 
            '間三': '問三',
            '間四': '問四',
            '間五': '問五',
            '間六': '問六',
            '問ー': '問一',  # 長音記号の誤認識
            '問二': '問二',  # 全角数字への統一
            '問3': '問三',
            '問4': '問四',
            '問5': '問五',
            '問6': '問六',
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    @staticmethod
    def analyze_confidence_scores(ocr_result: Dict) -> Dict[str, float]:
        """信頼度スコアを分析して低信頼度の文字を特定"""
        low_confidence_chars = []
        
        # Google Vision APIの結果から信頼度を抽出
        if 'textAnnotations' in ocr_result:
            for annotation in ocr_result['textAnnotations'][1:]:  # 最初は全文なのでスキップ
                if 'confidence' in annotation:
                    confidence = annotation['confidence']
                    if confidence < 0.8:  # 80%未満は低信頼度
                        low_confidence_chars.append({
                            'text': annotation['description'],
                            'confidence': confidence,
                            'vertices': annotation['boundingPoly']['vertices']
                        })
        
        return low_confidence_chars


# 使用例
if __name__ == "__main__":
    config = ImprovedOCRConfig()
    
    # 最適化された設定を取得
    vision_config = config.get_optimized_vision_config()
    print("最適化されたVision API設定:")
    print(vision_config)
    
    # OCR結果の後処理例
    sample_text = "間一 -Aについて、「たまたま撮影した1枚のスナップ」がなぜ3年"
    corrected_text = config.post_process_ocr_result(sample_text)
    print(f"\n修正前: {sample_text}")
    print(f"修正後: {corrected_text}")