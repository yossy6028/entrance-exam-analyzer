#!/usr/bin/env python3
"""漢字セクションのデバッグ"""

import re
from pathlib import Path

# OCRテキストファイル
ocr_file = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.ocr.txt")

with open(ocr_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 大問3を探す
match = re.search(r'三次の.*?(?=以下余白|\Z)', text, re.DOTALL)

if match:
    kanji_section = match.group(0)
    print("📚 大問3（漢字）のセクション:")
    print("=" * 60)
    print(kanji_section)
    print("=" * 60)
    
    # 数字パターンを分析
    print("\n📊 検出された番号:")
    
    # パターン1: 行頭の数字
    numbers_at_start = re.findall(r'^([1-8])\s+', kanji_section, re.MULTILINE)
    print(f"行頭の数字: {numbers_at_start}")
    
    # パターン2: 1~8の範囲表記
    range_pattern = re.search(r'([1-8])~([1-8])', kanji_section)
    if range_pattern:
        print(f"範囲表記: {range_pattern.group(1)}~{range_pattern.group(2)}")
    
    # パターン3: すべての独立した数字
    all_numbers = re.findall(r'(?:^|\s)([1-8])(?:\s|$)', kanji_section, re.MULTILINE)
    print(f"すべての数字: {all_numbers}")
    
    # 漢字問題のパターン
    kanji_problems = re.findall(r'([1-8])\s+[^0-9\s]+.*?[をの]?(?:カンレイ|ギョウセキ|シュトク|センモン|キセイ|コウサツ|ショウタイ|ユウシュウ)', kanji_section)
    print(f"\n漢字問題の番号: {kanji_problems}")
    
    # カタカナの単語を探す
    katakana_words = re.findall(r'[ア-ン]+', kanji_section)
    print(f"\nカタカナ単語: {katakana_words[:10]}...")  # 最初の10個
else:
    print("大問3が見つかりませんでした")