#!/usr/bin/env python3
"""
大問検出のデバッグ
"""
import re

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== 大問パターンの検索 ===\n")

# 様々なパターンで大問を検索
patterns = [
    (r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]\u3001\u6b21\u306e\u6587\u7ae0\u3092\u8aad\u3093\u3067', 'kanji_comma_text'),
    (r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]\s+\u6b21\u306e\u6587\u7ae0\u3092\u8aad\u3093\u3067', 'kanji_space_text'),
    (r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]\u3001', 'kanji_comma_only'),
]

all_matches = []
for pattern, p_type in patterns:
    matches = list(re.finditer(pattern, text))
    print(f"パターン '{p_type}': {len(matches)}件")
    for m in matches:
        start = m.start()
        end = m.end()
        context = text[max(0, start-50):min(len(text), end+100)]
        all_matches.append({
            'type': p_type,
            'text': m.group(),
            'start': start,
            'context': context.replace('\n', ' ')
        })
        print(f"  - '{m.group()}' at {start}")
        print(f"    Context: ...{context.replace(chr(10), ' ')}...")

# 位置でソート
all_matches.sort(key=lambda x: x['start'])

print("\n\n=== ページごとの大問検出 ===")
# ページごとに大問を確認
pages = text.split("=== ページ")
for i, page in enumerate(pages[1:], 1):  # 最初の空要素をスキップ
    print(f"\nページ {i}:")
    # このページ内で大問パターンを検索
    for pattern, p_type in patterns:
        matches = list(re.finditer(pattern, page))
        if matches:
            print(f"  {p_type}: {len(matches)}件")
            for m in matches:
                print(f"    - '{m.group()}'")

# 実際の構造を手動で確認
print("\n\n=== 実際の大問構造（手動確認）===")
# 一、の位置
pos1 = text.find("一、次の文章を読んで")
if pos1 > 0:
    print(f"大問一: 位置 {pos1}")
    print(f"  内容: {text[pos1:pos1+50].replace(chr(10), ' ')}")

# 二、の位置（複数の可能性をチェック）
patterns_for_two = [
    "二 次の文章を読んで",
    "二　次の文章を読んで",
    "二、次の文章を読んで",
]
for pat in patterns_for_two:
    pos2 = text.find(pat)
    if pos2 > 0:
        print(f"\n大問二: 位置 {pos2}")
        print(f"  パターン: '{pat}'")
        print(f"  内容: {text[pos2:pos2+50].replace(chr(10), ' ')}")
        break