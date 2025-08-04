#!/usr/bin/env python3
"""
スペースキーで「ファイルから選択」を実行
"""
import pyautogui
import time
import subprocess

def press_space_key():
    """スペースキーを押す"""
    
    print("🔲 スペースキーを押します！")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スペースキー
    print("1️⃣ スペースキーを押す...")
    pyautogui.press('space')
    time.sleep(1)
    
    # 念のためもう一度
    print("2️⃣ もう一度スペースキー...")
    pyautogui.press('space')
    
    print("\n✅ スペースキーを押しました！")
    print("📂 ファイルダイアログが開いているはずです")

if __name__ == "__main__":
    press_space_key()