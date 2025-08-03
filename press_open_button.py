#!/usr/bin/env python3
"""
選択したファイルを開く
"""
import subprocess
import time
import pyautogui

def press_open_button():
    """選択したファイルを開く"""
    
    print("📂 選択したファイルを開きます")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # Enterキーで「開く」
    print("\n1️⃣ Enterキーで「開く」...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # もう一度念のため
    print("2️⃣ もう一度Enter（念のため）...")
    pyautogui.press('return')
    
    print("\n✅ ファイルを開きました！")
    print("🔍 OCR処理が開始されます...")

if __name__ == "__main__":
    press_open_button()