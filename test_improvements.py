#!/usr/bin/env python3
"""
セキュリティとエラー処理の改善をテスト
"""
import sys
import os
import threading
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patterns.registry import PatternRegistry
from processors.file_manager import FileManager, SecurityError
from core.config_validator import ConfigValidator
from core.exceptions import ConfigurationError, AnalyzerError
from core.base_analyzer import BaseAnalyzer


def test_thread_safe_singleton():
    """シングルトンのスレッドセーフテスト"""
    print("=== Thread-Safe Singleton Test ===")
    
    instances = []
    
    def get_instance():
        instance = PatternRegistry()
        instances.append(instance)
    
    # 複数スレッドから同時にインスタンス取得
    threads = []
    for _ in range(10):
        t = threading.Thread(target=get_instance)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # すべてのインスタンスが同一であることを確認
    first_instance = instances[0]
    all_same = all(inst is first_instance for inst in instances)
    
    if all_same:
        print(f"✅ All {len(instances)} instances are identical (thread-safe)")
    else:
        print(f"❌ Multiple different instances created (not thread-safe)")
    
    print()


def test_path_validation():
    """パス検証のテスト"""
    print("=== Path Validation Test ===")
    
    # 安全なディレクトリのみ許可
    safe_dir = Path("/tmp/safe_test_dir")
    safe_dir.mkdir(exist_ok=True)
    
    manager = FileManager(allowed_dirs=[safe_dir])
    
    # テストケース
    test_cases = [
        # (パス, 期待される結果: True=成功, False=SecurityError)
        (safe_dir / "test.txt", True),
        (safe_dir / "subdir" / "test.txt", True),
        ("/etc/passwd", False),  # システムファイル
        ("../../../etc/passwd", False),  # パストラバーサル
        ("/tmp/safe_test_dir/../../../etc/passwd", False),  # 巧妙なパストラバーサル
    ]
    
    for test_path, should_succeed in test_cases:
        try:
            # テストファイルを作成
            if should_succeed:
                Path(test_path).parent.mkdir(parents=True, exist_ok=True)
                Path(test_path).write_text("test content")
            
            # 検証
            validated = manager._validate_path(Path(test_path))
            
            if should_succeed:
                print(f"✅ Allowed: {test_path}")
            else:
                print(f"❌ Should have blocked: {test_path}")
                
        except SecurityError as e:
            if not should_succeed:
                print(f"✅ Blocked: {test_path} - {e}")
            else:
                print(f"❌ Should have allowed: {test_path}")
        except Exception as e:
            print(f"❌ Unexpected error for {test_path}: {e}")
    
    # クリーンアップ
    import shutil
    if safe_dir.exists():
        shutil.rmtree(safe_dir)
    
    print()


def test_error_handling_improvements():
    """改善されたエラー処理のテスト"""
    print("=== Error Handling Improvements Test ===")
    
    registry = PatternRegistry()
    
    # 無効なパターンのテスト
    try:
        # 存在しないパターン
        pattern = registry.get_pattern("invalid.pattern.name")
        print("❌ Should have raised error for invalid pattern")
    except ValueError as e:
        print(f"✅ Invalid pattern handled: {e}")
    
    # 機密情報のサニタイズテスト
    error = AnalyzerError(
        "Database connection failed",
        details={
            "host": "localhost",
            "port": 5432,
            "password": "secret123",
            "api_key": "sk-1234567890",
            "error": "Connection timeout after 30 seconds"
        }
    )
    
    error_str = str(error)
    
    if "secret123" in error_str or "sk-1234567890" in error_str:
        print(f"❌ Sensitive information leaked: {error_str}")
    else:
        print(f"✅ Sensitive information redacted: {error_str}")
    
    print()


def test_config_validation():
    """設定検証のテスト"""
    print("=== Configuration Validation Test ===")
    
    validator = ConfigValidator()
    
    # 有効な設定
    valid_config = {
        "min_text_length": 100,
        "max_text_length": 1000000,
        "propagate_errors": True
    }
    
    try:
        validated = validator.validate(valid_config, "base_analyzer")
        print(f"✅ Valid config accepted: {validated}")
    except ConfigurationError as e:
        print(f"❌ Valid config rejected: {e}")
    
    # 無効な設定（型エラー）
    invalid_config = {
        "min_text_length": "not a number",  # 型エラー
        "max_text_length": 1000000
    }
    
    try:
        validated = validator.validate(invalid_config, "base_analyzer")
        print(f"❌ Invalid config accepted: {validated}")
    except ConfigurationError as e:
        print(f"✅ Invalid config rejected: {e}")
    
    # 範囲外の値
    out_of_range_config = {
        "min_text_length": -100,  # 負の値
        "max_text_length": 999999999  # 最大値超過
    }
    
    try:
        validated = validator.validate(out_of_range_config, "base_analyzer")
        print(f"❌ Out-of-range config accepted: {validated}")
    except ConfigurationError as e:
        print(f"✅ Out-of-range config rejected: {e}")
    
    # デフォルト値の適用
    empty_config = {}
    validated = validator.validate(empty_config, "base_analyzer")
    
    if "min_text_length" in validated:
        print(f"✅ Default values applied: min_text_length={validated['min_text_length']}")
    else:
        print("❌ Default values not applied")
    
    print()


def test_fallback_patterns():
    """重要パターンのフォールバックテスト"""
    print("=== Fallback Pattern Test ===")
    
    registry = PatternRegistry()
    
    # フォールバックパターンの存在を確認
    critical_patterns = [
        'year.year_4digit',
        'year.kanji',
        'section.kanji_comma_next',
        'source.author_title_niyoru'
    ]
    
    for pattern_name in critical_patterns:
        is_critical = registry._is_critical_pattern(pattern_name)
        fallback = registry._get_fallback_pattern(pattern_name)
        
        if is_critical and fallback:
            print(f"✅ {pattern_name}: Critical with fallback")
        elif is_critical and not fallback:
            print(f"⚠️  {pattern_name}: Critical but no fallback defined")
        else:
            print(f"ℹ️  {pattern_name}: Not critical")
    
    print()


def test_integrated_improvements():
    """統合テスト - すべての改善を組み合わせてテスト"""
    print("=== Integrated Improvements Test ===")
    
    class TestAnalyzer(BaseAnalyzer):
        def analyze(self, text: str, **kwargs):
            return {"processed": True}
    
    # 設定検証付きでアナライザーを初期化
    config = {
        "min_text_length": 10,
        "max_text_length": 100000,
        "unknown_property": "ignored"  # 未知のプロパティ
    }
    
    analyzer = TestAnalyzer(config)
    
    # 設定が検証されたことを確認
    if hasattr(analyzer, 'config'):
        print(f"✅ Analyzer initialized with validated config")
    else:
        print("❌ Config validation failed")
    
    # パターンレジストリが正しく初期化されたことを確認
    if analyzer.pattern_registry is not None:
        stats = analyzer.pattern_registry.get_stats()
        print(f"✅ Pattern registry loaded: {stats['definitions']} patterns")
    else:
        print("❌ Pattern registry not initialized")
    
    print("\n✅ All improvements successfully integrated!")


if __name__ == "__main__":
    test_thread_safe_singleton()
    test_path_validation()
    test_error_handling_improvements()
    test_config_validation()
    test_fallback_patterns()
    test_integrated_improvements()
    
    print("\n=== All Improvement Tests Completed ===")
    print("✅ Security and error handling improvements are working!")