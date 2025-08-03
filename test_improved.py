#!/usr/bin/env python3
"""
改善されたアナライザーのテスト
"""
import sys
sys.path.append('.')

from improved_text_analyzer import ImprovedTextAnalyzer
from config import QUESTION_PATTERNS

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# アナライザーを初期化
analyzer = ImprovedTextAnalyzer(QUESTION_PATTERNS)

# 分析実行
result = analyzer.analyze_exam_structure(text)

print("=== 改善版アナライザーの結果 ===\n")

print(f"大問数: {len(result['sections'])}")
print(f"総設問数: {len(result['questions'])}\n")

# 大問ごとの詳細
for section in result['sections']:
    print(f"\n【大問{section['number']}】")
    print(f"マーカー: {section['marker'] if section['marker'] else '(検出なし)'}")
    print(f"開始位置: {section['start_pos']}")
    
    # この大問の設問
    section_questions = [q for q in result['questions'] if q['section'] == section['number']]
    print(f"設問数: {len(section_questions)}")
    
    print("\n設問リスト:")
    for i, q in enumerate(section_questions, 1):
        print(f"  {i}. {q['marker']} ({q['type']})")
        # 問題文の一部
        text_preview = q['text'][:50].replace('\n', ' ')
        print(f"     「{text_preview}...」")

print("\n\n=== 総合結果 ===")
print(f"総設問数: {len(result['questions'])}問")

# タイプ別集計
print("\nタイプ別内訳:")
for t, count in result['question_types'].items():
    if count > 0:
        print(f"  {t}: {count}問")

# 目標との比較
print("\n【目標】")
print("- 大問数: 2")
print("- 総設問数: 11")
print(f"\n【結果】")
print(f"- 大問数: {len(result['sections'])}")
print(f"- 総設問数: {len(result['questions'])}")

# 精度評価
accuracy = (1 - abs(len(result['questions']) - 11) / 11) * 100
print(f"\n検出精度: {accuracy:.1f}%")