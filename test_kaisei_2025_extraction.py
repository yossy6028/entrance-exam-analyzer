#!/usr/bin/env python3
"""
2025年開成中学校の国語入試問題から著者・作品情報を正確に抽出するテスト
"""

import sys
import os
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.content_extractor import ContentExtractor

def analyze_kaisei_2025():
    """2025年開成の入試問題を分析"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*70)
    print("2025年 開成中学校 国語入試問題 分析結果")
    print("="*70)
    
    # コンテンツ抽出器を初期化
    extractor = ContentExtractor()
    
    # 内容を抽出
    result = extractor.extract_exam_content(text)
    
    # 結果を表示
    print("\n【主要な出典情報】")
    if result['primary_source']:
        source = result['primary_source']
        print(f"  著者: {source['author']}")
        print(f"  作品: {source['work']}")
        print(f"  信頼度: {source['confidence']:.1%}")
        print(f"  検出タイプ: {source['type']}")
    else:
        print("  出典情報が検出できませんでした")
    
    print("\n【検出された全ての出典候補】")
    if result['all_sources']:
        for i, source in enumerate(result['all_sources'], 1):
            print(f"  {i}. 著者: {source['author']}, 作品: {source['work']}")
            print(f"     信頼度: {source['confidence']:.1%}, タイプ: {source['type']}")
    else:
        print("  候補なし")
    
    print(f"\n【ジャンル】: {result['genre']}")
    print(f"【テーマ】: {result['theme']}")
    print(f"【総文字数】: {result['total_characters']:,}文字")
    
    # 実際のテキストから手動で確認
    print("\n【テキストから直接確認】")
    
    # 「（古内一絵『百年の子』より）」を探す
    if "古内一絵" in text:
        print("  ✓ '古内一絵' が検出されました")
        # 周辺のテキストを表示
        index = text.find("古内一絵")
        context = text[max(0, index-20):min(len(text), index+50)]
        print(f"    コンテキスト: ...{context}...")
    else:
        print("  ✗ '古内一絵' が見つかりません")
    
    if "百年の子" in text:
        print("  ✓ '百年の子' が検出されました")
    else:
        print("  ✗ '百年の子' が見つかりません")
    
    # 設問数を数える
    print("\n【設問数の確認】")
    questions = []
    
    # 「問一」「問二」「問三」のパターンを探す
    import re
    question_pattern = re.compile(r'問[一二三四五六七八九十]')
    matches = question_pattern.findall(text)
    print(f"  検出された設問: {', '.join(matches)}")
    print(f"  設問数: {len(matches)}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    analyze_kaisei_2025()