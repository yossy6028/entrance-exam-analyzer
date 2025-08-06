#!/usr/bin/env python3
"""
最終版抽出ロジックのテスト
2025年開成中学校の国語入試問題を完全に分析
"""

import sys
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor

def test_kaisei_2025_final():
    """2025年開成の入試問題を最終版で分析"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*70)
    print("2025年 開成中学校 国語入試問題 完全分析結果")
    print("="*70)
    
    # 最終版コンテンツ抽出器を初期化
    extractor = FinalContentExtractor()
    
    # 内容を抽出
    result = extractor.extract_all_content(text)
    
    # 基本情報
    print(f"\n【基本情報】")
    print(f"  総文字数: {result['total_characters']:,}文字")
    print(f"  総設問数: {result['total_questions']}問")
    print(f"  大問数: {len(result['sections'])}問")
    
    # 出典一覧
    print(f"\n【検出された出典】")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['author']}『{source['work']}』")
        print(f"     位置: {source['position']}")
    
    # 各大問の詳細
    print(f"\n【各大問の詳細分析】")
    for section in result['sections']:
        print(f"\n━━━ 大問{section['number']} ━━━")
        print(f"  文字数: {section['characters']:,}文字")
        print(f"  ジャンル: {section['genre']}")
        print(f"  テーマ: {section['theme']}")
        
        if section['source']:
            print(f"  著者: {section['source']['author']}")
            print(f"  作品: {section['source']['work']}")
        else:
            print("  出典: 不明")
        
        print(f"  設問数: {len(section['questions'])}問")
        if section['questions']:
            for j, q in enumerate(section['questions'], 1):
                print(f"    問{q['number']}: {q.get('type', '不明')}問題")
                # 設問の冒頭を表示
                preview = q['text'][:50].replace('\n', ' ')
                print(f"      「{preview}...」")
    
    # 設問タイプの集計
    print(f"\n【設問タイプ別集計】")
    for q_type, count in result['question_types'].items():
        if count > 0:
            print(f"  {q_type}: {count}問")
    
    print("\n" + "="*70)
    
    # 正解との照合
    print("【実際の正解との照合】")
    print("="*70)
    
    expected = [
        {'author': '古内一絵', 'work': '百年の子'},
        {'author': '永井玲衣', 'work': '世界の適切な保存'}
    ]
    
    print("\n期待される出典:")
    for exp in expected:
        print(f"  ・{exp['author']}『{exp['work']}』")
        
        # 検出できたか確認
        found = any(
            s['author'] == exp['author'] and s['work'] == exp['work']
            for s in result['sources']
        )
        
        if found:
            print(f"    ✅ 正しく検出されました")
        else:
            print(f"    ❌ 検出できませんでした")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_kaisei_2025_final()