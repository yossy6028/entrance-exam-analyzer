#!/usr/bin/env python3
"""
検索窓に25を入力（手動でクリック後）
"""
import pyautogui
import time

def type_25_in_search():
    """検索窓に25を入力"""
    
    print("📝 検索窓に「25」を入力します")
    print("（検索窓を手動でクリックしてください）")
    
    # 少し待つ
    time.sleep(2)
    
    # クリア
    print("\n1️⃣ 検索窓をクリア...")
    pyautogui.hotkey('cmd', 'a')
    pyautogui.press('delete')
    
    # 25を入力
    print("2️⃣ 「25」を入力...")
    pyautogui.typewrite('25')
    time.sleep(0.5)
    
    # 検索実行
    print("3️⃣ Enterで検索...")
    pyautogui.press('return')
    
    print("\n✅ 検索完了！")

if __name__ == "__main__":
    type_25_in_search()