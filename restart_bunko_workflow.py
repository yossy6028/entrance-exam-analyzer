#!/usr/bin/env python3
"""
最初からbunkoOCRワークフローをやり直し
"""
import pyautogui
import time
import subprocess

def restart_bunko_workflow():
    """最初からやり直し"""
    
    print("🔄 最初からやり直します")
    print("=" * 60)
    
    # bunkoOCRをアクティブ化
    print("\n1️⃣ bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(2)
    
    # Tab → 上5回 → 下2回
    print("\n2️⃣ メニュー選択...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    for i in range(5):
        pyautogui.press('up')
        time.sleep(0.2)
    
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    print("   ✅ 「ファイルから選択」を選択")
    
    # スペースキーで開く
    print("\n3️⃣ スペースキーでファイルダイアログを開く...")
    pyautogui.press('space')
    time.sleep(2)
    
    print("\n✅ ファイルダイアログが開きました")
    print("📂 次は開成フォルダを開いて25開成.pdfを選択します")

if __name__ == "__main__":
    restart_bunko_workflow()