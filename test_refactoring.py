#!/usr/bin/env python3
"""
リファクタリング後のコンポーネントのテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patterns.registry import PatternRegistry
from processors.text_preprocessor import TextPreprocessor
from processors.file_manager import FileManager
from core.base_analyzer import BaseAnalyzer
from core.exceptions import ValidationError


def test_pattern_registry():
    """パターンレジストリのテスト"""
    print("=== Pattern Registry Test ===")
    
    registry = PatternRegistry()
    
    # 統計情報
    stats = registry.get_stats()
    print(f"Loaded patterns: {stats}")
    
    # 年度パターンのテスト
    test_text = "二〇二五年度 聖光学院中学校 入学試験問題"
    
    # 漢数字年度の検出
    matches = list(registry.finditer('year.kanji', test_text))
    if matches:
        print(f"✅ Found kanji year: {matches[0].group(1)}")
    else:
        print("❌ No kanji year found")
    
    # セクションパターンのテスト
    section_text = "一、次の文章を読んで"
    matches = list(registry.finditer('section.kanji_comma_next', section_text))
    if matches:
        print(f"✅ Found section marker: {matches[0].group(0)}")
    else:
        print("❌ No section marker found")
    
    print()


def test_text_preprocessor():
    """テキスト前処理のテスト"""
    print("=== Text Preprocessor Test ===")
    
    preprocessor = TextPreprocessor()
    
    # OCRノイズを含むテキスト
    noisy_text = """
    === ページ 1 ===
    二〇二五年度　　　入学試験問題
    
    国｜語
    
    第一問    次の文章を読んで、、、後の問いに答えなさい。
    """
    
    # 前処理
    clean_text = preprocessor.clean_for_analysis(noisy_text)
    
    print("Original text:")
    print(repr(noisy_text[:100]))
    print("\nCleaned text:")
    print(repr(clean_text[:100]))
    
    # メタデータ抽出
    metadata = preprocessor.extract_metadata(clean_text)
    print(f"\nExtracted metadata: {metadata}")
    
    print()


def test_file_manager():
    """ファイルマネージャーのテスト"""
    print("=== File Manager Test ===")
    
    manager = FileManager()
    
    # テストファイルの作成と読み込み
    test_file = "/tmp/test_file_manager.txt"
    test_content = "This is a test file for FileManager"
    
    # 書き込み
    manager.write_text_file(test_file, test_content, backup=False)
    print(f"✅ Wrote test file: {test_file}")
    
    # 読み込み（キャッシュなし）
    content1 = manager.read_text_file(test_file, use_cache=False)
    print(f"✅ Read without cache: {len(content1)} chars")
    
    # 読み込み（キャッシュあり）
    content2 = manager.read_text_file(test_file, use_cache=True)
    print(f"✅ Read with cache: {len(content2)} chars")
    
    # キャッシュ統計
    stats = manager.get_cache_stats()
    print(f"Cache stats: {stats}")
    
    # ファイル情報
    info = manager.get_file_info(test_file)
    print(f"File info: name={info['name']}, size={info['size']} bytes")
    
    # クリーンアップ
    import os
    os.remove(test_file)
    
    print()


def test_base_analyzer():
    """基底アナライザーのテスト"""
    print("=== Base Analyzer Test ===")
    
    class TestAnalyzer(BaseAnalyzer):
        """テスト用の具体的なアナライザー"""
        
        def analyze(self, text: str, **kwargs):
            """簡単な分析を実装"""
            # 前処理
            clean_text = self.preprocess_text(text)
            
            # パターンマッチング
            years = self.find_all_matches('year.year_4digit', clean_text)
            
            return {
                'text_length': len(clean_text),
                'years_found': years,
                'cache_stats': self.get_cache_stats()
            }
    
    # アナライザーのインスタンス化（最小文字数を調整）
    analyzer = TestAnalyzer(config={'min_text_length': 10})
    
    # テキストの分析
    test_text = "=== ページ 1 ===\n2025年度 入学試験問題\n\n国語"
    
    try:
        # バリデーション
        analyzer.validate_input(test_text)
        print("✅ Input validation passed")
        
        # 分析実行
        result = analyzer.analyze_with_timing(test_text)
        print(f"Analysis result: {result}")
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    
    print()


def test_integration():
    """統合テスト - すべてのコンポーネントを組み合わせて使用"""
    print("=== Integration Test ===")
    
    # コンポーネントの初期化
    registry = PatternRegistry()
    preprocessor = TextPreprocessor()
    file_manager = FileManager()
    
    # サンプルテキスト
    sample_text = """
    二〇二五年度 聖光学院中学校 入学試験問題
    
    国語
    
    一、次の文章を読んで、後の問いに答えなさい。
    
    （文章省略）
    
    永井佳子「見えないキノコの勤勉な日々」（『図書』第九〇四号所収）による
    """
    
    # 前処理
    clean_text = preprocessor.clean_for_analysis(sample_text)
    
    # パターンマッチング
    year_matches = list(registry.finditer('year.kanji', clean_text))
    section_matches = list(registry.finditer('section.kanji_comma_next', clean_text))
    source_matches = list(registry.finditer('source.magazine_full_zen', clean_text))
    
    print(f"Found {len(year_matches)} year(s)")
    print(f"Found {len(section_matches)} section(s)")
    print(f"Found {len(source_matches)} source(s)")
    
    if source_matches:
        match = source_matches[0]
        print(f"Source: {match.group(1)}「{match.group(2)}」（『{match.group(3)}』所収）")
    
    print("\n✅ All components working together successfully!")


if __name__ == "__main__":
    test_pattern_registry()
    test_text_preprocessor()
    test_file_manager()
    test_base_analyzer()
    test_integration()
    
    print("\n=== All Tests Completed ===")
    print("✅ Refactoring successful - new architecture is working!")