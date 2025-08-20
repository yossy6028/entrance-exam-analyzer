#!/usr/bin/env python3
"""
改善されたテーマ抽出システムの総合テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.improved_theme_extractor import ImprovedThemeExtractor
from modules.universal_analyzer import UniversalAnalyzer


def test_ocr_noise_removal():
    """OCRノイズ除去のテスト"""
    print("=" * 60)
    print("🧹 OCRノイズ除去テスト")
    print("=" * 60)
    
    extractor = ImprovedThemeExtractor()
    
    test_cases = [
        {
            'input': '''
            受験番号: 2025001 採点欄: 
            この人物について述べている。下線①について答えなさい。
            友達と一緒に過ごした楽しい思い出を振り返る。
            まちがっている文章を選択しなさい。
            ''',
            'expected_clean_keywords': ['友達', '一緒', '楽しい', '思い出']
        },
        {
            'input': '''
            解答用紙 氏名欄: 学校名: ○○中学校
            あらわしている内容について。
            自然の美しさを感じながら、森の中を歩いた。
            動物たちと共に生きる環境の大切さを学んだ。
            正しい文章を選択しなさい。
            ''',
            'expected_clean_keywords': ['自然', '美しさ', '森', '動物', '環境', '大切さ']
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        print(f"入力テキスト: {case['input'][:100]}...")
        
        clean_text, noise_removed = extractor.clean_ocr_noise(case['input'])
        
        print(f"除去されたノイズ: {noise_removed}")
        print(f"クリーンテキスト: {clean_text}")
        
        # 期待されるキーワードが残っているかチェック
        keywords_preserved = all(
            keyword in clean_text for keyword in case['expected_clean_keywords']
        )
        
        # ノイズが除去されているかチェック
        noise_removed_check = all(
            noise not in clean_text.lower() 
            for noise in ['受験番号', '採点欄', 'この人物について', 'あらわしている']
        )
        
        if keywords_preserved and noise_removed_check:
            print("✅ OCRノイズ除去成功")
            success_count += 1
        else:
            print("❌ OCRノイズ除去失敗")
            if not keywords_preserved:
                print("  - 重要キーワードが除去されました")
            if not noise_removed_check:
                print("  - ノイズが残っています")
    
    print(f"\n📊 OCRノイズ除去結果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)


def test_reference_content_extraction():
    """参照コンテンツ抽出のテスト"""
    print("\n" + "=" * 60)
    print("🔗 参照コンテンツ抽出テスト")
    print("=" * 60)
    
    extractor = ImprovedThemeExtractor()
    
    test_cases = [
        {
            'input': '''
            次の文章を読んで、下線①について答えなさい。
            
            太郎は毎日友達と一緒に学校に通っている。①彼らの友情は深く、
            互いに助け合いながら困難を乗り越えてきた。そんな二人の絆は
            とても強いものだった。
            
            下線①について、最も適切な説明を選びなさい。
            ''',
            'expected_references': {
                '下線①': '彼らの友情は深く、互いに助け合いながら困難を乗り越えてきた'
            }
        },
        {
            'input': '''
            傍線部アについて説明しなさい。
            
            科学技術の発展により、ア私たちの生活は大きく変化している。
            AIやロボットが普及し、未来への可能性が広がっている。
            
            傍線部アの内容を60字以内で説明しなさい。
            ''',
            'expected_references': {
                '傍線部ア': '私たちの生活は大きく変化している'
            }
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        print(f"入力テキスト: {case['input'][:150]}...")
        
        reference_content = extractor.extract_reference_content(case['input'])
        
        print(f"抽出された参照コンテンツ: {reference_content}")
        
        # 期待される参照が抽出されているかチェック
        success = True
        for expected_marker, expected_content_part in case['expected_references'].items():
            if expected_marker not in reference_content:
                print(f"❌ マーカー '{expected_marker}' が見つかりません")
                success = False
            else:
                extracted_content = reference_content[expected_marker]
                if expected_content_part not in extracted_content:
                    print(f"❌ 期待されるコンテンツが含まれていません: {expected_content_part}")
                    success = False
                else:
                    print(f"✅ 正しく抽出: {extracted_content}")
        
        if success:
            success_count += 1
    
    print(f"\n📊 参照コンテンツ抽出結果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)


def test_advanced_theme_detection():
    """改善されたテーマ検出のテスト"""
    print("\n" + "=" * 60)
    print("🎯 改善されたテーマ検出テスト")
    print("=" * 60)
    
    extractor = ImprovedThemeExtractor()
    
    test_cases = [
        {
            'input': '''
            受験番号: 12345
            この人物について述べなさい。
            私と友達の田中は小学校時代からの親友だった。
            一緒に遊び、一緒に勉強し、困った時は助け合ってきた。
            友情の絆は年月を重ねるごとに深まっていった。
            下線①について答えなさい。
            ''',
            'expected_theme': '友情・人間関係',
            'min_confidence': 60.0
        },
        {
            'input': '''
            解答用紙
            あらわしている内容について答えよ。
            森の中を歩いていると、様々な動物たちの声が聞こえてくる。
            自然環境の豊かさを感じながら、地球の生態系について考えた。
            環境保護の重要性を改めて実感した瞬間だった。
            ''',
            'expected_theme': '自然・環境',
            'min_confidence': 50.0
        },
        {
            'input': '''
            まちがっている文章を選択しなさい。
            AI技術の急速な発展により、ロボットが様々な分野で活躍している。
            科学研究の成果として、未来の可能性が大きく広がっている。
            技術革新は私たちの生活を便利にし、新しい時代を切り開いている。
            若くして結婚した人物の話。
            ''',
            'expected_theme': '科学・技術・未来',
            'min_confidence': 40.0
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        print(f"入力テキスト: {case['input'][:150]}...")
        
        result = extractor.analyze_text(case['input'])
        
        print(f"検出されたテーマ: {result.theme}")
        print(f"信頼度: {result.confidence:.1f}%")
        print(f"期待されたテーマ: {case['expected_theme']}")
        print(f"除去されたノイズ: {len(result.noise_removed)}個")
        
        if (result.theme == case['expected_theme'] and 
            result.confidence >= case['min_confidence']):
            print("✅ テーマ検出成功")
            success_count += 1
        else:
            print("❌ テーマ検出失敗")
            if result.theme != case['expected_theme']:
                print(f"  - テーマが不一致: {result.theme} != {case['expected_theme']}")
            if result.confidence < case['min_confidence']:
                print(f"  - 信頼度が低すぎます: {result.confidence:.1f}% < {case['min_confidence']}%")
    
    print(f"\n📊 テーマ検出結果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)


def test_integration_with_universal_analyzer():
    """UniversalAnalyzerとの統合テスト"""
    print("\n" + "=" * 60)
    print("🔄 UniversalAnalyzer統合テスト")
    print("=" * 60)
    
    analyzer = UniversalAnalyzer()
    
    test_text = '''
    受験番号: 2025001 採点欄:
    この人物について述べている。下線①について答えなさい。
    
    私の祖父は昔から自然を愛する人だった。①森の中を歩きながら、
    様々な動物たちの生態を観察し、環境保護の大切さを教えてくれた。
    
    下線①の内容について最も適切なものを選びなさい。
    まちがっている文章を選択しなさい。
    '''
    
    try:
        result = analyzer.analyze(test_text, "テスト中学校", "2025")
        
        print(f"分析結果:")
        print(f"  テーマ: {result.theme}")
        print(f"  ジャンル: {result.genre}")
        # char_countがない場合は、テキスト長で代用
        char_count = getattr(result, 'char_count', len(test_text))
        print(f"  文字数: {char_count}")
        
        # テーマが適切に検出されているかチェック
        expected_themes = ['自然・環境', '家族・親子', '家族・親子関係']
        if result.theme in expected_themes:
            print("✅ 統合テスト成功")
            return True
        else:
            print(f"❌ 統合テスト失敗: 期待されるテーマ {expected_themes} に含まれていません")
            return False
            
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        return False


def run_all_tests():
    """すべてのテストを実行"""
    print("🚀 改善されたテーマ抽出システム 総合テスト開始")
    print("=" * 80)
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("OCRノイズ除去", test_ocr_noise_removal()))
    test_results.append(("参照コンテンツ抽出", test_reference_content_extraction()))
    test_results.append(("改善されたテーマ検出", test_advanced_theme_detection()))
    test_results.append(("UniversalAnalyzer統合", test_integration_with_universal_analyzer()))
    
    # 結果サマリー
    print("\n" + "=" * 80)
    print("📊 テスト結果サマリー")
    print("=" * 80)
    
    success_count = 0
    for test_name, success in test_results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    total_tests = len(test_results)
    print(f"\n総合結果: {success_count}/{total_tests} のテストが成功")
    
    if success_count == total_tests:
        print("🎉 すべてのテストが成功しました！")
        print("改善されたテーマ抽出システムは正常に動作しています。")
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("該当する機能の見直しが必要です。")
    
    return success_count == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🔧 次のステップ:")
        print("1. 実際のPDFファイルでの動作確認")
        print("2. 既存のExcel出力データとの比較検証")
        print("3. パフォーマンスの最適化")
    else:
        print("\n🔧 修正が必要な項目:")
        print("1. 失敗したテストケースの詳細分析")
        print("2. アルゴリズムの改善")
        print("3. エラーハンドリングの強化")
    
    sys.exit(0 if success else 1)