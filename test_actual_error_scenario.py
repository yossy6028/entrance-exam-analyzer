#!/usr/bin/env python3
"""
実際のエラーシナリオのテスト
"""

import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector
from exceptions import YearDetectionError

def test_problematic_scenarios():
    """問題のあるシナリオのテスト"""
    print("=== 問題のあるシナリオのテスト ===")
    
    # 実際にはエラーを出しそうなケース（ただし、今は修正されているはず）
    problematic_cases = [
        # 制御文字を含むケース
        "\x00=== ページ 1 ===\n二〇二五年度",
        
        # エンコーディング問題をシミュレート
        "ăšĂă[…ページ 1 …\n二〇二五年度",
        
        # 年度が全く含まれないケース
        "入学試験問題\n国語\n第一問",
        
        # 非常に短いテキスト
        "二",
        
        # 空テキスト
        "",
        
        # 間違った年度（有効範囲外）
        "昭和五十年度",
        
        # 複雑な漢数字（今は対応していない）
        "千九百九十五年度",
    ]
    
    detector = YearDetector()
    
    for i, test_text in enumerate(problematic_cases, 1):
        print(f"\n--- 問題ケース {i} ---")
        print(f"テキスト: {repr(test_text)}")
        
        try:
            result = detector.detect_years(test_text)
            print(f"✅ 成功: {result.years}")
            print(f"信頼度: {result.confidence:.2f}")
        except YearDetectionError as e:
            print(f"❌ YearDetectionError (これは期待される動作):")
            # エラーメッセージが短くなるように最初の部分だけ表示
            error_lines = str(e).split('\n')
            for line in error_lines[:5]:  # 最初の5行だけ表示
                print(f"  {line}")
            if len(error_lines) > 5:
                print(f"  ... (他 {len(error_lines) - 5} 行)")
        except Exception as e:
            print(f"❌ 予期しないエラー: {type(e).__name__}: {e}")

def test_edge_cases():
    """エッジケースのテスト"""
    print("\n=== エッジケースのテスト ===")
    
    edge_cases = [
        # 複数の年度が混在
        "平成27年度と令和3年度の比較",
        
        # 年度以外の数字が多い
        "2025年4月1日入学試験 問題数: 50問 制限時間: 90分",
        
        # 似たパターンだが年度ではない
        "第25回入学試験",
        
        # 正規表現が誤マッチしそうなケース
        "25年前の出来事について述べよ",
    ]
    
    detector = YearDetector()
    
    for i, test_text in enumerate(edge_cases, 1):
        print(f"\n--- エッジケース {i} ---")
        print(f"テキスト: {repr(test_text)}")
        
        try:
            result = detector.detect_years(test_text)
            print(f"✅ 成功: {result.years}")
            print(f"信頼度: {result.confidence:.2f}")
            print(f"パターン: {list(result.detection_patterns.keys())}")
        except YearDetectionError as e:
            print(f"❌ YearDetectionError:")
            print(f"  {str(e).split(chr(10))[0]}...")  # 最初の行のみ
        except Exception as e:
            print(f"❌ 予期しないエラー: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_problematic_scenarios()
    test_edge_cases()