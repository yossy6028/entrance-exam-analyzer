#!/usr/bin/env python3
"""
最終的な分析結果を確認
"""
import sys
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

print("=== 桜蔭中学校 2015年度 国語 分析結果 ===\n")

print(f"【総文字数】 {result['total_characters']:,}文字")
print(f"【文章テーマ】 {result['theme']}")
print(f"【大問数】 {len(result['sections'])}")
print(f"【総設問数】 {len(result['questions'])}\n")

# 大問ごとの詳細
for section in result['sections']:
    print(f"\n━━━ 大問{section['number']} ━━━")
    if section['marker']:
        print(f"マーカー: {section['marker']}")
    
    # この大問の設問
    section_questions = [q for q in result['questions'] if q['section'] == section['number']]
    print(f"設問数: {len(section_questions)}問")
    
    # 設問タイプ別集計
    types = {}
    for q in section_questions:
        types[q['type']] = types.get(q['type'], 0) + 1
    
    if types:
        print("\nタイプ別内訳:")
        for t, count in types.items():
            print(f"  {t}: {count}問")
    
    print("\n【設問一覧】")
    for i, q in enumerate(section_questions, 1):
        marker = q['marker']
        q_type = q['type']
        
        # 問題の要約
        text_preview = q['text'][:40].replace('\n', ' ')
        if '説明しなさい' in q['text']:
            summary = "説明問題"
        elif '漢字' in q['text'] or '慣用句' in q['text']:
            summary = "漢字・語句"
        elif '語群から選び' in q['text']:
            summary = "選択"
        else:
            summary = q_type
            
        print(f"{i:2d}. {marker:6s} - {summary}")

print("\n\n【総合評価】")
print(f"合計 {len(result['questions'])}問")

# 期待値との比較
expected = 11
accuracy = (1 - abs(len(result['questions']) - expected) / expected) * 100
print(f"\n期待される問題数: {expected}問")
print(f"検出精度: {accuracy:.1f}%")

if len(result['questions']) == expected:
    print("\n✅ 完璧に検出できました！")
else:
    diff = len(result['questions']) - expected
    if diff > 0:
        print(f"\n⚠️  {diff}問多く検出されています")
    else:
        print(f"\n⚠️  {abs(diff)}問少なく検出されています")

# 最後に問題の詳細を表示
print("\n\n【検出された全設問の詳細】")
for i, q in enumerate(result['questions'], 1):
    print(f"\n{i}. {q['marker']} (大問{q['section']}, {q['type']})")
    # 指示文を抽出
    import re
    instruction = re.search(r'([^。]+(?:しなさい|答えなさい|選びなさい))', q['text'])
    if instruction:
        print(f"   → {instruction.group(1)[:60]}...")

print("\n" + "="*50)
print("分析完了")