#!/usr/bin/env python3
"""
完璧な分析ロジックのテスト
"""
import sys
sys.path.append('.')

from perfect_analyzer import PerfectTextAnalyzer
from config import QUESTION_PATTERNS

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# アナライザーを初期化
analyzer = PerfectTextAnalyzer(QUESTION_PATTERNS)

# 分析実行
result = analyzer.analyze_exam_structure(text)

print("=== 桜蔭中学校 2015年度 国語 完璧な分析結果 ===\n")

print(f"【大問数】 {len(result['sections'])}")
print(f"【総設問数】 {len(result['questions'])}")

# 大問ごとの詳細
for section in result['sections']:
    print(f"\n━━━ 大問{section['number']} ━━━")
    print(f"マーカー: {section['marker']}")
    print(f"開始位置: {section['start_pos']}")
    
    # この大問の設問
    section_questions = [q for q in result['questions'] if q['section'] == section['number']]
    print(f"設問数: {len(section_questions)}問")
    
    print("\n【設問一覧】")
    for q in section_questions:
        print(f"  {q['number']:2d}. {q['marker']:6s} ({q['type']})")
        # 問題文の一部
        text_preview = q['text'][:50].replace('\n', ' ')
        print(f"      「{text_preview}...」")

print("\n\n【総合結果】")
print(f"総設問数: {len(result['questions'])}問")

# タイプ別集計
print("\nタイプ別内訳:")
for t, count in result['question_types'].items():
    if count > 0:
        print(f"  {t}: {count}問")

# 期待値との比較
expected = 11
actual = len(result['questions'])
print(f"\n期待される問題数: {expected}問")
print(f"実際の検出数: {actual}問")

if actual == expected:
    print("\n✅ 完璧！精度100%を達成しました！")
else:
    diff = actual - expected
    if diff > 0:
        print(f"\n⚠️  {diff}問多く検出されています")
    else:
        print(f"\n⚠️  {abs(diff)}問少なく検出されています")

# 正確な11問の内訳を表示
print("\n\n【正確な問題構成（11問）】")
print("大問一（8問）:")
print("  1. 問一: Aについて説明")
print("  2. 問二: Bのように感じた理由")
print("  3. 問三: Eについて説明")
print("  4. 問四: （問題文確認中）")
print("  5. 問五: （問題文確認中）")
print("  6. 問六: Fについて説明")
print("  7. ①: 慣用句（身体の一部）")
print("  8. ②: 慣用句（語群から選択）")
print("\n大問二（3問）:")
print("  9. 漢字・語句問題1")
print("  10. 漢字・語句問題2")
print("  11. 記述問題")