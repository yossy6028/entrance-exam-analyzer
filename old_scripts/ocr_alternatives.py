#!/usr/bin/env python3
"""
bunkoOCRの技術構造分析と代替実装案
"""

def analyze_bunko_ocr_technology():
    """bunkoOCRの技術スタックを分析"""
    
    print("=== bunkoOCR 技術分析 ===\n")
    
    print("【確認されたコンポーネント】")
    print("1. Core MLモデル:")
    print("   - TextDetector.mlmodelc: テキスト領域の検出")
    print("   - CodeDecoder.mlmodelc: 文字認識デコーダー")
    print("   - TransformerEncoder/Decoder: Transformerベースの高精度認識")
    print()
    print("2. フォント:")
    print("   - ipaexm.ttf: IPA明朝フォント（日本語表示用）")
    print()
    print("3. アプリ情報:")
    print("   - Bundle ID: info.lithium03.bunkoOCR")
    print("   - Version: 3.14")
    print("   - URLスキーム: bunkoOCR://")
    
    print("\n【技術的特徴】")
    print("- Transformerベースの最新OCR技術を使用")
    print("- 縦書き日本語に特化した学習モデル")
    print("- ローカル処理（プライバシー重視）")
    print("- iCloud統合で結果を自動保存")


def propose_alternatives():
    """代替実装案を提示"""
    
    print("\n=== 代替実装案 ===\n")
    
    print("【案1: Vision Framework + Core ML】")
    print("```python")
    print("import Vision  # macOS/iOS Vision Framework")
    print("import CoreML")
    print("")
    print("# Appleの日本語OCRモデルを使用")
    print("request = VNRecognizeTextRequest()")
    print("request.recognitionLanguages = ['ja-JP']")
    print("request.recognitionLevel = .accurate")
    print("request.usesLanguageCorrection = True")
    print("```")
    
    print("\n【案2: Tesseract + 日本語縦書き学習モデル】")
    print("```bash")
    print("# インストール")
    print("brew install tesseract")
    print("brew install tesseract-lang  # 日本語データ")
    print("")
    print("# 縦書き用の追加設定")
    print("tesseract input.png output -l jpn_vert --psm 5")
    print("```")
    
    print("\n【案3: Google Cloud Vision API + 前処理】")
    print("```python")
    print("# 画像の前処理で精度向上")
    print("def preprocess_for_vertical_text(image):")
    print("    # 1. 画像を90度回転")
    print("    rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)")
    print("    # 2. コントラスト強調")
    print("    enhanced = cv2.convertScaleAbs(rotated, alpha=1.5, beta=0)")
    print("    # 3. ノイズ除去")
    print("    denoised = cv2.fastNlMeansDenoising(enhanced)")
    print("    return denoised")
    print("```")
    
    print("\n【案4: オープンソースOCRモデルの活用】")
    print("1. manga-ocr (GitHub)")
    print("   - 日本語縦書きに特化")
    print("   - Transformerベース")
    print("   ```bash")
    print("   pip install manga-ocr")
    print("   ```")
    print()
    print("2. EasyOCR")
    print("   - 多言語対応")
    print("   - GPUサポート")
    print("   ```python")
    print("   import easyocr")
    print("   reader = easyocr.Reader(['ja'])")
    print("   result = reader.readtext('image.png')")
    print("   ```")


def create_ocr_pipeline():
    """高精度OCRパイプラインの提案"""
    
    print("\n=== 高精度OCRパイプライン実装案 ===\n")
    
    print("""
import cv2
import numpy as np
from PIL import Image
import pytesseract
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

class AdvancedJapaneseOCR:
    '''高精度日本語OCRパイプライン'''
    
    def __init__(self):
        # Transformerベースのモデルを使用
        self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
        self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
        
    def preprocess_image(self, image_path):
        '''画像前処理'''
        img = cv2.imread(image_path)
        
        # グレースケール変換
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 適応的二値化
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # ノイズ除去
        denoised = cv2.medianBlur(binary, 3)
        
        # 傾き補正
        coords = np.column_stack(np.where(denoised > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        
        (h, w) = denoised.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(denoised, M, (w, h), 
                               flags=cv2.INTER_CUBIC, 
                               borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def detect_text_regions(self, image):
        '''テキスト領域検出'''
        # 縦書き検出用の処理
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        dilated = cv2.dilate(image, kernel, iterations=3)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, 
                                      cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h > w * 2:  # 縦長の領域を優先
                regions.append((x, y, w, h))
        
        return sorted(regions, key=lambda r: r[0], reverse=True)  # 右から左へ
    
    def recognize_text(self, image_region):
        '''テキスト認識'''
        # PIL画像に変換
        pil_image = Image.fromarray(image_region)
        
        # Transformerモデルで認識
        pixel_values = self.processor(images=pil_image, return_tensors="pt").pixel_values
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return generated_text
    
    def process_pdf(self, pdf_path):
        '''PDFを処理して高精度OCR実行'''
        # PDF→画像変換
        from pdf2image import convert_from_path
        pages = convert_from_path(pdf_path, dpi=300)
        
        all_text = []
        for i, page in enumerate(pages):
            # numpy配列に変換
            img = np.array(page)
            
            # 前処理
            processed = self.preprocess_image(img)
            
            # テキスト領域検出
            regions = self.detect_text_regions(processed)
            
            # 各領域を認識
            page_text = []
            for x, y, w, h in regions:
                region = processed[y:y+h, x:x+w]
                text = self.recognize_text(region)
                page_text.append(text)
            
            all_text.append('\\n'.join(page_text))
        
        return '\\n\\n'.join(all_text)
""")
    
    print("\n【実装のポイント】")
    print("1. 画像前処理で品質向上")
    print("2. 縦書きテキスト領域の検出")
    print("3. Transformerベースの高精度認識")
    print("4. 右から左への読み順序対応")


def main():
    """メイン実行"""
    
    analyze_bunko_ocr_technology()
    propose_alternatives()
    create_ocr_pipeline()
    
    print("\n【推奨アプローチ】")
    print("1. 短期的: bunkoOCRを手動で使用し、結果を自動取得")
    print("2. 中期的: manga-ocrなどの既存ツールを活用")
    print("3. 長期的: 独自の高精度OCRパイプラインを構築")
    
    print("\n【bunkoOCRとの連携】")
    print("- URLスキーム経由での起動: bunkoOCR://")
    print("- iCloud経由での結果取得")
    print("- AppleScriptでの自動化も可能")


if __name__ == "__main__":
    main()