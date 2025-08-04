#!/usr/bin/env python3
"""
修正版アプリケーションのテスト
BunkoOCRのキーボードナビゲーション機能をテスト
"""
import sys
from pathlib import Path

def test_app():
    """修正版アプリケーションをテスト"""
    
    print("🧪 修正版入試問題分析アプリケーションのテスト開始")
    print("=" * 80)
    
    print("\n📋 テスト内容:")
    print("1. 過去問フォルダから学校リストを動的生成")
    print("2. 学校別の利用可能な年度を表示")
    print("3. 複数年度選択機能")
    print("4. PDFファイルの自動特定")
    print("5. BunkoOCRのキーボードナビゲーション起動")
    print("6. ファイルダイアログでの自動選択")
    
    print("\n🚀 アプリケーションを起動中...")
    
    # GUI版とCLI版を選択
    choice = input("\nどちらをテストしますか？ (1: GUI版, 2: CLI版): ")
    
    if choice == "1":
        print("\n✅ GUI版を起動します")
        try:
            from entrance_exam_app import main
            main()
        except ImportError:
            print("❌ tkinterがインストールされていません")
            print("   CLI版を起動します...")
            from entrance_exam_app_cli import main
            main()
    else:
        print("\n✅ CLI版を起動します")
        from entrance_exam_app_cli import main
        main()
    
    print("\n🎉 テスト完了！")

if __name__ == "__main__":
    test_app()