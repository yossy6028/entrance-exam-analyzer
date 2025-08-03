#!/usr/bin/env python3
"""
「開く」ボタンをクリック
"""
import subprocess
import time
import pyautogui

def click_open_button():
    """開くボタンをクリック"""
    
    print("✅ 25開成.pdfが選択されています！")
    print("🎯 「開く」ボタンをクリックします...")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # 方法1: Enterキーを押す
    print("\n1️⃣ Enterキーで開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 方法2: 開くボタンをクリック（右下）
    print("2️⃣ 「開く」ボタンをクリック...")
    pyautogui.click(680, 460)  # 開くボタンの座標
    
    print("\n🎉 ファイルを開きました！")
    print("🔍 OCR処理が開始されます...")

if __name__ == "__main__":
    click_open_button()