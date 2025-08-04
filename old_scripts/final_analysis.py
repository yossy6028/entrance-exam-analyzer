#!/usr/bin/env python3
"""
桜蔭15年度の最終分析
"""
import sys
import re
sys.path.append('.')

from modules.text_analyzer import TextAnalyzer
from config import QUESTION_PATTERNS

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== 桜蔭15年度 国語問題 最終分析 ===\n")

# アナライザーを初期化
analyzer = TextAnalyzer(QUESTION_PATTERNS)

# 分析実行
result = analyzer.analyze_exam_structure(text)

print(f"検出された大問数: {len(result['sections'])}")
print(f"検出された設問総数: {len(result['questions'])}\n")

# 大問ごとの詳細
for section in result['sections']:
    print(f"\n【大問{section['number']}】 {section['marker']}")
    
    # この大問の設問
    section_questions = [q for q in result['questions'] if q['section'] == section['number']]
    print(f"設問数: {len(section_questions)}")
    
    # 設問タイプ別集計
    types = {}
    for q in section_questions:
        types[q['type']] = types.get(q['type'], 0) + 1
    
    print("タイプ別内訳:")
    for t, count in types.items():
        print(f"  - {t}: {count}問")
    
    print("\n設問詳細:")
    for i, q in enumerate(section_questions, 1):
        marker = q['marker']
        # 問題文の一部を抽出（説明文を含む）
        q_text = q['text']
        
        # 説明指示を探す
        if '説明しなさい' in q_text:
            desc = '説明問題'
        elif '答えなさい' in q_text and '漢字' in q_text:
            desc = '漢字問題'
        elif '語群から選び' in q_text:
            desc = '語句選択'
        elif '抜き出し' in q_text:
            desc = '抜き出し'
        else:
            desc = q['type']
        
        print(f"  {i}. {marker} - {desc}")
        
        # 問題文の要約（最初の指示部分）
        instruction = re.search(r'([^。]+(?:しなさい|答えなさい|選びなさい))', q_text)
        if instruction:
            inst_text = instruction.group(1).replace('\n', ' ')[:60]
            print(f"     「{inst_text}...」")

print("\n\n=== 最終集計 ===")
print(f"総設問数: {len(result['questions'])}問")
print("\n設問タイプ別:")
for t, count in result['question_types'].items():
    if count > 0:
        print(f"  - {t}: {count}問")

# 手動での確認
print("\n\n=== 手動確認（実際の問題構成）===")
print("大問一（写真・浮遊写真の話）:")
print("  - 問一: Aについて説明（記述）")
print("  - 問二: Bについて説明（記述）") 
print("  - 問三: Eについて説明（記述）")
print("  - 問四: Fについて説明（記述）")
print("  - 問五: ①慣用句の穴埋め（語句）")
print("  - 問六: ②慣用句の穴埋め（語句）")
print("  小計: 6問")
print("\n大問二（藪原宿・櫛職人の話）:")
print("  - 数問の設問")
print("\n合計: 11問程度")

# 検出精度の評価
detected_total = len(result['questions'])
expected_total = 11
accuracy = (1 - abs(detected_total - expected_total) / expected_total) * 100

print(f"\n\n検出精度: {accuracy:.1f}%")
if detected_total == expected_total:
    print("✅ 正確に検出できました！")
elif detected_total > expected_total:
    print(f"⚠️  {detected_total - expected_total}問多く検出されています")
else:
    print(f"⚠️  {expected_total - detected_total}問少なく検出されています")