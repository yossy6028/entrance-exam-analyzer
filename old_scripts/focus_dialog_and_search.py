#!/usr/bin/env python3
"""
ファイルダイアログにフォーカスして検索
"""
import pyautogui
import time
import subprocess

def focus_dialog_and_search():
    """ファイルダイアログにフォーカスして検索"""
    
    print("🎯 ファイルダイアログにフォーカスを戻します...")
    
    # bunkoOCRをアクティブに（ファイルダイアログもbunkoOCRの一部）
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルダイアログ内をクリックしてフォーカス
    print("📂 ファイルダイアログ内をクリック...")
    # ダイアログの中央付近をクリック
    pyautogui.click(640, 400)  # 画面中央付近
    time.sleep(0.5)
    
    # 検索をキャンセル（もし開いていれば）
    print("❌ 既存の検索をキャンセル...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 新しく検索を開始
    print("\n🔍 検索を開始...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    
    # 「25」を入力
    print("📝 「25」を入力...")
    pyautogui.typewrite('25')
    time.sleep(1)
    
    print("\n✅ 「25」を含むファイルが検索されました")
    print("📄 開成のPDFファイルを選択してEnterキーを押してください")

if __name__ == "__main__":
    focus_dialog_and_search()