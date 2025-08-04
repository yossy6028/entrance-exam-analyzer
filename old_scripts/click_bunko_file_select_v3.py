#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンをクリックするスクリプト（位置修正版）
"""
import pyautogui
import time
import subprocess

def click_file_select_button():
    """bunkoOCRの3番目のボタン「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # bunkoOCRウィンドウの実際の位置
    # Window position: 720, 25
    # Window size: 823 x 1055
    window_x = 720
    window_y = 25
    window_width = 823
    
    # ウィンドウの中央X座標
    window_center_x = window_x + (window_width // 2)
    
    # 「ファイルから選択」ボタンのY座標
    # ウィンドウのY座標(25) + ウィンドウ内での位置
    # 1つ目: カメラ撮影
    # 2つ目: 写真ライブラリから選択 (成功していた)
    # 3つ目: ファイルから選択 (これをクリックしたい)
    button_y = window_y + 400  # ウィンドウ内で上から400px程度
    
    print(f"bunkoOCRウィンドウ位置: ({window_x}, {window_y})")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("「ファイルから選択」をクリックしました")
    
    print("\nファイルダイアログが開いたら、手動で以下の操作を行ってください：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    click_file_select_button()