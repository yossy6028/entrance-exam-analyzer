#!/usr/bin/env python3
"""
bunkoOCRの初期画面で「ファイルから選択」をクリック
"""
import pyautogui
import time
import subprocess

def click_file_select():
    """初期画面の3番目のボタン「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # まず初期画面に戻る（必要に応じて）
    # Escキーを押して前の画面に戻る
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # bunkoOCRウィンドウの位置
    window_x = 720
    window_width = 823
    
    # ウィンドウの中央X座標
    window_center_x = window_x + (window_width // 2)
    
    # 3つのボタンの推定Y座標（初期画面）
    # 1つ目: カメラ撮影 (約200px)
    # 2つ目: 写真ライブラリから選択 (約250px)
    # 3つ目: ファイルから選択 (約235px)
    button_y = 235
    
    print(f"初期画面で「ファイルから選択」をクリック")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("クリックしました！")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    print("\nファイルダイアログが開いたら：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    click_file_select()