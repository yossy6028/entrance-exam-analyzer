#!/usr/bin/env python3
"""
弁証法的解決策のテスト
Gemini-Claude議論から生まれた修正案の検証
"""

from modules.section_splitter_v3 import ImprovedSectionSplitterV3

def test_dialectical_improvements():
    """修正された機能のテスト"""
    splitter = ImprovedSectionSplitterV3()
    
    # テストケース1: 番号の逆行を防げるかテスト
    test_text_regression = """
    大問一 次の文章を読んで答えなさい。
    これは最初の問題です。
    
    大問二十二 解答用紙に記入してください。
    これはOCRノイズです。
    
    大問二 実際の2番目の問題です。
    これが本当の大問2です。
    """
    
    print("=== テスト1: 番号逆行防止 ===")
    sections = splitter.split_sections(test_text_regression)
    print(f"検出された大問数: {len(sections)}")
    for i, section in enumerate(sections):
        print(f"大問{i+1}: {section.title}")
    
    # テストケース2: OCRノイズフィルタリング
    test_text_noise = """
    大問一 次の文章を読んで答えなさい。
    
    大問二 解答用紙
    受験番号を記入してください。
    
    大問三 億円の経済効果について
    実際の問題内容です。
    """
    
    print("\n=== テスト2: OCRノイズフィルタリング ===")
    sections = splitter.split_sections(test_text_noise)
    print(f"検出された大問数: {len(sections)}")
    for i, section in enumerate(sections):
        print(f"大問{i+1}: {section.title}")
        if "解答用紙" in section.text or "億円" in section.title:
            print("  ⚠️  OCRノイズが混入している可能性")
    
    # テストケース3: 適応的距離チェック
    test_text_distance = """
    大問一 短い問題。
    
    大問二 これは非常に長い問題文で、複数の段落にわたって詳細な説明が続きます。歴史的な背景から現代への影響まで幅広くカバーしており、受験生には深い理解が求められます。このような長文問題では、次の大問までの距離が自然と長くなります。
    
    大問三 次の問題です。
    """
    
    print("\n=== テスト3: 適応的距離チェック ===")
    sections = splitter.split_sections(test_text_distance)
    print(f"検出された大問数: {len(sections)}")
    for i, section in enumerate(sections):
        print(f"大問{i+1}: 文字数 {len(section.text)}")

if __name__ == "__main__":
    test_dialectical_improvements()