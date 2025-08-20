#!/usr/bin/env python3
"""
大問ごとの文字数異常の問題を調査
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.universal_analyzer import UniversalAnalyzer
from models import Section

def test_section_analysis():
    """セクション分析の問題を再現"""
    
    # 聖光学院の典型的なパターンを再現
    test_text = """
    二〇二五年度 聖光学院中学校 入学試験問題
    
    国語
    
    一、次の文章を読んで、後の問いに答えなさい。
    
    （ここに本来は長い文章が入る。
    普通は2000文字以上の文章が続く。
    しかし、OCRの問題で文章が切れることがある。）
    
    森沢明夫『本が紡いだ五つの奇跡』による
    
    問一　傍線部①「それ」とは何を指しますか。
    問二　傍線部②について、筆者の考えを説明しなさい。
    問三　この文章の主題を60字以内で書きなさい。
    
    二、次の文章を読んで、後の問いに答えなさい。
    
    （第二の文章もここに入る。
    こちらも通常2000文字以上。）
    
    永井佳子「見えないキノコの勤勉な日々」（『図書』第九〇四号所収）による
    
    問一　漢字の読みを答えなさい。
    問二　空欄に入る語句を選びなさい。
    
    三、次の漢字・語句の問題に答えなさい。
    
    問一　次の漢字の読みをひらがなで書きなさい。
    　１　蓄積
    　２　潤沢
    　３　融和
    　４　執筆
    　５　簡潔
    
    問二　次のカタカナを漢字に直しなさい。
    　１　キョウリョク
    　２　シンチョウ
    　３　カンサツ
    
    四、次の文章を読んで、後の問いに答えなさい。
    
    （短い文章や詩が入ることがある）
    
    問一　この詩の形式を答えなさい。
    """
    
    # 分析実行
    analyzer = UniversalAnalyzer()
    result = analyzer.analyze(test_text, '聖光学院中学校', '2025')
    
    print("=== セクション分析結果 ===")
    print(f"総文字数: {result.total_characters}")
    print(f"大問数: {len(result.sections)}")
    
    for i, section in enumerate(result.sections, 1):
        text_length = len(section.text) if hasattr(section, 'text') else len(section.content)
        print(f"\n大問{i}: {section.title}")
        print(f"  文字数: {text_length}")
        
        # 文字数が異常に少ない場合の警告
        if text_length < 100:
            print(f"  ⚠️ 警告: 文字数が異常に少ない！")
            content = section.text[:200] if hasattr(section, 'text') else section.content[:200]
            print(f"  内容プレビュー: {repr(content)}")
    
    # 問題の診断
    print("\n=== 診断 ===")
    
    # 大問の文字数の分布を確認
    char_counts = []
    for section in result.sections:
        text_length = len(section.text) if hasattr(section, 'text') else len(section.content)
        char_counts.append(text_length)
    
    if char_counts:
        avg_chars = sum(char_counts) / len(char_counts)
        min_chars = min(char_counts)
        max_chars = max(char_counts)
        
        print(f"平均文字数: {avg_chars:.0f}")
        print(f"最小文字数: {min_chars}")
        print(f"最大文字数: {max_chars}")
        
        # 異常検出
        if min_chars < 100:
            print("\n❌ 問題検出: 100文字未満の大問があります")
            print("  原因の可能性:")
            print("  1. セクション分割が不適切")
            print("  2. OCRテキストの欠損")
            print("  3. ページ境界での分断")
        
        if max_chars / min_chars > 20:
            print("\n❌ 問題検出: 大問間の文字数の差が大きすぎます")
            print("  原因の可能性:")
            print("  1. 複数の大問が結合されている")
            print("  2. 小問が大問として誤認識されている")


def test_section_detection_patterns():
    """セクション検出パターンのテスト"""
    
    print("\n=== セクション検出パターンテスト ===")
    
    test_cases = [
        ("一、次の文章を読んで", True, "標準的な大問開始"),
        ("二、次の文章を読んで", True, "第二の大問"),
        ("三、次の漢字の", True, "漢字問題の大問"),
        ("四、次の問いに", True, "第四の大問"),
        ("問一　これは", False, "小問（大問ではない）"),
        ("問二　それは", False, "小問（大問ではない）"),
        ("第一問　次の", True, "別形式の大問"),
        ("大問一　", True, "明示的な大問表記"),
    ]
    
    analyzer = UniversalAnalyzer()
    
    for text, should_be_section, description in test_cases:
        # パターンマッチングのテスト
        is_section = False
        
        # 大問マーカーのパターンチェック
        import re
        major_patterns = [
            r'^([一二三四五六七八九十])[、，]\s*次の',
            r'^大問\s*([一二三四五六七八九十])',
            r'^第([一二三四五六七八九十])問',
        ]
        
        for pattern in major_patterns:
            if re.match(pattern, text.strip()):
                is_section = True
                break
        
        # 小問パターンのチェック（除外用）
        if text.startswith('問') and '次の' not in text:
            is_section = False
        
        status = "✅" if is_section == should_be_section else "❌"
        print(f"{status} '{text}' -> {is_section} ({description})")


if __name__ == "__main__":
    test_section_analysis()
    test_section_detection_patterns()
    
    print("\n=== テスト完了 ===")
    print("大問の文字数異常は、主にセクション分割の問題が原因と考えられます。")