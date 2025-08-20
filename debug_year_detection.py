#!/usr/bin/env python3
"""年度検出のデバッグスクリプト"""

from pathlib import Path
from modules.year_detector import YearDetector

# OCRテキストファイルを読み込み
ocr_file = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.ocr.txt")

if not ocr_file.exists():
    print(f"❌ ファイルが見つかりません: {ocr_file}")
    exit(1)

with open(ocr_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 年度検出器を初期化
detector = YearDetector()

# デバッグ用に各パターンをテスト
print("=== パターン別の検出結果 ===\n")

import re

for pattern_obj in detector.patterns:
    print(f"パターン: {pattern_obj.name} (優先度: {pattern_obj.priority})")
    print(f"正規表現: {pattern_obj.pattern}")
    
    matches = pattern_obj.compiled.finditer(text)
    found_years = []
    
    for match in matches:
        try:
            year = pattern_obj.converter(match.group(1))
            if detector._is_valid_year(year):
                # 周辺のテキストを表示
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].replace('\n', ' ')
                
                found_years.append({
                    'year': year,
                    'matched': match.group(0),
                    'position': match.start(),
                    'context': context
                })
        except:
            pass
    
    if found_years:
        for item in found_years[:5]:  # 最初の5件のみ表示
            print(f"  - 検出: {item['year']} (マッチ: '{item['matched']}')")
            print(f"    文脈: ...{item['context']}...")
    else:
        print("  - 検出なし")
    print()

# 最終的な検出結果
print("\n=== 最終的な検出結果 ===")
result = detector.detect_years(text, ocr_file)
print(f"検出された年度: {', '.join(result.years)}")
print(f"信頼度: {result.confidence:.1%}")
print(f"検出パターン: {list(result.detection_patterns.keys())}")