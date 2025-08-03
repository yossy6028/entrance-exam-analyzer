#!/usr/bin/env python3
"""
bunkoOCRにフォーカスしてから25開成.pdfを選択
"""
import subprocess
import time
import pyautogui

def focus_and_select_25():
    """bunkoOCRにフォーカスしてファイル選択"""
    
    print("🎯 bunkoOCRのファイルダイアログにフォーカス...")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルダイアログ内をクリック
    print("📂 ファイルダイアログ内をクリック...")
    pyautogui.click(500, 300)  # ファイルリスト部分
    time.sleep(0.5)
    
    # 検索で25を探す
    print("\n🔍 検索で「25」を探す...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('25')
    time.sleep(1)
    
    # 検索結果を選択
    print("📄 検索結果を選択...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # ファイルを開く
    print("✅ ファイルを開く...")
    pyautogui.press('return')

if __name__ == "__main__":
    focus_and_select_25()