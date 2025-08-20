#!/usr/bin/env python3
"""
正確なエラーの再現スクリプト
"""

import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector
from exceptions import YearDetectionError

def test_exact_error():
    """エラーメッセージにあるテキストでテスト"""
    # エラーメッセージから抽出したサンプルテキスト
    error_sample = "'=== ページ 1 ===\n二〇二五年度\n第一回入学試験問題\n国\n語"
    
    print("=== 正確なエラーの再現テスト ===")
    print(f"エラーメッセージのサンプル: {repr(error_sample)}")
    
    detector = YearDetector()
    
    try:
        result = detector.detect_years(error_sample)
        print(f"✅ 年度検出成功: {result.years}")
        print(f"信頼度: {result.confidence}")
        print(f"パターン: {result.detection_patterns}")
    except YearDetectionError as e:
        print(f"❌ YearDetectionError: {e}")
        print(f"サンプルテキスト: '{e.text_sample}'")
        print(f"試行パターン: {e.patterns_tried}")
        
        # デバッグ情報
        print("\n=== デバッグ情報 ===")
        detected_years = {}
        
        for pattern_obj in detector.patterns:
            print(f"\nパターン: {pattern_obj.name}")
            print(f"正規表現: {pattern_obj.pattern}")
            
            matches = list(pattern_obj.compiled.finditer(error_sample))
            print(f"マッチ数: {len(matches)}")
            
            for match in matches:
                print(f"  マッチ: '{match.group(0)}'")
                print(f"  グループ1: '{match.group(1)}'")
                try:
                    converted = pattern_obj.converter(match.group(1))
                    print(f"  変換結果: '{converted}'")
                    is_valid = detector._is_valid_year(converted)
                    print(f"  有効性: {is_valid}")
                    
                    if is_valid:
                        detected_years[converted] = match.start()
                        
                except Exception as conv_error:
                    print(f"  変換エラー: {conv_error}")
        
        print(f"\n検出された年度辞書: {detected_years}")
        
    except Exception as e:
        print(f"❌ その他のエラー: {type(e).__name__}: {e}")

def test_variations():
    """様々なバリエーションでテスト"""
    print("\n=== バリエーションテスト ===")
    
    test_texts = [
        "二〇二五年度",
        "=== ページ 1 ===\n二〇二五年度",
        "'=== ページ 1 ===\n二〇二五年度\n第一回入学試験問題\n国\n語",
        "=== ページ 1 ===\n二〇二五年度\n第一回入学試験問題\n国\n語",
    ]
    
    detector = YearDetector()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nテスト {i}: {repr(text[:50])}...")
        try:
            result = detector.detect_years(text)
            print(f"✅ 成功: {result.years}")
        except YearDetectionError as e:
            print(f"❌ 失敗: {e}")
        except Exception as e:
            print(f"❌ エラー: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_exact_error()
    test_variations()