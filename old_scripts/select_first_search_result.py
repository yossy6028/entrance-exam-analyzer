#!/usr/bin/env python3
"""
検索結果から開成のPDFを選択
"""
import pyautogui
import time

def select_first_search_result():
    """検索結果の最初のファイルを選択"""
    
    print("📄 検索結果から開成のPDFを選択します...")
    
    # 検索結果の最初の項目にフォーカス
    print("1️⃣ 下矢印キーで最初の検索結果を選択...")
    pyautogui.press('down')
    time.sleep(0.5)
    
    # ファイルを選択（Enterキー）
    print("2️⃣ Enterキーでファイルを選択...")
    pyautogui.press('return')
    time.sleep(1)
    
    # ダイアログの「開く」ボタンを押す（もう一度Enter）
    print("3️⃣ もう一度Enterキーで「開く」...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 念のためもう一度
    print("4️⃣ 念のためもう一度Enter...")
    pyautogui.press('return')
    
    print("\n✅ 開成のPDFファイルを選択しました！")
    print("🔍 OCR処理が開始されます...")

if __name__ == "__main__":
    select_first_search_result()