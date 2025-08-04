#!/usr/bin/env python3
"""
右上の検索窓をクリックして検索
"""
import pyautogui
import time
import subprocess

def click_search_box():
    """右上の検索窓をクリックして検索"""
    
    print("🔍 右上の検索窓をクリックします")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 右上の検索窓をクリック
    print("\n1️⃣ 右上の検索窓をクリック...")
    pyautogui.click(640, 85)  # スクリーンショットから推定した検索窓の座標
    time.sleep(0.5)
    
    # 既存のテキストをクリア
    print("2️⃣ 検索窓をクリア...")
    pyautogui.hotkey('cmd', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 25開成と入力
    print("3️⃣ 「25開成」を入力...")
    pyautogui.typewrite('25')
    time.sleep(0.5)
    
    # 検索実行（Enter）
    print("4️⃣ 検索実行...")
    pyautogui.press('return')
    time.sleep(1)
    
    # ファイルを選択
    print("\n5️⃣ 検索結果のファイルを選択...")
    pyautogui.click(550, 300)  # ファイルリストエリア
    time.sleep(0.5)
    
    # ファイルを開く
    print("6️⃣ ファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n✅ 完了！")

if __name__ == "__main__":
    click_search_box()