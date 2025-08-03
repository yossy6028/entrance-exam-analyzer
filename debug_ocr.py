#!/usr/bin/env python3
"""
OCR結果を確認するためのデバッグスクリプト
"""
import sys
import os
sys.path.append('.')

from modules.pdf_processor import PDFProcessor
from modules.ocr_handler import OCRHandler
from pathlib import Path

# 環境変数を確認
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not creds_path:
    print('Google Cloud認証情報が設定されていません')
    sys.exit(1)

# PDFのパス
pdf_path = Path('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭/15桜蔭.pdf')

# モジュールの初期化
pdf_processor = PDFProcessor(dpi=300)
ocr_handler = OCRHandler(creds_path)

# PDFを画像に変換
print('PDFを画像に変換中...')
images = pdf_processor.convert_pdf_to_images(pdf_path)
print(f'{len(images)}ページを処理します')

# 全ページのOCR結果を保存
all_text = ""

# OCR実行
for i, image in enumerate(images):
    print(f'\nページ {i+1} を処理中...')
    processed_image = pdf_processor.preprocess_image(image)
    ocr_result = ocr_handler.extract_text_from_image(processed_image)
    
    page_text = ocr_result['full_text']
    all_text += f"\n\n=== ページ {i+1} ===\n" + page_text
    
    # 最初の500文字を表示
    print(f"最初の500文字:")
    print(page_text[:500])
    print("...")

# 全テキストをファイルに保存
output_path = Path('ocr_output.txt')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(all_text)

print(f"\n全OCR結果を {output_path} に保存しました")

# 設問パターンを検索
print("\n=== 設問パターンの検索 ===")
import re

# 大問のパターン
section_patterns = [
    r'第[一二三四五六七八九十]+問',
    r'[一二三四五六七八九十]\s*[、。．]',
    r'[１２３４５６７８９]+\s*[、。．]',
]

for pattern in section_patterns:
    matches = re.findall(pattern, all_text)
    if matches:
        print(f"パターン '{pattern}' のマッチ: {matches[:5]}...")

# 小問のパターン
question_patterns = [
    r'問[０-９0-9]+',
    r'[（(][０-９0-9]+[）)]',
    r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]',
]

for pattern in question_patterns:
    matches = re.findall(pattern, all_text)
    if matches:
        print(f"パターン '{pattern}' のマッチ: {matches[:10]}...")