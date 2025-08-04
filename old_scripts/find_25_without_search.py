#!/usr/bin/env python3
"""
検索を使わずに25開成.pdfを見つける
"""
import pyautogui
import time
import subprocess

def find_25_without_search():
    """検索を使わずにキーボードで25開成.pdfを見つける"""
    
    print("⌨️ キーボードで25開成.pdfを見つけます")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルリストにフォーカス
    print("\n1️⃣ ファイルリストをクリック...")
    pyautogui.click(550, 300)  # ファイルリストの中央
    time.sleep(0.5)
    
    # 「2」を押してファイル名で移動
    print("2️⃣ 「2」キーで20番台へジャンプ...")
    pyautogui.typewrite('2')
    time.sleep(0.5)
    
    # 「5」を押して25へ
    print("3️⃣ 「5」キーで25へ...")
    pyautogui.typewrite('5')
    time.sleep(0.5)
    
    # 念のため上下で調整
    print("4️⃣ 微調整...")
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('up')
    time.sleep(0.3)
    
    # ファイルを開く
    print("\n5️⃣ Enterでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n✅ 25開成.pdfを選択しました！")

if __name__ == "__main__":
    find_25_without_search()