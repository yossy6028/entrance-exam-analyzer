#!/usr/bin/env python3
"""
ファイルダイアログで開成中PDFを自動選択
"""
import pyautogui
import time
import pyperclip

def select_kaisei_pdf_in_dialog():
    """ファイルダイアログで開成中PDFを選択"""
    
    print("\n📁 ファイルダイアログで開成中PDFを選択します...")
    
    # 開成中のPDFパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # パスをコピー
    pyperclip.copy(pdf_path)
    
    # Cmd+Shift+G でパス入力ダイアログを開く
    print("📂 パス入力ダイアログを開きます...")
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    print("📋 パスをペースト...")
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enterキーでパスに移動
    print("⏎ パスに移動...")
    pyautogui.press('return')
    time.sleep(1)
    
    # もう一度Enterキーでファイルを開く
    print("⏎ ファイルを開く...")
    pyautogui.press('return')
    
    print("\n✅ 開成中2025年のPDFを選択しました！")
    print("🔍 OCR処理が自動的に開始されます")
    print("\n⏳ 処理には2-3分かかります")
    print("完了したら: python check_latest_bunko_result.py")

if __name__ == "__main__":
    select_kaisei_pdf_in_dialog()