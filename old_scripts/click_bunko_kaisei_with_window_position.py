#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンをクリック（22時の成功方法を使用）
"""
import pyautogui
import time
import subprocess
import pyperclip

def click_file_select_with_window_position():
    """bunkoOCRの3番目のボタン「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # bunkoOCRウィンドウの位置（22時の成功時の設定）
    # Window position: 720, 25
    # Window size: 823 x 1055
    window_x = 720
    window_y = 25
    window_width = 823
    
    # ウィンドウの中央X座標
    window_center_x = window_x + (window_width // 2)
    
    # 「ファイルから選択」ボタンのY座標
    # 3つ目のボタンなので、より下の位置
    button_y = window_y + 400  # ウィンドウ内で上から400px程度
    
    print(f"bunkoOCRウィンドウ位置: ({window_x}, {window_y})")
    print(f"クリック位置: ({window_center_x}, {button_y})")
    
    # クリック
    pyautogui.click(window_center_x, button_y)
    print("「ファイルから選択」をクリックしました")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    # 開成中のPDFパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    print("ファイルパスを入力します...")
    
    # Cmd+Shift+G でパス入力ダイアログを開く
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enterキーを押してパスに移動
    pyautogui.press('return')
    time.sleep(1)
    
    # もう一度Enterキーを押してファイルを開く
    pyautogui.press('return')
    
    print("ファイルを開きました。OCR処理が開始されます。")
    print("処理には約2-3分かかります...")
    
    print("\n処理が完了したら、以下のコマンドを実行してください：")
    print("python check_latest_bunko_result.py")

if __name__ == "__main__":
    click_file_select_with_window_position()