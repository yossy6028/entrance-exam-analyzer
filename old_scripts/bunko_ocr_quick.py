#!/usr/bin/env python3
"""
bunkoOCR クイック処理スクリプト
30秒でテキスト化が完了することを前提にした効率的な処理
"""
import subprocess
import time
from pathlib import Path
import os


def quick_ocr_process(pdf_path: str):
    """bunkoOCRで高速OCR処理"""
    
    print("\n" + "="*60)
    print("bunkoOCR クイック処理")
    print("="*60)
    
    bunko_app = "/Applications/bunkoOCR.app"
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    
    # ファイル確認
    if not os.path.exists(pdf_path):
        print(f"❌ ファイルが見つかりません: {pdf_path}")
        return None
    
    print(f"\n📄 対象: {os.path.basename(pdf_path)}")
    print(f"📏 サイズ: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
    
    # 処理開始前の状態を記録
    before_dirs = set(results_dir.iterdir()) if results_dir.exists() else set()
    
    # bunkoOCRで開く
    print("\n🚀 bunkoOCRを起動...")
    subprocess.run(["open", "-a", bunko_app, pdf_path])
    
    print("\n⏱️  処理時間: 約30秒")
    print("   ", end="", flush=True)
    
    # 30秒待機（プログレスバー表示）
    for i in range(30):
        print("■", end="", flush=True)
        time.sleep(1)
    
    print(" 完了!")
    
    # 結果を確認
    print("\n🔍 結果を検索中...")
    time.sleep(5)  # ファイル生成の余裕を持たせる
    
    current_dirs = set(results_dir.iterdir()) if results_dir.exists() else set()
    new_dirs = current_dirs - before_dirs
    
    if new_dirs:
        latest_dir = max(new_dirs, key=lambda x: x.stat().st_mtime)
        print(f"✅ 新しい結果: {latest_dir.name}")
        
        # テキストファイルを確認
        text_files = list(latest_dir.glob("text*.txt"))
        if text_files:
            print(f"📄 {len(text_files)}個のテキストファイルを検出")
            
            # 最初のファイルの内容を少し表示
            with open(text_files[0], 'r', encoding='utf-8') as f:
                preview = f.read(200)
                print(f"\n【プレビュー】")
                print(preview[:100] + "..." if len(preview) > 100 else preview)
            
            return latest_dir
    else:
        print("⚠️  新しい結果が見つかりません")
        print("\nbunkoOCRの「OCR結果」メニューを確認してください")
    
    return None


def show_results_guide():
    """結果の確認方法をガイド"""
    
    print("\n" + "="*60)
    print("📖 bunkoOCR結果の確認ガイド")
    print("="*60)
    
    print("\n【bunkoOCRでの確認】")
    print("1. bunkoOCRのメニューバーから「OCR結果」を選択")
    print("2. リストの最下部が最新の処理結果")
    print("3. クリックしてテキストを確認")
    print("4. Command+S でテキストファイルとして保存")
    
    print("\n【iCloudでの確認】")
    print("場所: ~/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results/")
    print("1. 最新のフォルダを開く")
    print("2. text0.txt, text1.txt... がページごとのテキスト")
    print("3. result0.json, result1.json... が構造情報")


def process_multiple_files():
    """複数ファイルの処理例"""
    
    base_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問")
    
    # 処理したいファイルのリスト
    files_to_process = [
        base_path / "渋渋/15渋渋.pdf",
        base_path / "桜蔭/15桜蔭.pdf",  # 既にテキストファイルあり
        # 必要に応じて追加
    ]
    
    print("\n📦 複数ファイル処理モード")
    
    for i, pdf_path in enumerate(files_to_process, 1):
        if pdf_path.exists():
            print(f"\n[{i}/{len(files_to_process)}] {pdf_path.name}")
            
            # 既存のテキストファイルをチェック
            txt_path = pdf_path.with_suffix('.txt')
            if txt_path.exists():
                print(f"   ✅ 既にテキストファイルが存在: {txt_path.name}")
                continue
            
            # OCR処理
            result = quick_ocr_process(str(pdf_path))
            
            if i < len(files_to_process):
                print("\n続行しますか？ (Enter/n): ", end="")
                if input().lower() == 'n':
                    break
        else:
            print(f"\n[{i}] ❌ ファイルなし: {pdf_path.name}")


def main():
    """メイン実行"""
    
    print("bunkoOCR クイック処理システム")
    print("処理時間: 約30秒/ファイル")
    
    # 選択
    print("\n1. 渋渋15年度のみ処理")
    print("2. 複数ファイル処理")
    print("3. 結果確認ガイドを表示")
    
    # デフォルトで1を選択
    choice = "1"
    
    if choice == "3":
        show_results_guide()
    elif choice == "2":
        process_multiple_files()
    else:
        # 単一ファイル処理
        pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
        result = quick_ocr_process(pdf_path)
        
        if result:
            print("\n✅ 処理が完了しました！")
            show_results_guide()


if __name__ == "__main__":
    main()