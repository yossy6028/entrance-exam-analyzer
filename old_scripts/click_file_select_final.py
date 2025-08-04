#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンを正確にクリック
"""
import pyautogui
import time
import subprocess

def click_file_select_button():
    """画像から特定した正確な位置でクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 画像から確認した「ファイルから選択」の位置
    # bunkoOCRウィンドウの位置を考慮
    window_x = 720  # ウィンドウのX座標
    
    # 「ファイルから選択」ボタンの座標（画像から確認）
    # テキストの左側から少し右、中央付近
    click_x = window_x + 400  # ウィンドウ中央付近
    click_y = 335  # 画像で確認した正確なY座標
    
    print(f"「ファイルから選択」をクリック: ({click_x}, {click_y})")
    
    # クリック
    pyautogui.click(click_x, click_y)
    print("クリックしました！")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    print("\nファイルダイアログが開きました。")
    print("手動で以下の操作をお願いします：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    click_file_select_button()