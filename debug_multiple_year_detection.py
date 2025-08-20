#!/usr/bin/env python3
"""
複数年度誤検出の根本原因分析スクリプト
2000, 2015, 2025が同時検出される問題を詳細調査
"""

import re
import sys
import os
from pathlib import Path

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector
from config.settings import Settings

def analyze_multiple_year_detection():
    """複数年度検出の詳細分析"""
    print("=== 複数年度誤検出の根本原因分析 ===\n")
    
    detector = YearDetector()
    
    # 2000, 2015, 2025が同時検出されるようなテキストを作成
    problematic_text = """聖光学院中学校
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
"""
    
    print("分析対象テキスト:")
    print("=" * 50)
    print(problematic_text)
    print("=" * 50)
    
    # 年度検出を実行
    try:
        result = detector.detect_years(problematic_text)
        print(f"\n検出結果:")
        print(f"検出年度: {result.years}")
        print(f"信頼度: {result.confidence:.2f}")
        print(f"検出パターン詳細:")
        
        for pattern_name, matches in result.detection_patterns.items():
            print(f"  {pattern_name}: {matches}")
            
        # 複数年度が検出された場合の詳細分析
        if len(result.years) > 1:
            print(f"\n⚠️ 複数年度が検出されました: {result.years}")
            detailed_pattern_analysis(detector, problematic_text)
            
    except Exception as e:
        print(f"エラー: {e}")

def detailed_pattern_analysis(detector, text):
    """各パターンでのマッチを詳細分析"""
    print(f"\n【パターン別詳細分析】")
    
    detected_positions = {}  # 年度とその検出位置を記録
    
    for pattern_obj in sorted(detector.patterns, key=lambda x: x.priority, reverse=True):
        matches = list(pattern_obj.compiled.finditer(text))
        if matches:
            print(f"\n{pattern_obj.name} (優先度: {pattern_obj.priority}):")
            print(f"  パターン: {pattern_obj.pattern}")
            
            for match in matches:
                try:
                    converted_year = pattern_obj.converter(match.group(1))
                    is_valid = detector._is_valid_year(converted_year)
                    
                    # 前後の文脈を取得
                    start_context = max(0, match.start() - 30)
                    end_context = min(len(text), match.end() + 30)
                    context = text[start_context:end_context].replace('\n', '\\n')
                    
                    print(f"    マッチ: '{match.group(0)}' -> '{converted_year}' ({'有効' if is_valid else '無効'})")
                    print(f"    位置: {match.start()}-{match.end()}")
                    print(f"    文脈: ...{context}...")
                    
                    # 重複検出の分析
                    if converted_year in detected_positions:
                        existing_pos = detected_positions[converted_year]['position']
                        existing_pattern = detected_positions[converted_year]['pattern']
                        distance = abs(match.start() - existing_pos)
                        
                        print(f"    ⚠️ 重複検出: {existing_pattern}で位置{existing_pos}で既に検出済み (距離: {distance})")
                        
                        # 重複判定ロジックをテスト
                        is_duplicate = detector._is_duplicate(converted_year, match.start(), 
                                                            {converted_year: existing_pos}, 
                                                            {existing_pattern: [(existing_pos, converted_year)]})
                        print(f"    重複判定結果: {is_duplicate}")
                    else:
                        detected_positions[converted_year] = {
                            'position': match.start(),
                            'pattern': pattern_obj.name
                        }
                        
                except Exception as e:
                    print(f"    変換エラー: '{match.group(0)}' -> {e}")

def test_year_prioritization():
    """年度優先順位の仕組みをテスト"""
    print(f"\n【年度優先順位テスト】")
    
    detector = YearDetector()
    
    # 優先度の異なるパターンが重複する場合のテスト
    test_cases = [
        {
            'name': '漢数字vs平成年号',
            'text': '平成十五年度 二〇二五年度',
            'expected': ['2025'],  # 漢数字が優先されるべき
        },
        {
            'name': '4桁西暦vs2桁年度', 
            'text': '2025年度入試 25年度生',
            'expected': ['2025'],  # 4桁が優先されるべき
        },
        {
            'name': '令和vs2桁年度',
            'text': '令和7年度 25年度',
            'expected': ['2025'],  # どちらを優先すべきか？
        }
    ]
    
    for test_case in test_cases:
        print(f"\nテスト: {test_case['name']}")
        print(f"入力: '{test_case['text']}'")
        
        result = detector.detect_years(test_case['text'])
        print(f"結果: {result.years}")
        print(f"期待: {test_case['expected']}")
        print(f"一致: {'✓' if result.years == test_case['expected'] else '✗'}")
        
        # 詳細分析
        if len(result.years) != len(test_case['expected']) or result.years != test_case['expected']:
            print(f"パターン詳細: {result.detection_patterns}")

