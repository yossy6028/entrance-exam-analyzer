#!/usr/bin/env python3
"""
ファイルダイアログで開成中PDFを選択
"""
import pyautogui
import time
import pyperclip


def select_kaisei_pdf():
    """開成中PDFファイルを選択"""
    
    print("\n📁 ファイルダイアログで開成中PDFを選択します...")
    
    # PDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校"
    
    # フォルダに移動
    print("📂 開成中学校フォルダに移動...")
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    
    print("\n🔍 「開成」「25」を含むPDFファイルを探してください")
    print("   例: 2025年開成中学校問題_国語.pdf")
    print("   例: 25開成.pdf")
    print("   例: 開成中_2025.pdf")
    print("\n📄 ファイルを選択してEnterキーを押してください")
    
    # ファイル名に「25」を含むものを自動で探す試み
    print("\n⌨️ 検索ボックスで「25」を入力...")
    pyautogui.hotkey('cmd', 'f')  # 検索を開く
    time.sleep(0.5)
    pyautogui.typewrite('25')  # 「25」を検索
    time.sleep(1)
    
    print("\n✅ 「25」を含むファイルが表示されているはずです")
    print("   開成のPDFファイルを選択してEnterキーを押してください")


if __name__ == "__main__":
    select_kaisei_pdf()