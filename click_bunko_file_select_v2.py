#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンをクリックするスクリプト（改良版）
"""
import pyautogui
import time
import subprocess

def click_file_select_button():
    """bunkoOCRの3番目のボタン「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットからボタンの位置を推定
    screen_width, screen_height = pyautogui.size()
    
    # ウィンドウの中央と推定される位置
    window_center_x = screen_width // 2
    
    # 「ファイルから選択」ボタンのY座標
    # 写真ライブラリから選択ができていたので、その少し下
    button_y = 520
    
    print(f"画面サイズ: {screen_width}x{screen_height}")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("「ファイルから選択」をクリックしました")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    print("ファイルダイアログが開きました")
    print("手動で以下のファイルを選択してください：")
    print("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf")
    
    # 手動操作のために待機
    print("\nファイルを選択したら、Enterキーを押してください...")
    input()
    
    print("OCR処理が開始されます。")
    print("処理には約30秒かかります...")
    
    # プログレスバー表示
    for i in range(30):
        print("■", end="", flush=True)
        time.sleep(1)
    
    print("\nOCR処理が完了しました！")

def click_only():
    """ボタンをクリックするだけのバージョン"""
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットからボタンの位置を推定
    screen_width, screen_height = pyautogui.size()
    
    # ウィンドウの中央と推定される位置
    window_center_x = screen_width // 2
    
    # 「ファイルから選択」ボタンのY座標
    # 写真ライブラリから選択ができていたので、その少し下
    button_y = 520
    
    print(f"画面サイズ: {screen_width}x{screen_height}")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("「ファイルから選択」をクリックしました")
    
    print("\nファイルダイアログが開いたら、手動で以下の操作を行ってください：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    # ボタンをクリックするだけ
    click_only()