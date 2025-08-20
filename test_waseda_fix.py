#!/usr/bin/env python3
"""
早稲田実業2015年度の分析テスト
修正されたロジックのテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.universal_analyzer import UniversalAnalyzer
from pathlib import Path

def test_waseda_2015():
    """早稲田実業2015年度のテスト"""
    
    # OCRテキストファイルを読み込み
    ocr_file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.ocr.txt"
    
    if not Path(ocr_file_path).exists():
        print(f"ファイルが見つかりません: {ocr_file_path}")
        return False
        
    with open(ocr_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"テキストの長さ: {len(text)} 文字")
    print("=" * 50)
    
    # 分析を実行
    analyzer = UniversalAnalyzer()
    result = analyzer.analyze(text, "早稲田実業学校中等部", "2015")
    
    # 結果の詳細表示
    print(f"学校名: {result.school_name}")
    print(f"年度: {result.year}")
    print(f"総文字数: {result.total_characters}")
    print(f"大問数: {len(result.sections)}")
    print("=" * 50)
    
    # 各大問の詳細
    for i, section in enumerate(result.sections, 1):
        print(f"大問{i}: {section.title}")
        print(f"  設問数: {section.question_count}")
        print(f"  内容の冒頭: {section.content[:100]}...")
        print()
    
    # 出典情報
    print("出典情報:")
    for i, source in enumerate(result.sources, 1):
        print(f"  出典{i}: 著者={source.author}, タイトル={source.title}")
    
    # 設問タイプ
    print("\n設問タイプ:")
    for q_type, count in result.question_types.items():
        print(f"  {q_type}: {count}問")
    
    print(f"\nテーマ: {result.theme}")
    print(f"ジャンル: {result.genre}")
    
    # 期待値との比較
    print("=" * 50)
    print("期待値との比較:")
    expected_sections = 3
    expected_sources = 2
    
    if len(result.sections) == expected_sections:
        print(f"✅ 大問数: {len(result.sections)} (期待値: {expected_sections})")
    else:
        print(f"❌ 大問数: {len(result.sections)} (期待値: {expected_sections})")
    
    if len(result.sources) >= expected_sources:
        print(f"✅ 出典数: {len(result.sources)} (期待値以上: {expected_sources})")
    else:
        print(f"❌ 出典数: {len(result.sources)} (期待値: {expected_sources})")
    
    return len(result.sections) == expected_sections and len(result.sources) >= expected_sources

if __name__ == "__main__":
    success = test_waseda_2015()
    if success:
        print("\n🎉 テスト成功！")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)