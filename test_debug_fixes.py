#!/usr/bin/env python3
"""
分析結果不完全問題の修正をテストするスクリプト
"""

import sys
import os
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.universal_analyzer import UniversalAnalyzer
from models import Section


def test_char_count_setting():
    """char_count設定のテスト"""
    print("=" * 60)
    print("🔍 char_count設定のテスト")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    
    # テスト用のサンプルテキスト
    sample_text = """
一、次の文章を読んで、後の問いに答えなさい。

これは文章読解問題のテストです。
ここに長い文章が続きます。

問1 この文章の内容について答えなさい。
問2 筆者の考えを記号で答えなさい。
　ア　賛成　　イ　反対　　ウ　どちらでもない

二、次の漢字の読み方を答えなさい。

1　美しい → 美しい
2　強い → 強い
    """
    
    # 分析実行
    result = analyzer.analyze(sample_text, "テスト中学校", "2025")
    
    # セクションのchar_count確認
    success_count = 0
    total_sections = len(result.sections)
    
    for i, section in enumerate(result.sections, 1):
        print(f"\n大問{i}:")
        print(f"  タイトル: {section.title}")
        print(f"  セクションタイプ: {getattr(section, 'section_type', 'なし')}")
        print(f"  文字数: {getattr(section, 'char_count', 'なし')}")
        print(f"  文章問題: {getattr(section, 'is_text_problem', 'なし')}")
        print(f"  設問数: {section.question_count}")
        
        if hasattr(section, 'char_count') and section.char_count is not None:
            if section.char_count > 0:
                success_count += 1
                print(f"  ✅ 文字数が正常に設定されています: {section.char_count}")
            else:
                print(f"  ❌ 文字数が0です")
        else:
            print(f"  ❌ char_countが設定されていません")
    
    print(f"\n📊 結果: {success_count}/{total_sections} のセクションで文字数が正常に設定されました")
    return success_count == total_sections


def test_theme_genre_detection():
    """テーマ・ジャンル検出のテスト"""
    print("\n" + "=" * 60)
    print("🎯 テーマ・ジャンル検出のテスト")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    
    test_cases = [
        {
            'text': '私の小さいころの体験について書きます。友達と一緒に遊んだ思い出があります。',
            'expected_theme': '人間関係・成長',
            'expected_genre': '随筆・エッセイ'
        },
        {
            'text': '環境問題について考察する。地球温暖化は深刻な問題である。',
            'expected_theme': '自然・環境',
            'expected_genre': '評論・論説'
        },
        {
            'text': '「おはよう」と太郎は言った。「今日はいい天気ですね」と花子は答えた。',
            'expected_theme': None,
            'expected_genre': '小説・物語'
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nテストケース {i}:")
        print(f"  テキスト: {case['text'][:50]}...")
        
        result = analyzer.analyze(case['text'], "テスト中学校", "2025")
        
        detected_theme = result.theme
        detected_genre = result.genre
        
        print(f"  検出されたテーマ: {detected_theme}")
        print(f"  期待されたテーマ: {case['expected_theme']}")
        print(f"  検出されたジャンル: {detected_genre}")
        print(f"  期待されたジャンル: {case['expected_genre']}")
        
        theme_match = detected_theme == case['expected_theme']
        genre_match = detected_genre == case['expected_genre']
        
        if theme_match and genre_match:
            print("  ✅ テーマとジャンルが正しく検出されました")
            success_count += 1
        else:
            if not theme_match:
                print("  ❌ テーマの検出が不正確")
            if not genre_match:
                print("  ❌ ジャンルの検出が不正確")
    
    print(f"\n📊 結果: {success_count}/{len(test_cases)} のテストケースが成功")
    return success_count == len(test_cases)


def test_question_detail_analysis():
    """設問詳細分析のテスト"""
    print("\n" + "=" * 60)
    print("📝 設問詳細分析のテスト")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    
    # 詳細な設問を含むテキスト
    detailed_text = """
一、次の文章を読んで答えなさい。

問1　内容を30字以内で答えなさい。
問2　筆者の考えを記号で答えなさい。
　ア　賛成　　イ　反対　　ウ　分からない　　エ　その他
問3　本文から適切な語句を抜き出しなさい。
問4　あなたの意見を50字程度で述べなさい。

二、漢字問題

1～5　次の漢字の読みを答えなさい。
    """
    
    result = analyzer.analyze(detailed_text, "テスト中学校", "2025")
    
    # 詳細分析結果を確認
    print(f"設問タイプ別:")
    for q_type, count in result.question_types.items():
        if count > 0:
            print(f"  {q_type}: {count}問")
    
    # 詳細情報の確認
    if hasattr(result, 'word_limit_details'):
        print(f"\n文字数制限詳細: {result.word_limit_details}")
    
    if hasattr(result, 'choice_type_details'):
        print(f"選択肢詳細: {result.choice_type_details}")
    
    if hasattr(result, 'extract_details'):
        print(f"抜き出し詳細: {result.extract_details}")
    
    # 成功条件のチェック
    has_details = any([
        hasattr(result, 'word_limit_details') and result.word_limit_details,
        hasattr(result, 'choice_type_details') and result.choice_type_details,
        hasattr(result, 'extract_details') and result.extract_details
    ])
    
    if has_details:
        print("\n✅ 設問詳細分析が正常に動作しています")
        return True
    else:
        print("\n❌ 設問詳細分析に問題があります")
        return False


def main():
    """メインテスト実行"""
    print("🤖 分析結果不完全問題の修正テスト開始")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("char_count設定", test_char_count_setting()))
    test_results.append(("テーマ・ジャンル検出", test_theme_genre_detection()))
    test_results.append(("設問詳細分析", test_question_detail_analysis()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📋 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 総合結果: {passed}/{len(test_results)} テストが成功")
    
    if passed == len(test_results):
        print("🎉 すべてのテストが成功しました！修正は完了です。")
        return True
    else:
        print("⚠️  いくつかのテストが失敗しています。追加の修正が必要です。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)