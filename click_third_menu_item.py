#!/usr/bin/env python3
"""
bunkoOCRの上から3つ目のメニュー「ファイルから選択」をクリック
"""
import pyautogui
import time
import subprocess
import pyperclip

def click_third_menu_item():
    """上から3つ目のメニュー項目をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # メニューの位置を計算
    # 1つ目: カメラ撮影
    # 2つ目: 写真ライブラリから選択  
    # 3つ目: ファイルから選択 ← これ
    
    # 左側のメニューエリアのX座標（アイコンとテキストの中間）
    menu_x = 100
    
    # 上から3つ目のメニュー項目のY座標
    # メニュー項目の間隔を考慮
    menu_item_height = 50  # 各メニュー項目の高さ
    first_item_y = 70      # 最初の項目のY座標
    
    # 3つ目の項目の位置
    third_item_y = first_item_y + (menu_item_height * 2)
    
    print(f"「ファイルから選択」をクリック")
    print(f"クリック位置: ({menu_x}, {third_item_y})")
    
    # クリック
    pyautogui.click(menu_x, third_item_y)
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    # 開成中のPDFパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    print("\nファイルダイアログでPDFを選択...")
    
    # パスをコピー
    pyperclip.copy(pdf_path)
    
    # Cmd+Shift+G でパス入力ダイアログを開く
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
    
    print("\n✅ ファイルを選択しました！")
    print("🔍 OCR処理が開始されます...")
    print("\n処理が完了したら（約2-3分後）、以下のコマンドを実行：")
    print("python check_latest_bunko_result.py")

if __name__ == "__main__":
    click_third_menu_item()