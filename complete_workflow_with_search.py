#!/usr/bin/env python3
"""
完全版：検索機能を使った確実なワークフロー
"""
import pyautogui
import time
import subprocess
import pyperclip
import sys

def complete_workflow_with_search(year="25"):
    """検索機能を使った確実なワークフロー"""
    
    print(f"🚀 bunkoOCRで{year}開成.pdfを確実に選択します")
    print("=" * 60)
    
    # 1. bunkoOCRをアクティブ化
    print("\n1️⃣ bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(2)
    
    # 2. キーボードナビゲーション
    print("\n2️⃣ 「ファイルから選択」を選択...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    for i in range(8):
        pyautogui.press('up')
        time.sleep(0.2)
    
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    # 3. スペースキーで開く
    print("\n3️⃣ スペースキーでファイルダイアログを開く...")
    pyautogui.press('space')
    time.sleep(2)
    
    # 4. 開成フォルダに直接移動
    print("\n4️⃣ 開成フォルダに直接移動...")
    folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成"
    pyperclip.copy(folder_path)
    
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(2)
    
    # 5. 検索でファイルを見つける
    print(f"\n5️⃣ 検索で{year}開成.pdfを見つける...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    
    # 検索ボックスをクリア
    pyautogui.hotkey('cmd', 'a')
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # ファイル名を入力
    pyautogui.typewrite(f"{year}開成.pdf")
    time.sleep(1)
    
    # 検索を閉じて結果を選択
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 6. ファイルを開く
    print(f"\n6️⃣ {year}開成.pdfを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print(f"\n✅ {year}開成.pdfを選択しました！")
    print("🔍 OCR処理が開始されます")
    print("⏳ 処理には2-3分かかります")

def main():
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = "25"
    
    complete_workflow_with_search(year)

if __name__ == "__main__":
    main()