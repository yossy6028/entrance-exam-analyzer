#!/usr/bin/env python3
"""
過去問フォルダに移動して開成PDFを選択
"""
import pyautogui
import time
import pyperclip

def navigate_to_kakomon_folder():
    """過去問フォルダに移動して開成PDFを選択"""
    
    print("📂 過去問フォルダに移動します...")
    
    # パスをコピー
    folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
    pyperclip.copy(folder_path)
    
    # Cmd+Shift+G でパス入力ダイアログ
    print("📍 パス入力ダイアログを開く...")
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    print("📋 パスをペースト...")
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enterでフォルダに移動
    print("⏎ フォルダに移動...")
    pyautogui.press('return')
    time.sleep(2)
    
    # 開成中学校フォルダを探す
    print("\n🔍 開成中学校フォルダを探します...")
    
    # 「開成」で検索
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('開成')
    time.sleep(1)
    
    # 検索結果を選択（開成中学校フォルダ）
    print("📁 開成中学校フォルダを選択...")
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('return')  # フォルダを開く
    time.sleep(2)
    
    # フォルダ内で「25」を検索
    print("\n🔍 フォルダ内で「25」を含むPDFを検索...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('25')
    time.sleep(1)
    
    # 最初のPDFを選択
    print("📄 PDFファイルを選択...")
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開くボタンを押す
    print("✅ 「開く」ボタンを押す...")
    pyautogui.press('return')
    
    print("\n🎉 開成のPDFファイルを選択しました！")

if __name__ == "__main__":
    navigate_to_kakomon_folder()