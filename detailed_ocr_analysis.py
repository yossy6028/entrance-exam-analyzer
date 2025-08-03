#!/usr/bin/env python3
"""
OCRテキストの詳細分析 - 桜蔭15年度の問題構造を完全に把握
"""
import re

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== 桜蔭15年度 OCR結果の詳細分析 ===\n")

# ページごとに分割
pages = text.split("=== ページ")

print("【ページ構成】")
print(f"総ページ数: {len(pages)-1}ページ\n")

# 各ページの内容を分析
for i in range(1, len(pages)):
    page_text = pages[i]
    print(f"\n━━━ ページ {i} ━━━")
    
    # 大問マーカーを探す
    dai_mon_patterns = [
        r'([一二三四五六七八九十])、次の文章を読んで',
        r'([一二三四五六七八九十])\s+次の文章を読んで',
        r'([一二三四五六七八九十])[\s、]+'
    ]
    
    for pattern in dai_mon_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            print(f"大問マーカー検出: {matches}")
    
    # 設問マーカーを探す
    question_markers = []
    
    # 問一〜問六のパターン
    mon_matches = re.findall(r'問[一二三四五六七八九十]', page_text)
    if mon_matches:
        question_markers.extend(mon_matches)
    
    # 間一〜間六（OCR誤認識）
    kan_matches = re.findall(r'間[一二三四五六七八九十]', page_text)
    if kan_matches:
        question_markers.extend([m.replace('間', '問') for m in kan_matches])
    
    # 丸数字
    circle_matches = re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩]', page_text)
    if circle_matches:
        question_markers.extend(circle_matches)
    
    if question_markers:
        print(f"設問マーカー: {question_markers}")
    
    # ページの最初の100文字を表示
    preview = page_text[:100].replace('\n', ' ')
    print(f"冒頭部分: {preview}...")

print("\n\n【実際の問題構造（手動確認）】")

# ページ1の詳細分析
print("\n◆ページ1（大問一）")
page1_text = pages[1] if len(pages) > 1 else ""

# 大問一の検出
if '一、次の文章を読んで' in page1_text:
    print("✓ 大問一「一、次の文章を読んで」を検出")
    
    # 大問一の設問を探す
    print("\n大問一の設問:")
    
    # ①②の位置を特定
    circle_nums = []
    for num in ['①', '②']:
        pos = page1_text.find(num)
        if pos > 0:
            context = page1_text[pos:pos+50].replace('\n', ' ')
            print(f"  {num} (位置:{pos}) - {context[:40]}...")
            circle_nums.append((num, pos))

# ページ2の詳細分析
print("\n◆ページ2（大問一の続き + 大問二）")
page2_text = pages[2] if len(pages) > 2 else ""

# 問一〜問六を探す
for i in ['一', '二', '三', '四', '五', '六']:
    patterns = [f'問{i}', f'間{i}']  # OCR誤認識も考慮
    for pattern in patterns:
        if pattern in page2_text:
            pos = page2_text.find(pattern)
            context = page2_text[pos-20:pos+50].replace('\n', ' ')
            print(f"  {pattern} → 問{i} (位置:{pos})")
            print(f"    前後: ...{context}...")

# 大問二の開始位置
if '二 次の文章を読んで' in page2_text:
    pos = page2_text.find('二 次の文章を読んで')
    print(f"\n✓ 大問二「二 次の文章を読んで」を検出 (位置:{pos})")

print("\n\n【正確な問題構成】")
print("大問一（写真・浮遊写真の話）:")
print("  - 問一: 「Aについて」説明")
print("  - 問二: 「Bのように感じた」理由説明")
print("  - 問三: 「Eとはどういうことか」C・Dを例に説明")
print("  - 問四: (ページ2に続く)")
print("  - 問五: (ページ2に続く)")
print("  - 問六: 「Fとは筆者の場合」説明")
print("  - ①: 慣用句の穴埋め（身体の一部）")
print("  - ②: 慣用句の穴埋め（語群から選択）")
print("  小計: 8問")

print("\n大問二（藪原宿・櫛職人の話）:")
print("  - 漢字・語彙問題など")
print("  小計: 3問程度")

print("\n合計: 11問")

# 検出漏れの原因分析
print("\n\n【検出漏れの原因】")
print("1. 大問一の開始位置が早い（ページ1の51文字目）")
print("2. 問一〜問三がページ2にあり、大問二と混在")
print("3. OCRで「問」が「間」として認識される場合がある")
print("4. 設問が複数ページにまたがっている")