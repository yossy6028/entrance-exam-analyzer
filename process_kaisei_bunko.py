#!/usr/bin/env python3
"""
開成中2025年度をbunkoOCRで処理する簡易スクリプト
"""
import subprocess
import time
from pathlib import Path
import pyautogui
import pyperclip

def process_kaisei_with_bunko():
    """開成中2025年のPDFをbunkoOCRで処理"""
    
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    print("📱 bunkoOCRでPDFを開きます...")
    
    # bunkoOCRでPDFを直接開く
    subprocess.run(['open', '-a', 'bunkoOCR', pdf_path])
    
    print("\n⏳ bunkoOCRが起動するまで5秒待機...")
    time.sleep(5)
    
    print("\n【手動操作が必要です】")
    print("1. bunkoOCRでOCRボタンをクリック")
    print("2. 処理完了後、以下の手順でテキストファイルを保存:")
    print("   - メニュー > ファイル > テキストファイルを保存")
    print("   - ファイル名: kaisei_2025_bunko.txt")
    print("3. 保存場所: このスクリプトと同じフォルダ")
    print("\n完了したらEnterキーを押してください...")
    input()
    
    # 保存されたファイルを確認
    if Path("kaisei_2025_bunko.txt").exists():
        print("✅ ファイルが保存されました: kaisei_2025_bunko.txt")
        
        # 結合スクリプトを作成
        print("\n📝 bunkoOCR結果を結合中...")
        
        # 最新のResultsフォルダから全てのtext*.txtを結合
        results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        
        if results_dir.exists():
            folders = [d for d in results_dir.iterdir() if d.is_dir()]
            if folders:
                # 最新のフォルダを取得
                latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
                print(f"最新の結果フォルダ: {latest_folder.name}")
                
                # text*.txtファイルを結合
                text_files = sorted(latest_folder.glob("text*.txt"))
                if text_files:
                    combined_text = []
                    for txt_file in text_files:
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            combined_text.append(f"=== {txt_file.name} ===\n{f.read()}")
                    
                    # 結合したテキストを保存
                    with open("kaisei_2025_bunko_combined.txt", 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(combined_text))
                    
                    print("✅ 結合ファイルを作成: kaisei_2025_bunko_combined.txt")
                    print(f"   総ページ数: {len(text_files)}")
                    
                    # 分析スクリプトを実行
                    print("\n🔍 分析を開始します...")
                    subprocess.run(['python', 'analyze_kaisei_2025_bunko.py'])
    else:
        print("❌ ファイルが見つかりません。手動で保存してください。")

if __name__ == "__main__":
    process_kaisei_with_bunko()