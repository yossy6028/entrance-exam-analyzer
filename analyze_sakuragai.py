#!/usr/bin/env python3
"""
桜蔭15年度の問題構造を詳細に分析
"""
import re
from pathlib import Path

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== 桜蔭15年度 問題構造分析 ===\n")

# 大問の検出
print("【大問の検出】")
section_patterns = [
    (r'[一二三四五六七八九十]\s*、', 'kanji_comma'),
    (r'第[一二三四五六七八九十]+問', 'dai_mon'),
]

sections = []
for pattern, p_type in section_patterns:
    for match in re.finditer(pattern, text):
        start = match.start()
        end = match.end()
        sections.append({
            'type': p_type,
            'text': match.group(),
            'start': start,
            'context': text[max(0, start-20):min(len(text), end+100)]
        })

sections.sort(key=lambda x: x['start'])
for i, sec in enumerate(sections):
    print(f"大問{i+1}: {sec['text']} (位置: {sec['start']})")
    print(f"  前後文脈: ...{sec['context'].replace(chr(10), ' ')}...")
    print()

# 小問の検出
print("\n【小問の検出】")
question_patterns = [
    (r'問[一二三四五六七八九十]+', 'kanji_question'),
    (r'問[０-９0-9]+', 'number_question'),
    (r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]', 'circle_number'),
    (r'[（(][０-９0-9]+[）)]', 'parenthesis_number'),
]

questions = []
for pattern, p_type in question_patterns:
    for match in re.finditer(pattern, text):
        start = match.start()
        end = match.end()
        questions.append({
            'type': p_type,
            'text': match.group(),
            'start': start,
            'context': text[max(0, start-20):min(len(text), end+100)]
        })

questions.sort(key=lambda x: x['start'])

# 重複を除去（近い位置のものは同じ問題と見なす）
unique_questions = []
prev_start = -100
for q in questions:
    if q['start'] - prev_start > 50:  # 50文字以上離れていれば別の問題
        unique_questions.append(q)
        prev_start = q['start']

print(f"検出された小問数: {len(unique_questions)}")
for i, q in enumerate(unique_questions):
    print(f"\n小問{i+1}: {q['text']} (タイプ: {q['type']}, 位置: {q['start']})")
    print(f"  前後文脈: ...{q['context'][:80].replace(chr(10), ' ')}...")

# 問題タイプの分析
print("\n\n【問題タイプの分析】")
question_types = {
    '漢字・語句': 0,
    '記号選択': 0,
    '抜き出し': 0,
    '記述': 0,
    'その他': 0
}

for q in unique_questions:
    context = text[q['start']:min(len(text), q['start']+300)]
    
    # 漢字・語句問題
    if re.search(r'漢字|語句|慣用句|ことわざ|意味|読み', context):
        question_types['漢字・語句'] += 1
    # 記号選択
    elif re.search(r'[ア-ン]\s*[\.。、]|から選び|選びなさい|正しいもの|適切なもの', context):
        question_types['記号選択'] += 1
    # 抜き出し
    elif re.search(r'抜き出し|書き抜き|そのまま', context):
        question_types['抜き出し'] += 1
    # 記述
    elif re.search(r'説明しなさい|述べなさい|答えなさい|どうして|なぜ|理由', context):
        question_types['記述'] += 1
    else:
        question_types['その他'] += 1

print("問題タイプ別集計:")
for t, count in question_types.items():
    if count > 0:
        print(f"  {t}: {count}問")

# 実際の問題文を抽出して確認
print("\n\n【実際の設問文の確認】")
# ページ2に問1〜問6があるはず
page2_start = text.find("=== ページ 2 ===")
page3_start = text.find("=== ページ 3 ===")
if page2_start > 0 and page3_start > 0:
    page2_text = text[page2_start:page3_start]
    
    # 問題を行ごとに分割して確認
    lines = page2_text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'問[一二三四五六七八九十０-９0-9]+|[①②③④⑤⑥⑦⑧⑨⑩]', line):
            print(f"\n行{i}: {line}")
            # 次の数行も表示
            for j in range(1, min(4, len(lines)-i)):
                if lines[i+j].strip():
                    print(f"  続き: {lines[i+j]}")

print("\n\n=== 分析結果まとめ ===")
print(f"大問数: {len(sections)}")
print(f"小問総数: {len(unique_questions)}")
print("\n【詳細内訳】")
print("- 大問一（写真の話）: 問一〜問六 + ①②の語句問題 = 8問")
print("- 大問二（藪原宿の話）: 複数の小問")
print(f"\n合計: 約{len(unique_questions)}問が検出されました")