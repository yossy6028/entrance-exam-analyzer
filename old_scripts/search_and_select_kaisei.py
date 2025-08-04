#!/usr/bin/env python3
"""
ファイルダイアログで開成のPDFを検索して選択
"""
import pyautogui
import time
import pyperclip

def search_and_select_kaisei():
    """開成のPDFファイルを検索して選択"""
    
    print("🔍 開成のPDFファイルを探します...")
    
    # まず開成中学校フォルダに移動
    folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校"
    
    print("\n📂 開成中学校フォルダに移動...")
    pyperclip.copy(folder_path)
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(2)
    
    # 検索ボックスで「25」を検索
    print("\n🔍 検索ボックスで「25」を検索...")
    pyautogui.hotkey('cmd', 'f')  # 検索を開く
    time.sleep(0.5)
    pyautogui.typewrite('25')  # 「25」を入力
    time.sleep(1)
    
    print("\n📄 「25」を含むファイルが表示されているはずです")
    print("   - 2025年開成中学校問題_国語.pdf")
    print("   - 25開成.pdf")
    print("   - 開成中_2025.pdf")
    print("   などの名前のファイルを探してください")
    
    # 最初の検索結果を選択（Enterキー）
    print("\n⏎ 最初の検索結果を選択...")
    pyautogui.press('return')
    time.sleep(1)
    
    # ファイルを開く
    print("⏎ ファイルを開く...")
    pyautogui.press('return')
    
    print("\n✅ 開成のPDFファイルを選択しました！")

if __name__ == "__main__":
    search_and_select_kaisei()