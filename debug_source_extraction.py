#!/usr/bin/env python3
"""出典抽出ロジックのデバッグ用スクリプト"""

import re

# 実際のテキストファイルから出典を抽出してテスト
with open('15渋渋_bunko.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("=== 出典抽出テスト ===")

# 実際の出典文字列
actual_source = "（朱喜哲『〈￹公正￺フェアネス￻〉を乗りこなす 正義の反対は別の正義か』より）"
print(f"実際の出典文字列:")
print(f"'{actual_source}'")
print(f"長さ: {len(actual_source)} 文字")

# analyze_shibuya_2015.pyで使用されているパターン
source_patterns = [
    r'（([^）]{1,50}『[^』]{1,100}』[^）]{0,20})）',  # 日本語括弧、長さ制限
    r'（([^）]{1,50}「[^」]{1,100}」[^）]{0,20})）',   # 日本語括弧、引用符
    r'\(([^)]{1,50}『[^』]{1,100}』[^)]{0,20})\)',  # 半角括弧
]

print(f"\n=== パターンマッチングテスト ===")
sources = []

for i, pattern in enumerate(source_patterns, 1):
    print(f"\nパターン {i}: {pattern}")
    matches = list(re.finditer(pattern, text))
    print(f"マッチ数: {len(matches)}")
    
    for match in matches:
        source_text = match.group(1)
        print(f"  マッチ内容: '{source_text}'")
        print(f"  長さ: {len(source_text)} 文字")
        print(f"  位置: {match.start()}-{match.end()}")
        
        # 長さチェック
        if len(source_text) > 150:
            print(f"  → 除外: 長すぎる（{len(source_text)} > 150）")
            continue
            
        # 著者名と作品名を抽出
        if '『' in source_text:
            parts = source_text.split('『')
            if len(parts) >= 2:
                author = parts[0].strip()
                title = parts[1].split('』')[0].strip()
                print(f"  著者: '{author}' (長さ: {len(author)})")
                print(f"  作品: '{title}' (長さ: {len(title)})")
                
                # 長さ制限チェック
                if 1 <= len(author) <= 20 and 1 <= len(title) <= 50:
                    sources.append({
                        'author': author,
                        'title': title,
                        'full': source_text,
                        'position': match.start()
                    })
                    print(f"  → 採用")
                else:
                    print(f"  → 除外: 長さ制限（著者: {len(author)}, 作品: {len(title)}）")

print(f"\n=== 最終結果 ===")
print(f"抽出された出典数: {len(sources)}")
for i, source in enumerate(sources, 1):
    print(f"{i}. 著者: {source['author']}")
    print(f"   作品: {source['title']}")
    print(f"   位置: {source['position']}")

# 特に、朱喜哲の出典が正しく抽出されるかチェック
target_found = False
for source in sources:
    if '朱喜哲' in source['author'] or 'フェアネス' in source['title']:
        target_found = True
        print(f"\n🎯 目標の出典が見つかりました:")
        print(f"   著者: {source['author']}")
        print(f"   作品: {source['title']}")

if not target_found:
    print(f"\n❌ 朱喜哲の出典が見つかりませんでした")
    
    # デバッグ: 実際の文字列に対してパターンを個別テスト
    print(f"\n=== 個別文字列テスト ===")
    test_string = actual_source
    for i, pattern in enumerate(source_patterns, 1):
        match = re.search(pattern, test_string)
        print(f"パターン {i}: {'マッチ' if match else 'マッチしない'}")
        if match:
            print(f"  マッチ内容: '{match.group(1)}'")