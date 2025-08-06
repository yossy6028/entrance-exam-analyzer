#!/usr/bin/env python3
"""
改良版抽出ロジックのテスト
2025年開成中学校の国語入試問題を正確に分析
"""

import sys
import os
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.improved_content_extractor import ImprovedContentExtractor

def test_kaisei_2025():
    """2025年開成の入試問題を改良版で分析"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*70)
    print("2025年 開成中学校 国語入試問題 分析結果（改良版）")
    print("="*70)
    
    # 改良版コンテンツ抽出器を初期化
    extractor = ImprovedContentExtractor()
    
    # 内容を抽出
    result = extractor.extract_sources_from_exam(text)
    
    # 結果を表示
    print(f"\n【総文字数】: {result['total_characters']:,}文字")
    print(f"【総設問数】: {result['total_questions']}問")
    print(f"【大問数】: {len(result['sections'])}問")
    
    print("\n【各大問の詳細】")
    for section in result['sections']:
        print(f"\n大問{section['number']}:")
        print(f"  文字数: {section['characters']:,}文字")
        
        if section['source']:
            print(f"  著者: {section['source']['author']}")
            print(f"  作品: {section['source']['work']}")
        else:
            print("  出典: 検出できず")
        
        print(f"  設問数: {len(section['questions'])}問")
        if section['questions']:
            q_nums = [q['number'] for q in section['questions']]
            print(f"  設問番号: {', '.join(q_nums)}")
    
    # 実際のテキストから正解を確認
    print("\n" + "="*70)
    print("【正解との照合】")
    print("="*70)
    
    correct_sources = [
        {'author': '古内一絵', 'work': '百年の子'},
        {'author': '永井玲衣', 'work': '世界の適切な保存'},
    ]
    
    print("\n期待される出典:")
    for i, source in enumerate(correct_sources, 1):
        print(f"  {i}. {source['author']}『{source['work']}』")
        
        # テキスト中に存在するか確認
        if source['author'] in text:
            print(f"     ✓ 著者名「{source['author']}」がテキストに存在")
        else:
            print(f"     ✗ 著者名「{source['author']}」が見つからない")
            
        if source['work'] in text:
            print(f"     ✓ 作品名「{source['work']}」がテキストに存在")
        else:
            print(f"     ✗ 作品名「{source['work']}」が見つからない")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_kaisei_2025()