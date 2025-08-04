#!/usr/bin/env python3
"""
開成のPDFを自動で確実に選択
"""
import pyautogui
import time
import pyperclip

def auto_select_kaisei_pdf():
    """開成中学校フォルダの2025年開成中学校問題_国語.pdfを選択"""
    
    print("🎯 開成のPDFを自動選択します！")
    
    # まず現在の検索をクリア
    print("🧹 検索をクリア...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 正確なパスで直接移動
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    print("📍 PDFファイルの場所に直接移動...")
    pyperclip.copy(pdf_path)
    
    # Cmd+Shift+G でパス入力
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enterで直接ファイルを開く
    print("⏎ ファイルを開く...")
    pyautogui.press('return')
    time.sleep(1)
    
    # 念のためもう一度Enter
    pyautogui.press('return')
    
    print("\n✅ 開成中学校2025年問題_国語.pdfを選択しました！")
    print("🔍 OCR処理が開始されます...")

if __name__ == "__main__":
    auto_select_kaisei_pdf()