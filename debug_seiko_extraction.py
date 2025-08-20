#!/usr/bin/env python3
"""
聖光学院の入試問題分析デバッグスクリプト
問題：大問1に森沢明夫、大問2に永井慶子が記載されているが、実際は異なる
"""

import os
import sys
import json
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, '/Users/yoshiikatsuhiko/entrance_exam_analyzer')

from modules.final_content_extractor import FinalContentExtractor

def debug_seiko_analysis():
    """聖光学院の問題分析をデバッグ"""
    
    # OCRテキストファイルのパス
    ocr_file = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).ocr.txt'
    
    if not os.path.exists(ocr_file):
        print(f"OCRファイルが見つかりません: {ocr_file}")
        return
    
    # OCRテキストを読み込み
    with open(ocr_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=" * 80)
    print("聖光学院2025年 入試問題分析デバッグ")
    print("=" * 80)
    
    # テキストの基本情報
    print(f"総文字数: {len(text):,}")
    print(f"行数: {text.count(chr(10)):,}")
    print()
    
    # FinalContentExtractorで分析
    extractor = FinalContentExtractor()
    
    print("1. 出典抽出の確認")
    print("-" * 40)
    sources = extractor._extract_all_sources(text)
    print(f"検出された出典数: {len(sources)}")
    
    for i, source in enumerate(sources, 1):
        print(f"  出典{i}: {source['author']} 『{source['work']}』")
        print(f"    位置: {source['position']}")
        print(f"    原文: {source['full_text']}")
        print()
    
    print("2. 大問分割の確認")
    print("-" * 40)
    sections = extractor._identify_and_divide_sections(text, sources)
    print(f"検出された大問数: {len(sections)}")
    
    for i, section in enumerate(sections, 1):
        print(f"  大問{i}:")
        if section.get('source'):
            print(f"    著者: {section['source']['author']}")
            print(f"    作品: {section['source']['work']}")
        else:
            if section.get('is_kanji'):
                print(f"    種類: 漢字・語句問題")
            else:
                print(f"    種類: 出典なしの文章問題")
        
        print(f"    文字数: {len(section['text']):,}")
        print(f"    範囲: {section['start']} - {section['end']}")
        
        # セクションの最初の部分を表示
        preview = section['text'][:200].replace('\n', ' ')
        print(f"    内容プレビュー: {preview}...")
        print()
    
    print("3. 完全分析結果")
    print("-" * 40)
    result = extractor.extract_all_content(text)
    
    print(f"総文字数: {result['total_characters']:,}")
    print(f"総設問数: {result['total_questions']}")
    print("設問タイプ:")
    for q_type, count in result['question_types'].items():
        print(f"  {q_type}: {count}問")
    print()
    
    print("各大問の詳細:")
    for section in result['sections']:
        print(f"  大問{section['number']}:")
        if section['source']:
            print(f"    著者: {section['source']['author']}")
            print(f"    作品: {section['source']['work']}")
        else:
            print(f"    種類: 出典なし（{section['genre']}）")
        
        print(f"    ジャンル: {section['genre']}")
        print(f"    テーマ: {section['theme']}")
        print(f"    文字数: {section['characters']:,}")
        print(f"    設問数: {len(section['questions'])}")
        print()
    
    print("4. 問題の特定")
    print("-" * 40)
    
    # 実際の構成を確認
    print("期待される構成:")
    print("  大問1: 漢字語句問題（出典なし）")
    print("  大問2: ???")
    print("  大問3: 森沢明夫『本が紡いだ物語』")
    print("  大問4: 永井慶子の作品")
    print()
    
    print("現在の検出結果:")
    for i, section in enumerate(result['sections'], 1):
        if section['source']:
            print(f"  大問{i}: {section['source']['author']} 『{section['source']['work']}』")
        else:
            print(f"  大問{i}: {section['genre']} ({section['theme']})")
    
    # 問題点を特定
    issues = []
    if len(result['sections']) < 3:
        issues.append("大問の数が不足している可能性")
    
    if len(sources) < 2:
        issues.append("出典の検出数が不足している可能性")
    
    # 森沢明夫と永井慶子の位置を確認
    morisawa_found = any('森沢明夫' in text[s['position']:s['position']+100] for s in sources)
    nagai_found = any('永井' in text[s['position']:s['position']+100] for s in sources)
    
    if not morisawa_found:
        issues.append("森沢明夫が正しく検出されていない可能性")
    if not nagai_found:
        issues.append("永井慶子が正しく検出されていない可能性")
    
    if issues:
        print("\n問題点:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n特に問題は検出されませんでした。")
    
    # JSON形式でも出力
    output_file = '/Users/yoshiikatsuhiko/entrance_exam_analyzer/seiko_debug_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細結果をJSONファイルに保存しました: {output_file}")

if __name__ == "__main__":
    debug_seiko_analysis()