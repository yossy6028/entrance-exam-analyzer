#!/usr/bin/env python3
"""
歴史的文脈フィルタリング機能のデバッグ
"""

import re
import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector

def debug_historical_filtering():
    """歴史的文脈フィルタリングのデバッグ"""
    print("=== 歴史的文脈フィルタリングのデバッグ ===\n")
    
    detector = YearDetector()
    
    test_text = """2025年度入学試験問題（歴史）
1. 平成15年に制定された個人情報保護法について
2. 昭和39年の東京オリンピック開催について  
3. 西暦2000年のIT革命について
4. 1995年に起きた阪神淡路大震災について
"""
    
    print(f"テストテキスト:\n{test_text}")
    print("-" * 50)
    
    # まず通常の年度検出を実行
    result = detector.detect_years(test_text)
    print(f"通常の検出結果: {result.years}")
    print(f"検出パターン: {result.detection_patterns}")
    
    # detected_years と patterns を取得するために内部ロジックを再現
    detected_years = {}
    detection_patterns = {}
    
    for pattern_obj in sorted(detector.patterns, key=lambda x: x.priority, reverse=True):
        matches = pattern_obj.compiled.finditer(test_text)
        
        for match in matches:
            try:
                year = pattern_obj.converter(match.group(1))
                if detector._is_valid_year(year):
                    position = match.start()
                    
                    if not detector._is_duplicate(year, position, detected_years, detection_patterns):
                        detected_years[year] = position
                        
                        if pattern_obj.name not in detection_patterns:
                            detection_patterns[pattern_obj.name] = []
                        detection_patterns[pattern_obj.name].append((position, year))
                        
                        print(f"検出: {pattern_obj.name} -> '{match.group(0)}' -> {year} (位置: {position})")
                        
            except (ValueError, IndexError):
                continue
    
    print(f"\n検出された年度: {detected_years}")
    print(f"検出パターン: {detection_patterns}")
    
    # 歴史的文脈フィルタリングをテスト
    print(f"\n=== 歴史的文脈フィルタリングの実行 ===")
    
    filtered_years = detector._filter_historical_contexts(test_text, detected_years, detection_patterns)
    print(f"フィルタリング前: {detected_years}")
    print(f"フィルタリング後: {filtered_years}")
    
    # 歴史的パターンのマッチを詳細確認
    print(f"\n=== 歴史的パターンのマッチ確認 ===")
    
    historical_patterns = [
        r'[平成昭和]\d{1,2}年[にで]',     # 平成15年に、昭和60年で
        r'西暦\d{4}年[のに]',            # 西暦2000年の、西暦1995年に  
        r'\d{4}年[のに]起[きこ]',        # 2000年に起きた
        r'\d{4}年[のに]制定',           # 2000年に制定された
        r'創立[記念]*[:\s]*\d{4}年',    # 創立記念: 2000年
        r'\d{4}年[のに][設建]',         # 2000年に設立、1995年に建設
        r'\d{4}年[のに].*事[件変]',      # 2000年に起きた事件
    ]
    
    for pattern in historical_patterns:
        matches = list(re.finditer(pattern, test_text))
        if matches:
            print(f"パターン '{pattern}':")
            for match in matches:
                print(f"  マッチ: '{match.group(0)}' (位置: {match.start()})")
                
                # 年度抽出
                year_match = re.search(r'\d{4}', match.group(0))
                if year_match:
                    historical_year = year_match.group(0)
                    print(f"    抽出年度: {historical_year}")
                    print(f"    検出年度に含まれる: {historical_year in detected_years}")
                    
                # 平成年号の処理
                heisei_match = re.search(r'平成(\d{1,2})年', match.group(0))
                if heisei_match:
                    heisei_year = str(1988 + int(heisei_match.group(1)))
                    print(f"    平成->西暦: {heisei_year}")
                    print(f"    検出年度に含まれる: {heisei_year in detected_years}")

def test_pattern_positions():
    """検出位置と強い年度パターンの判定をテスト"""
    print(f"\n=== 検出位置と強い年度パターンの判定テスト ===")
    
    detector = YearDetector()
    
    test_text = """2025年度入学試験問題（歴史）
1. 平成15年に制定された個人情報保護法について
2. 西暦2000年のIT革命について
"""
    
    result = detector.detect_years(test_text)
    
    print(f"テストテキスト: {repr(test_text)}")
    print(f"検出パターン詳細:")
    
    for pattern_name, matches in result.detection_patterns.items():
        print(f"  {pattern_name}:")
        for pos, year in matches:
            print(f"    位置{pos}: {year}")
            
            # 強い年度パターンかどうかの判定
            is_strong = pattern_name in ['year_kanji', 'reiwa', 'year_4digit']
            is_front = pos < 200
            
            print(f"      強いパターン: {is_strong}")
            print(f"      文書前半: {is_front}")
            print(f"      強い年度: {is_strong and is_front}")

if __name__ == "__main__":
    debug_historical_filtering()
    test_pattern_positions()