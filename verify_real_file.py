#!/usr/bin/env python3
"""
実際のファイルで修正を検証するスクリプト
"""

import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.universal_analyzer import UniversalAnalyzer

def test_with_real_text():
    """実際のテキストで検証"""
    print("🔍 実際のテキストファイルでの検証")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    
    # サンプルテキスト（桜蔭中学などを模擬）
    sample_text = """
一、次の文章を読んで、後の問いに答えなさい。

　春という季節は、多くの人々にとって新しい始まりを象徴するものである。桜の花が咲き誇り、新緑が芽吹く中で、私たちは希望に満ちた気持ちで新年度を迎える。しかし、この美しい季節にも、見過ごされがちな環境問題が潜んでいることを忘れてはならない。

問1　この文章の内容を30字以内で要約しなさい。
問2　筆者の考えに最も近いものを記号で答えなさい。
　ア　春は環境問題を考える良い機会である
　イ　春の美しさばかりに気を取られてはいけない
　ウ　新年度は希望を持って迎えるべきである
　エ　桜と新緑は日本の象徴である

二、次の漢字の読み方を答えなさい。

1～8　次の漢字の読み方をひらがなで書きなさい。
1　象徴
2　芽吹く
3　見過ごす
4　潜む
5　忘却
6　美麗
7　季節
8　希望

三、次の問いに答えなさい。

問1　本文から「環境」を含む語句を抜き出しなさい。
問2　あなたの考えを80字程度で述べなさい。

（出典：山田太郎『春の随想』より）
    """
    
    # 分析実行
    result = analyzer.analyze(sample_text, "桜蔭中学校", "2025")
    
    print("🎯 分析結果:")
    print(f"学校名: {result.school_name}")
    print(f"年度: {result.year}")
    print(f"総文字数: {result.total_characters:,}")
    print(f"テーマ: {result.theme}")
    print(f"ジャンル: {result.genre}")
    
    print(f"\n📚 大問情報:")
    for i, section in enumerate(result.sections, 1):
        print(f"  大問{i}: {section.title}")
        print(f"    文字数: {getattr(section, 'char_count', '未設定')}")
        print(f"    セクションタイプ: {getattr(section, 'section_type', '未設定')}")
        print(f"    文章問題: {getattr(section, 'is_text_problem', '未設定')}")
        print(f"    設問数: {section.question_count}")
    
    print(f"\n📝 設問タイプ別:")
    for q_type, count in result.question_types.items():
        if count > 0:
            print(f"  {q_type}: {count}問")
    
    print(f"\n📖 出典:")
    for i, source in enumerate(result.sources, 1):
        if source.author or source.title:
            author_part = source.author if source.author else ""
            title_part = f"『{source.title}』" if source.title else ""
            print(f"  {i}. {author_part}{title_part}")
    
    # 詳細情報
    if hasattr(result, 'word_limit_details') and result.word_limit_details:
        print(f"\n📏 文字数制限詳細:")
        for limit, count in result.word_limit_details.items():
            print(f"  {limit}: {count}問")
    
    if hasattr(result, 'choice_type_details') and result.choice_type_details:
        print(f"\n🔤 選択肢詳細:")
        for choice_type, details in result.choice_type_details.items():
            print(f"  {choice_type}: {details}")
    
    if hasattr(result, 'extract_details') and result.extract_details:
        print(f"\n📎 抜き出し詳細:")
        for extract_type, count in result.extract_details.items():
            if count > 0:
                print(f"  {extract_type}: {count}問")
    
    # 検証ポイント
    print(f"\n✅ 検証ポイント:")
    success_points = 0
    total_points = 6
    
    # 1. char_countが設定されているか
    all_sections_have_char_count = all(
        hasattr(section, 'char_count') and section.char_count is not None and section.char_count > 0
        for section in result.sections
    )
    if all_sections_have_char_count:
        print("  ✅ すべてのセクションでchar_countが正常に設定")
        success_points += 1
    else:
        print("  ❌ char_countの設定に問題")
    
    # 2. テーマが検出されているか
    if result.theme:
        print(f"  ✅ テーマが検出: {result.theme}")
        success_points += 1
    else:
        print("  ❌ テーマが検出されていない")
    
    # 3. ジャンルが検出されているか
    if result.genre:
        print(f"  ✅ ジャンルが検出: {result.genre}")
        success_points += 1
    else:
        print("  ❌ ジャンルが検出されていない")
    
    # 4. 出典が検出されているか
    if result.sources:
        print(f"  ✅ 出典が検出: {len(result.sources)}件")
        success_points += 1
    else:
        print("  ❌ 出典が検出されていない")
    
    # 5. 設問タイプが分析されているか
    if result.question_types and sum(result.question_types.values()) > 0:
        print(f"  ✅ 設問タイプが分析: {sum(result.question_types.values())}問")
        success_points += 1
    else:
        print("  ❌ 設問タイプの分析に問題")
    
    # 6. 詳細分析が動作しているか
    has_detailed_analysis = any([
        hasattr(result, 'word_limit_details') and result.word_limit_details,
        hasattr(result, 'choice_type_details') and result.choice_type_details,
        hasattr(result, 'extract_details') and result.extract_details and any(result.extract_details.values())
    ])
    if has_detailed_analysis:
        print("  ✅ 詳細分析が動作")
        success_points += 1
    else:
        print("  ❌ 詳細分析に問題")
    
    print(f"\n🎯 総合評価: {success_points}/{total_points} ポイント")
    
    if success_points == total_points:
        print("🎉 すべての機能が正常に動作しています！")
        return True
    else:
        print("⚠️ 一部機能に問題があります。")
        return False


if __name__ == "__main__":
    success = test_with_real_text()
    sys.exit(0 if success else 1)