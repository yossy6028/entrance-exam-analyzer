#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンをクリックするスクリプト
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
    # bunkoOCRウィンドウの中央付近、上から3つ目のボタン位置
    screen_width, screen_height = pyautogui.size()
    
    # ウィンドウの中央と推定される位置
    window_center_x = screen_width // 2
    
    # 上から3つ目のボタンの推定Y座標
    # 1つ目: カメラ撮影 (約200px)
    # 2つ目: 写真ライブラリから選択 (約300px) ← これがクリックされた
    # 3つ目: ファイルから選択 (約350px) ← これをクリックしたい
    button_y = 480
    
    print(f"画面サイズ: {screen_width}x{screen_height}")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("「ファイルから選択」をクリックしました")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    # ファイルパスを入力
    print("ファイルパスを入力します...")
    
    # Cmd+Shift+G でパス入力ダイアログを開く
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # ファイルパスを入力
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    pyautogui.typewrite(pdf_path)
    time.sleep(0.5)
    
    # Enterキーを押してパスに移動
    pyautogui.press('return')
    time.sleep(1)
    
    # もう一度Enterキーを押してファイルを開く
    pyautogui.press('return')
    
    print("ファイルを開きました。OCR処理が開始されます。")
    print("処理には約30秒かかります...")
    
    # プログレスバー表示
    for i in range(30):
        print("■", end="", flush=True)
        time.sleep(1)
    
    print("\nOCR処理が完了しました！")

if __name__ == "__main__":
    click_file_select_button()