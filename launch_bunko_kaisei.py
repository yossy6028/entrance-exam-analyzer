#!/usr/bin/env python3
"""
bunkoOCRで開成中2025年を処理する修正版スクリプト
"""
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path


def launch_bunko_ocr_kaisei():
    """bunkoOCRを起動して開成中2025年のPDFを処理"""
    
    print(f"\n{'='*60}")
    print(f"bunkoOCRを使用した開成中学校2025年度分析")
    print(f"{'='*60}")
    
    # PDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # bunkoOCRを起動
    print("\n📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルから選択ボタンをクリック
    print("📂 「ファイルから選択」をクリック...")
    
    # 手動で確認した「ファイルから選択」の正確な位置
    click_x = 1071  # 実際に確認したX座標
    click_y = 712   # 実際に確認したY座標
    
    print(f"座標: ({click_x}, {click_y})")
    pyautogui.click(click_x, click_y)
    time.sleep(2)
    
    # ファイルダイアログでPDFを選択
    print("📄 PDFファイルを選択中...")
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')  # パス入力ダイアログ
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')  # パスをペースト
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')  # ファイル選択
    
    print("\n🔍 自動OCR処理が開始されました...")
    print("⏳ 処理完了まで約2-3分お待ちください...")
    
    # 処理完了を待つ（3分）
    for i in range(18):
        print(f"\r処理中... {i*10}/180秒", end='', flush=True)
        time.sleep(10)
    
    print("\n\n✅ OCR処理が完了しました！")
    
    # 結果の場所を確認
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    
    # 最新のフォルダを取得
    folders = [d for d in results_dir.iterdir() if d.is_dir()]
    if folders:
        latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
        print(f"\n📁 OCR結果フォルダ: {latest_folder.name}")
        
        # テキストファイルを結合
        text_files = sorted(latest_folder.glob("text*.txt"))
        if text_files:
            combined_text = []
            for txt_file in text_files:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_text.append(f"=== {txt_file.name} ===\n{content}")
            
            # 結合したテキストを保存
            output_file = "開成2025_bunko.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(combined_text))
            
            print(f"✅ 結合テキストを保存: {output_file}")
            print(f"   総ページ数: {len(text_files)}")
            
            # 最初のページを確認
            with open(text_files[0], 'r', encoding='utf-8') as f:
                first_page = f.read()[:200]
                print(f"\n📄 最初のページの内容:")
                print(first_page)
            
            return output_file
    
    return None


def main():
    """メイン処理"""
    
    # bunkoOCRで処理
    text_file = launch_bunko_ocr_kaisei()
    
    if text_file:
        print(f"\n🎯 次のステップ:")
        print(f"1. python analyze_kaisei_2025_bunko.py を実行")
        print(f"2. 分析結果を確認")
    else:
        print("\n❌ OCR処理に失敗しました")


if __name__ == "__main__":
    main()