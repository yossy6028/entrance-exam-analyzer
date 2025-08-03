#!/usr/bin/env python3
"""
渋谷教育学園渋谷中学校 15年度 国語問題分析
"""
import os
import sys
sys.path.append('.')

from modules.pdf_processor import PDFProcessor
from modules.text_analyzer import TextAnalyzer
from extract_sources import extract_source_info
import re
from typing import Dict, List


def analyze_shibuya_15():
    """渋渋15年度の分析を実行"""
    
    pdf_path = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf'
    
    print("=== 渋谷教育学園渋谷中学校 15年度 国語問題分析 ===\n")
    
    # 1. PDFからOCRでテキスト抽出
    print("1. PDFからテキストを抽出中...")
    try:
        processor = PDFProcessor()
        pages = processor.extract_text_from_pdf(pdf_path)
        
        # 全ページのテキストを結合
        full_text = "\n".join([page['text'] for page in pages])
        
        # OCRテキストをファイルに保存（デバッグ用）
        ocr_output_path = 'shibuya_15_ocr.txt'
        with open(ocr_output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"   OCRテキストを {ocr_output_path} に保存しました")
        print(f"   総文字数: {len(full_text)}文字")
        
    except Exception as e:
        print(f"   エラー: {e}")
        return
    
    # 2. テキスト分析
    print("\n2. 問題構造を分析中...")
    analyzer = TextAnalyzer()
    result = analyzer.analyze_exam_structure(full_text)
    
    print(f"   検出された大問数: {len(result['sections'])}個")
    print(f"   検出された設問数: {result['total_questions']}問")
    
    # 3. 大問の詳細表示
    print("\n3. 大問別内訳:")
    for section in result['sections']:
        print(f"\n   大問{section['number']}: {section.get('type', '不明')}")
        print(f"   設問数: {section['question_count']}問")
        
        # この大問の設問を表示
        questions = [q for q in result['questions'] if q['section'] == section['number']]
        for q in questions:
            print(f"     {q['marker']}: {q['type']}")
    
    # 4. 出典情報を抽出
    print("\n4. 出典情報を抽出中...")
    source_result = extract_source_info(full_text)
    
    if source_result['sources']:
        print("\n   【検出された出典】")
        for source in source_result['sources']:
            print(f"\n   大問{source['section']}:")
            print(f"   著者: {source['author']}")
            if source.get('title'):
                print(f"   作品: 「{source['title']}」")
            if source.get('book'):
                print(f"   書籍: 『{source['book']}』")
    else:
        print("   出典情報が検出できませんでした")
        
        # デバッグ: 出典パターンを探す
        print("\n   【デバッグ情報】")
        patterns = [
            r'（[^）]+）',  # 括弧内のすべて
            r'「[^」]+」',  # 鉤括弧内のタイトル
            r'『[^』]+』'   # 二重鉤括弧内の書籍名
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, full_text)[:10]  # 最初の10個
            if matches:
                print(f"\n   パターン {pattern} で見つかった候補:")
                for match in matches:
                    print(f"     - {match}")
    
    # 5. 精度評価
    print("\n5. 精度評価:")
    
    # 渋渋の典型的な構成と比較
    expected_questions = 10  # 渋渋は通常10問前後
    accuracy = min(result['total_questions'] / expected_questions * 100, 100)
    
    print(f"   期待値: 約{expected_questions}問")
    print(f"   検出数: {result['total_questions']}問")
    print(f"   推定精度: {accuracy:.1f}%")
    
    if accuracy < 80:
        print("\n   ⚠️ 精度が低い可能性があります。")
        print("   対策:")
        print("   1. 高精度OCRツール（bunkoOCR等）でテキストファイルを作成")
        print("   2. 縦書きPDFの場合は特に精度が低下します")
    
    return result


if __name__ == "__main__":
    analyze_shibuya_15()