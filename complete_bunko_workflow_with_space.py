#!/usr/bin/env python3
"""
完全版：bunkoOCRワークフロー（スペースキーで開く）
"""
import pyautogui
import time
import subprocess
import pyperclip

def complete_bunko_workflow():
    """完全なbunkoOCRワークフロー"""
    
    print("🚀 bunkoOCR完全ワークフロー開始！")
    print("=" * 60)
    
    # 1. bunkoOCRをアクティブ化
    print("\n1️⃣ bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(2)
    
    # 2. キーボードナビゲーション
    print("\n2️⃣ キーボードナビゲーション...")
    print("   Tab → 上5回 → 下2回")
    
    # Tab
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # 上5回
    for i in range(5):
        pyautogui.press('up')
        time.sleep(0.2)
    
    # 下2回
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    print("   ✅ 「ファイルから選択」を選択")
    
    # 3. スペースキーで開く！！！
    print("\n3️⃣ 🔥 スペースキーで開く！！！")
    pyautogui.press('space')
    time.sleep(2)
    
    print("   ✅ ファイルダイアログが開きました！")
    
    # 4. 過去問フォルダに移動
    print("\n4️⃣ 過去問フォルダに移動...")
    folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
    pyperclip.copy(folder_path)
    
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(2)
    
    # 5. 開成フォルダを探す
    print("\n5️⃣ 開成フォルダを検索...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('開成')
    time.sleep(1)
    
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('return')  # フォルダを開く
    time.sleep(2)
    
    # 6. 25を含むPDFを探す
    print("\n6️⃣ 「25」を含むPDFを検索...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('25')
    time.sleep(1)
    
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('return')  # ファイル選択
    time.sleep(0.5)
    pyautogui.press('return')  # 開く
    
    print("\n✅ 完了！OCR処理が開始されます")
    print("⏳ 処理には2-3分かかります")

if __name__ == "__main__":
    complete_bunko_workflow()