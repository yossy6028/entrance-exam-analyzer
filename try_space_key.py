#!/usr/bin/env python3
"""
スペースキーでメニューを選択
"""
import pyautogui
import time
import subprocess

def try_space_key():
    """スペースキーで選択を試す"""
    
    print("📱 bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    print("\n⌨️ スペースキーを試します...")
    
    # スペースキー
    print("1️⃣ スペースキー")
    pyautogui.press('space')
    time.sleep(1)
    
    # Command + スペース（macOSの一般的なショートカット）
    print("2️⃣ Command + スペース")
    pyautogui.hotkey('cmd', 'space')
    time.sleep(1)
    
    # Option + スペース
    print("3️⃣ Option + スペース")
    pyautogui.hotkey('option', 'space')
    time.sleep(1)
    
    # もう一度Enter
    print("4️⃣ もう一度Enter")
    pyautogui.press('enter')
    
    print("\n✅ 各種キーを試しました")

if __name__ == "__main__":
    try_space_key()