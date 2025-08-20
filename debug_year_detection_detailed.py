#!/usr/bin/env python3
"""
年度検出の詳細デバッグスクリプト
"""

import re
import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector

def debug_kanji_conversion():
    """漢数字変換のデバッグ"""
    detector = YearDetector()
    
    test_cases = [
        "二〇二五年度",
        "二〇二五",
        "一九九八年",
        "二〇二四年度",
        "２０２５年度"
    ]
    
    print("=== 漢数字変換テスト ===")
    for test_string in test_cases:
        print(f"\n入力: '{test_string}'")
        result = detector._kanji_year_to_year(test_string)
        print(f"結果: '{result}'")
    
    print("\n=== 正規表現マッチテスト ===")
    pattern = r'([一二三四五六七八九〇０-９]{4})年度?'
    compiled_pattern = re.compile(pattern)
    
    test_text = """=== ページ 1 ===
二〇二五年度
第一回入学試験問題
国
語"""
    
    print(f"テストテキスト:\n{repr(test_text)}")
    print(f"正規表現パターン: {pattern}")
    
    matches = list(compiled_pattern.finditer(test_text))
    print(f"\nマッチ数: {len(matches)}")
    
    for i, match in enumerate(matches):
        print(f"マッチ {i+1}:")
        print(f"  全体: '{match.group(0)}'")
        print(f"  グループ1: '{match.group(1)}'")
        print(f"  位置: {match.start()}-{match.end()}")
        
        # 変換テスト
        converted = detector._kanji_year_to_year(match.group(1))
        print(f"  変換結果: '{converted}'")

def debug_full_detection():
    """完全な年度検出のデバッグ"""
    detector = YearDetector()
    
    test_text = """=== ページ 1 ===
二〇二五年度
第一回入学試験問題
国
語"""
    
    print("\n=== 完全な年度検出テスト ===")
    print(f"入力テキスト:\n{test_text}")
    
    try:
        result = detector.detect_years(test_text)
        print(f"\n検出成功!")
        print(f"検出された年度: {result.years}")
        print(f"信頼度: {result.confidence}")
        print(f"検出パターン: {result.detection_patterns}")
    except Exception as e:
        print(f"\nエラー発生: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        
        # 詳細なデバッグ情報
        print("\n=== 詳細デバッグ ===")
        for pattern_obj in detector.patterns:
            if pattern_obj.name == "year_kanji":
                print(f"漢数字パターンでのマッチ確認:")
                matches = pattern_obj.compiled.findall(test_text)
                print(f"  findall結果: {matches}")
                
                matches_iter = list(pattern_obj.compiled.finditer(test_text))
                print(f"  finditer結果数: {len(matches_iter)}")
                
                for match in matches_iter:
                    print(f"    マッチ: '{match.group(1)}'")
                    try:
                        converted = detector._kanji_year_to_year(match.group(1))
                        print(f"    変換: '{converted}'")
                        is_valid = detector._is_valid_year(converted)
                        print(f"    有効: {is_valid}")
                    except Exception as conv_error:
                        print(f"    変換エラー: {conv_error}")

if __name__ == "__main__":
    print("年度検出の詳細デバッグを開始します\n")
    
    debug_kanji_conversion()
    debug_full_detection()
    
    print("\n=== 手動テスト ===")
    detector = YearDetector()
    test_input = "二〇二五"
    print(f"手動変換テスト: '{test_input}'")
    result = detector._kanji_year_to_year(test_input)
    print(f"変換結果: '{result}'")
    
    # 文字ごとの変換確認
    print("\n文字ごとの変換:")
    for char in test_input:
        print(f"'{char}' -> ?")