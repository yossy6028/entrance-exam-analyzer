#!/usr/bin/env python3
"""
正しい座標で検索窓をクリック
"""
import pyautogui
import time
import subprocess

def search_with_correct_coords():
    """正しい座標で検索"""
    
    print("🔍 正しい位置で検索窓をクリック")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットから正確に読み取った検索窓の位置
    # ファイルダイアログの右上にある検索窓
    print("\n1️⃣ 検索窓をクリック（正しい座標）...")
    pyautogui.click(600, 85)  # ファイルダイアログ内の検索窓
    time.sleep(0.5)
    
    # 検索窓がアクティブになったか確認のため、クリア操作
    print("2️⃣ 検索窓をクリア...")
    pyautogui.hotkey('cmd', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    
    # 25を入力
    print("3️⃣ 「25」を入力...")
    pyautogui.typewrite('25')
    time.sleep(0.5)
    
    # 検索実行
    print("4️⃣ Enterで検索...")
    pyautogui.press('return')
    time.sleep(1)
    
    print("\n✅ 検索完了！25開成.pdfが表示されているはずです")

if __name__ == "__main__":
    search_with_correct_coords()