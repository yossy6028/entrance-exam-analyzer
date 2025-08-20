#!/usr/bin/env python3
"""
創立記念ケースの詳細デバッグ
"""

import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector

def debug_creation_case():
    """創立記念ケースの詳細デバッグ"""
    print("=== 創立記念ケースの詳細デバッグ ===\n")
    
    detector = YearDetector()
    
    test_text = """令和7年度入学試験問題
本校は創立記念: 2000年設立の伝統校です。
平成15年に校舎を建設しました。
"""
    
    print(f"テストテキスト:\n{test_text}")
    print("-" * 50)
    
    # 年度検出実行
    result = detector.detect_years(test_text)
    print(f"最終検出結果: {result.years}")
    print(f"信頼度: {result.confidence:.2f}")
    print(f"検出パターン: {result.detection_patterns}")
    
    # 内部ロジックを再現
    detected_years = {}
    detection_patterns = {}
    
    print(f"\n=== パターンマッチの詳細 ===")
    
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
                        
                        # 文脈分析
                        context_start = max(0, position - 20)
                        context_end = min(len(test_text), position + 30)
                        context = test_text[context_start:context_end].replace('\n', '\\n')
                        print(f"    文脈: ...{context}...")
                        
            except (ValueError, IndexError):
                continue
    
    print(f"\nフィルタリング前: {detected_years}")
    
    # 歴史的文脈フィルタリングをテスト
    filtered_years = detector._filter_historical_contexts(test_text, detected_years, detection_patterns)
    print(f"フィルタリング後: {filtered_years}")
    
    # どの年度が除外されたかの詳細
    removed_years = set(detected_years.keys()) - set(filtered_years.keys())
    if removed_years:
        print(f"除外された年度: {removed_years}")
        
        # 除外理由を分析
        print(f"\n=== 除外理由の分析 ===")
        for year in removed_years:
            print(f"年度 {year} の除外理由:")
            
            # 歴史的パターンマッチを確認
            import re
            historical_patterns = [
                r'平成\d{1,2}年[にで]',
                r'昭和\d{1,2}年[にで]',
                r'西暦\d{4}年[のに]',
                r'\d{4}年[のに]起[きこ]',
                r'\d{4}年[のに]制定',
                r'創立[記念]*[:\s]*\d{4}年',
                r'\d{4}年[のに][設建]',
                r'\d{4}年[のに].*?事[件変]',
            ]
            
            for pattern in historical_patterns:
                matches = list(re.finditer(pattern, test_text))
                for match in matches:
                    if year in match.group(0):
                        print(f"  歴史的パターン '{pattern}' でマッチ: '{match.group(0)}'")
    
    # 強い年度パターンの分析
    print(f"\n=== 強い年度パターンの分析 ===")
    for pattern_name, matches in detection_patterns.items():
        for pos, year in matches:
            is_strong_pattern = pattern_name in ['year_kanji', 'reiwa', 'year_4digit']
            is_front = pos < 50
            
            # 試験関連語彙との近接性チェック
            context_start = max(0, pos - 30)
            context_end = min(len(test_text), pos + 50)
            context = test_text[context_start:context_end]
            has_test_keywords = any(keyword in context for keyword in ['入学試験', '年度', '試験問題', '合格', '募集'])
            
            print(f"年度 {year} (位置 {pos}):")
            print(f"  パターン: {pattern_name}")
            print(f"  強いパターン: {is_strong_pattern}")
            print(f"  文書前半: {is_front}")
            print(f"  試験キーワード: {has_test_keywords}")
            print(f"  文脈: '{context.replace(chr(10), ' ')}'")
            print(f"  -> 強い年度: {is_strong_pattern and (is_front or has_test_keywords)}")

if __name__ == "__main__":
    debug_creation_case()