#!/usr/bin/env python3
"""
第2の出典検出のテスト
聖光学院2025年度で検出されない第2の出典をテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.universal_analyzer import UniversalAnalyzer

def test_second_source_detection():
    """第2の出典検出のテスト"""
    
    # 第2の出典が含まれるテキスト（実際の聖光学院2025年度の形式）
    test_text = """
    四、次の文章を読んで、後の問いに答えなさい。
    
    （前略）
    
    キノコは本当に奇妙な生き物だ。植物でもなく動物でもない。
    そのひっそりとした営みは、まるで見えない世界の住人のようだ。
    
    （中略）
    
    永井佳子「見えないキノコの勤勉な日々」（『図書』第九〇四号所収）による
    """
    
    analyzer = UniversalAnalyzer()
    
    # 出典抽出のテスト
    sources = analyzer._extract_sources_from_text(test_text)
    
    print("=== 第2の出典検出テスト ===")
    print(f"テキスト: {repr(test_text[-100:])}")
    print(f"\n検出された出典: {len(sources)}件")
    
    for i, source in enumerate(sources, 1):
        print(f"  出典{i}: {source.author}「{source.title}」")
        if hasattr(source, 'extra_info'):
            print(f"    追加情報: {source.extra_info}")
    
    # より複雑なケースもテスト
    complex_text = """
    三、次の文章を読んで、後の問いに答えなさい。
    
    森沢明夫『本が紡いだ五つの奇跡』による
    
    四、次の文章を読んで、後の問いに答えなさい。
    
    永井佳子「見えないキノコの勤勉な日々」（『図書』第九〇四号所収）による
    """
    
    print("\n=== 複数出典の検出テスト ===")
    sources2 = analyzer._extract_sources_from_text(complex_text)
    print(f"検出された出典: {len(sources2)}件")
    
    for i, source in enumerate(sources2, 1):
        print(f"  出典{i}: {source.author}「{source.title}」")

if __name__ == "__main__":
    test_second_source_detection()