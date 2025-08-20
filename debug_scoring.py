#!/usr/bin/env python3
"""
年度スコアリングのデバッグ
"""

import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector

def debug_scoring():
    """年度スコアリングのデバッグ"""
    print("=== 年度スコアリングのデバッグ ===\n")
    
    detector = YearDetector()
    
    test_text = """令和7年度入学試験問題
本校は創立記念: 2000年設立の伝統校です。
平成15年に校舎を建設しました。
"""
    
    print(f"テストテキスト:\n{test_text}")
    print("-" * 50)
    
    # 年度検出実行
    result = detector.detect_years(test_text)
    print(f"検出結果: {result.years}")
    print(f"検出パターン: {result.detection_patterns}")
    
    # 内部ロジックを再現して年度を取得
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
                        
            except (ValueError, IndexError):
                continue
    
    years = sorted(detected_years.keys())
    print(f"検出された年度: {years}")
    
    # 主要年度選択をテスト
    primary_year = detector._select_primary_year(test_text, years, detection_patterns)
    print(f"主要年度選択結果: {primary_year}")
    
    # 各年度のスコアリング詳細を表示
    print(f"\n=== 年度スコアリング詳細 ===")
    
    for year in years:
        score = 0
        print(f"\n年度 {year} のスコア計算:")
        
        # 文書位置によるスコア
        for pattern_name, matches in detection_patterns.items():
            for pos, detected_year in matches:
                if detected_year == year:
                    pos_score = 0
                    if pos < 50:
                        pos_score = 10
                        print(f"  文書冒頭 (位置 {pos}): +10")
                    elif pos < 200:
                        pos_score = 5
                        print(f"  文書前半 (位置 {pos}): +5")
                    score += pos_score
                    
                    # パターンタイプによるスコア
                    pattern_score = 0
                    if pattern_name in ['year_kanji', 'reiwa']:
                        pattern_score = 5
                        print(f"  明確な年度パターン ({pattern_name}): +5")
                    elif pattern_name == 'year_4digit':
                        pattern_score = 3
                        print(f"  4桁年度パターン: +3")
                    elif pattern_name == 'heisei':
                        pattern_score = -2
                        print(f"  平成年号（歴史的可能性）: -2")
                    score += pattern_score
        
        # 年度による調整
        try:
            year_num = int(year)
            year_score = 0
            if year_num >= 2020:
                year_score = 5
                print(f"  最近の年度 ({year_num}): +5")
            elif year_num < 2010:
                year_score = -5
                print(f"  古い年度 ({year_num}): -5")
            score += year_score
        except:
            pass
        
        # 歴史的文脈による減点
        import re
        historical_context_patterns = [
            r'創立.*?' + re.escape(year) + r'年',
            re.escape(year) + r'年設立',
            r'平成\d{1,2}年に.*?建設',
            r'昭和\d{1,2}年に.*?建設',
        ]
        
        for hist_pattern in historical_context_patterns:
            if re.search(hist_pattern, test_text):
                score -= 8
                print(f"  歴史的文脈パターン '{hist_pattern}': -8")
        
        print(f"  最終スコア: {score}")

if __name__ == "__main__":
    debug_scoring()