def analyze_confidence_calculation():
    """信頼度計算の分析"""
    print(f"\n【信頼度計算分析】")
    
    detector = YearDetector()
    
    test_cases = [
        ('二〇二五年度', '単一の漢数字年度'),
        ('2025年度', '単一の4桁西暦'),
        ('令和7年度', '単一の令和年号'),
        ('平成15年度', '単一の平成年号'),
        ('25年度', '単一の2桁年度'),
        ('2025年度入試 令和7年度生募集', '複数パターンで同一年度'),
        ('2025年度入試 2024年度参考', '異なる年度の複数検出'),
        ('2025年度 平成15年創立 西暦2000年記念', '異なる年度の複数検出'),
    ]
    
    for text, description in test_cases:
        result = detector.detect_years(text)
        print(f"\n{description}:")
        print(f"  テキスト: '{text}'")
        print(f"  検出年度: {result.years}")
        print(f"  信頼度: {result.confidence:.2f}")
        print(f"  パターン数: {len(result.detection_patterns)}")

def suggest_fix_for_multiple_detection():
    """複数年度誤検出の修正案を提案"""
    print(f"\n【修正案の提案】")
    
    print("1. 文脈フィルタリングの強化:")
    print("   - 歴史問題での年号は年度として扱わない")
    print("   - '平成○年に起きた', '西暦○年の出来事' -> 歴史的事実")
    print("   - '○年度入学試験', '令和○年度' -> 実際の年度")
    
    print("\n2. 優先度ルールの改良:")
    print("   - 最高優先度: ファイル名から単一年度検出")
    print("   - 高優先度: 明確な年度表記（二〇二五年度、令和7年度、2025年度）")
    print("   - 中優先度: 年号表記（平成15年度）")
    print("   - 低優先度: 2桁年度（25年度）")
    
    print("\n3. 重複除外ロジックの強化:")
    print("   - 同一年度が複数パターンで検出された場合、最高優先度のもののみ採用")
    print("   - 異なる年度が検出された場合、文脈分析で年度らしさを判定")
    
    print("\n4. 信頼度に基づく単一年度選択:")
    print("   - 複数年度検出時、最も信頼度の高い年度を選択")
    print("   - または、明らかに試験年度と思われるパターンを優先")

def create_improved_detector():
    """改良版年度検出器のプロトタイプを作成"""
    print(f"\n【改良版年度検出器のテスト】")
    
    # 改良版のロジックをここに実装（簡易版）
    def detect_primary_year(text):
        """主要年度を検出（改良版）"""
        detector = YearDetector()
        result = detector.detect_years(text)
        
        if len(result.years) <= 1:
            return result.years
        
        # 複数年度が検出された場合の優先順位判定
        primary_patterns = ['year_kanji', 'year_4digit', 'reiwa']
        historical_patterns = ['heisei']  # 文脈によっては歴史的年号
        
        primary_years = []
        for pattern_name in primary_patterns:
            if pattern_name in result.detection_patterns:
                years = [year for _, year in result.detection_patterns[pattern_name]]
                primary_years.extend(years)
        
        if primary_years:
            # 最新の年度を優先（現在の試験年度と推定）
            return [max(primary_years)]
        
        # フォールバック: 最初に検出された年度
        return [result.years[0]]
    
    # テスト実行
    test_text = """聖光学院中学校
二〇二五年度入学試験問題
平成15年に制定された法律について述べよ。
西暦2000年に起きた出来事を説明せよ。"""
    
    original_years = YearDetector().detect_years(test_text).years
    improved_years = detect_primary_year(test_text)
    
    print(f"元の検出結果: {original_years}")
    print(f"改良版の結果: {improved_years}")

if __name__ == "__main__":
    analyze_multiple_year_detection()
    test_year_prioritization()
    analyze_confidence_calculation()
    suggest_fix_for_multiple_detection()
    create_improved_detector()