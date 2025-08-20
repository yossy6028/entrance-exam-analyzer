#\!/usr/bin/env python3
"""
セクション分割と文字数カウントのデバッグ
"""
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.section_splitter_v2 import ImprovedSectionSplitter
from modules.universal_analyzer import UniversalAnalyzer

def test_section_splitting():
    """セクション分割をテスト"""
    
    # テスト用テキスト（実際の問題を模倣）
    test_text = """
一、次の文章を読んで、後の問いに答えなさい。

これは大問1の文章です。ここには1000文字以上の長い文章が入ります。
""" + ("テスト文章" * 200) + """

問一　この文章の主題は何ですか。
問二　著者の意図を説明しなさい。

二、次の文章を読んで、後の問いに答えなさい。

これは大問2の文章です。ここにも長い文章が入ります。
""" + ("別のテスト文章" * 300) + """

問一　この文章の要点を述べなさい。
問二　登場人物の心情を説明しなさい。

三、次の漢字の読みを答えなさい。

１．難解
２．邂逅
３．憧憬
"""
    
    # セクション分割をテスト
    splitter = ImprovedSectionSplitter(min_section_length=100)
    sections = splitter.split_sections(test_text)
    
    print("=" * 60)
    print("セクション分割結果")
    print("=" * 60)
    
    for section in sections:
        # 実際の文字数を計算（空白と改行を除く）
        actual_chars = len(section.text.replace(' ', '').replace('\n', '')) if section.text else 0
        content_chars = len(section.content.replace(' ', '').replace('\n', '')) if section.content else 0
        
        print(f"\n【セクション {section.number}】")
        print(f"タイトル: {section.title}")
        print(f"content文字数: {content_chars}")
        print(f"text文字数: {actual_chars}")
        print(f"設問数: {section.question_count}")
        print(f"contentの最初50文字: {section.content[:50] if section.content else 'なし'}")
        print(f"textの最初50文字: {section.text[:50] if section.text else 'なし'}")
    
    # UniversalAnalyzerでも分析
    print("\n" + "=" * 60)
    print("UniversalAnalyzerの分析結果")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    result = analyzer.analyze(test_text, "テスト学校", "2025")
    
    print(f"総文字数: {result.total_characters}")
    print(f"セクション数: {len(result.sections)}")
    
    for i, section in enumerate(result.sections, 1):
        # セクションの文字数を正確に計算
        if hasattr(section, 'text') and section.text:
            actual_chars = len(section.text.replace(' ', '').replace('\n', ''))
        elif hasattr(section, 'content') and section.content:
            actual_chars = len(section.content.replace(' ', '').replace('\n', ''))
        else:
            actual_chars = 0
            
        print(f"\nセクション{i}:")
        print(f"  文字数: {actual_chars}")
        print(f"  設問数: {section.question_count if hasattr(section, 'question_count') else 'N/A'}")

if __name__ == "__main__":
    test_section_splitting()