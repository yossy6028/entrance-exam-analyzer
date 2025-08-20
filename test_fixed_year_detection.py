#!/usr/bin/env python3
"""
修正済み年度検出器のテストスクリプト
"""

import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector

def test_fixed_detector():
    """修正済み年度検出器のテスト"""
    print("=== 修正済み年度検出器のテスト ===\n")
    
    detector = YearDetector()
    
    test_cases = [
        {
            'name': '聖光学院タイプ（複数年度誤検出）',
            'text': """聖光学院中学校
二〇二五年度入学試験問題

【歴史問題】
1. 平成15年に制定された法律について述べよ。
2. 西暦2000年に起きた出来事を説明せよ。

【参考資料】 
・創立記念: 2000年設立
・第15回記念行事開催
・令和7年度入学生募集要項

【試験概要】
実施年度: 二〇二五年度
試験科目: 国語・数学・社会・理科
""",
            'expected': ['2025']
        },
        {
            'name': '歴史問題が多い場合',
            'text': """2025年度入学試験問題（歴史）
1. 平成15年に制定された個人情報保護法について
2. 昭和39年の東京オリンピック開催について  
3. 西暦2000年のIT革命について
4. 1995年に起きた阪神淡路大震災について
""",
            'expected': ['2025']
        },
        {
            'name': '創立記念の年号がある場合',
            'text': """令和7年度入学試験問題
本校は創立記念: 2000年設立の伝統校です。
平成15年に校舎を建設しました。
""",
            'expected': ['2025']
        },
        {
            'name': '単純な年度（従来通り動作すべき）',
            'text': """二〇二五年度入学試験問題
数学・国語・理科・社会
""",
            'expected': ['2025']
        },
        {
            'name': '複数の有効な年度（年度範囲）',
            'text': """2024年度・2025年度合同入学試験問題
両年度の受験生が対象です。
""",
            'expected': ['2024', '2025']  # これは複数年度が正しい
        }
    ]
    
    for test_case in test_cases:
        print(f"【{test_case['name']}】")
        print(f"入力テキスト: {repr(test_case['text'][:100])}")
        
        try:
            result = detector.detect_years(test_case['text'])
            print(f"検出年度: {result.years}")
            print(f"信頼度: {result.confidence:.2f}")
            print(f"検出パターン: {list(result.detection_patterns.keys())}")
            print(f"期待値: {test_case['expected']}")
            
            is_correct = result.years == test_case['expected']
            print(f"結果: {'✓ 正しい' if is_correct else '✗ 不正確'}")
            
            if not is_correct:
                print(f"  詳細パターン: {result.detection_patterns}")
                
        except Exception as e:
            print(f"エラー: {e}")
        
        print("-" * 60)

def test_specific_patterns():
    """特定の問題パターンをテスト"""
    print("\n=== 特定パターンのテスト ===\n")
    
    detector = YearDetector()
    
    patterns = [
        ("平成15年に制定", "歴史的事実"),
        ("西暦2000年の出来事", "歴史的事実"),
        ("創立記念: 2000年", "設立年"),
        ("二〇二五年度入学試験", "試験年度"),
        ("令和7年度生募集", "募集年度"),
        ("2025年度合格者発表", "試験年度"),
    ]
    
    for pattern_text, description in patterns:
        try:
            result = detector.detect_years(pattern_text)
            print(f"{description}: '{pattern_text}'")
            print(f"  -> 検出: {result.years}, 信頼度: {result.confidence:.2f}")
        except:
            print(f"{description}: '{pattern_text}' -> 検出失敗")

if __name__ == "__main__":
    test_fixed_detector()
    test_specific_patterns()