#!/usr/bin/env python3
"""
修正されたBunkoOCR起動機能のテスト
指定されたPDFファイルを正しくBunkoOCRで開けるかテスト
"""
import sys
import time
from pathlib import Path

# 既存モジュールのインポート
sys.path.append(str(Path(__file__).parent))
from entrance_exam_app_cli import EntranceExamAnalyzerCLI

def test_bunko_launch():
    """修正されたBunkoOCR起動機能をテスト"""
    
    # テスト用のPDFファイルパス
    test_pdf = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/2023過去問/23女子学院/kokugo-mondai (1).pdf"
    
    print("🧪 BunkoOCR起動機能テスト開始")
    print(f"対象ファイル: {test_pdf}")
    print("=" * 80)
    
    # ファイル存在確認
    if not Path(test_pdf).exists():
        print(f"❌ エラー: ファイルが見つかりません: {test_pdf}")
        return False
    
    # アプリ初期化
    app = EntranceExamAnalyzerCLI()
    
    try:
        print("\n1️⃣ BunkoOCR起動機能をテスト中...")
        app.launch_bunko_with_file(test_pdf)
        
        print("\n✅ 起動機能のテスト完了")
        print("\n📋 次の手順:")
        print("1. BunkoOCRが起動し、PDFが表示されているか確認")
        print("2. 画面下部の「OCR」ボタンをクリック")
        print("3. 処理完了まで待機（2-3分）")
        print("4. python check_latest_bunko_result.py で結果確認")
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bunko_launch()
    
    if success:
        print("\n🎉 テスト成功！")
    else:
        print("\n💥 テスト失敗")
        sys.exit(1)