#!/usr/bin/env python3
"""
スクロールして25開成.pdfを探す
"""
import pyautogui
import time

def scroll_and_find_25():
    """下にスクロールして25開成.pdfを探す"""
    
    print("📜 下にスクロールして25開成.pdfを探します...")
    
    # ファイルリストにフォーカス
    print("\n1️⃣ ファイルリストにフォーカス...")
    pyautogui.click(600, 300)  # ファイルリスト内
    time.sleep(0.5)
    
    # Page Downで下にスクロール
    print("\n2️⃣ Page Downで下へスクロール...")
    for i in range(3):
        pyautogui.press('pagedown')
        time.sleep(0.5)
        print(f"   スクロール {i+1}/3")
    
    # または下矢印連打
    print("\n3️⃣ 下矢印で探す...")
    for i in range(10):
        pyautogui.press('down')
        time.sleep(0.2)
    
    # 25が見つかったらEnter
    print("\n4️⃣ ファイルを選択...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開く
    print("5️⃣ 「開く」ボタン...")
    pyautogui.press('return')
    
    print("\n✅ 処理完了！")

if __name__ == "__main__":
    scroll_and_find_25()