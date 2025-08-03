#!/usr/bin/env python3
"""
bunkoOCRのファイルダイアログにフォーカス
"""
import subprocess
import time
import pyautogui

def focus_bunko_dialog():
    """bunkoOCRのファイルダイアログにフォーカス"""
    
    print("🎯 bunkoOCRのファイルダイアログにフォーカス...")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルダイアログの中央付近をクリック
    print("📂 ファイルダイアログをクリック...")
    pyautogui.click(640, 400)  # 画面中央
    time.sleep(0.5)
    
    print("✅ フォーカスしました！")

if __name__ == "__main__":
    focus_bunko_dialog()