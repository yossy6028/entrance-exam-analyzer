#!/usr/bin/env python3
"""
改善された分析ロジックでの桜蔭15年度のテスト
"""
import sys
import re
sys.path.append('.')

from modules.text_analyzer import TextAnalyzer
from config import QUESTION_PATTERNS

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# アナライザーを初期化
analyzer = TextAnalyzer(QUESTION_PATTERNS)

# 分析実行
result = analyzer.analyze_exam_structure(text)

print("=== 改善された分析結果 ===\n")

# 大問の情報
print(f"大問数: {len(result['sections'])}")
for i, section in enumerate(result['sections']):
    print(f"\n大問{section['number']}: {section['marker']}")
    # この大問に含まれる設問数をカウント
    section_questions = [q for q in result['questions'] if q['section'] == section['number']]
    print(f"  設問数: {len(section_questions)}")
    
    # 設問の詳細
    for q in section_questions:
        print(f"  - {q['marker']} ({q['type']})")

# 全体のサマリー
print(f"\n\n=== サマリー ===")
print(f"総設問数: {len(result['questions'])}")
print("\n設問タイプ別集計:")
for q_type, count in result['question_types'].items():
    if count > 0:
        print(f"  {q_type}: {count}問")

# 実際の問題構成と比較
print("\n\n=== 実際の問題構成との比較 ===")
print("【期待される構成】")
print("大問一（写真の話）:")
print("  - 問一〜問六: 6問（記述中心）") 
print("  - ①②: 2問（語句問題）")
print("大問二（藪原宿の話）:")
print("  - 複数の小問: 3問程度")
print("合計: 11問")

print("\n【検出結果】")
print(f"検出された総設問数: {len(result['questions'])}問")

# 詳細な設問リストを出力
print("\n\n=== 検出された全設問 ===")
for i, q in enumerate(result['questions']):
    print(f"{i+1}. 大問{q['section']} - {q['marker']} ({q['type']})")
    # 設問文の最初の50文字を表示
    q_text = q['text'][:50].replace('\n', ' ')
    print(f"   '{q_text}...'")