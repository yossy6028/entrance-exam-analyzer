#!/usr/bin/env python3
"""
Enterキーを押してファイルダイアログを開く
"""
import pyautogui
import time
import pyperclip


def press_enter_and_select_file():
    """Enterキーを押してダイアログを開き、ファイルを選択"""
    
    print("\n📂 Enterキーを押してファイルダイアログを開きます...")
    pyautogui.press('return')
    time.sleep(2)
    
    print("✅ ファイルダイアログが開きました")
    
    # PDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # ファイル選択
    print("\n📄 開成中PDFファイルを選択中...")
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')  # パス入力ダイアログ
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')  # パスをペースト
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')  # ファイル選択
    
    print("\n✅ ファイルを選択しました！")
    print("🔍 OCR処理が自動的に開始されます...")
    print("\n⏳ 処理完了まで2-3分お待ちください")


if __name__ == "__main__":
    press_enter_and_select_file()