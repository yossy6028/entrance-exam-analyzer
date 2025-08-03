#!/usr/bin/env python3
"""
開成フォルダ内で25を含むPDFを選択
"""
import pyautogui
import time

def select_25_kaisei_pdf():
    """25を含む開成PDFを選択"""
    
    print("📄 開成フォルダ内でPDFを選択します...")
    
    # ファイルリストにフォーカス（右側のペイン）
    print("\n1️⃣ ファイルリストをクリック...")
    pyautogui.click(600, 250)  # ファイルリスト内をクリック
    time.sleep(0.5)
    
    # 「2」を入力してファイルを探す
    print("\n2️⃣ 「2」を入力して20番台のファイルへ移動...")
    pyautogui.typewrite('2')
    time.sleep(0.5)
    
    # 続けて「5」を入力
    print("3️⃣ 「5」を入力...")
    pyautogui.typewrite('5')
    time.sleep(0.5)
    
    # 下矢印で調整（必要に応じて）
    print("\n4️⃣ 下矢印で微調整...")
    pyautogui.press('down')
    time.sleep(0.3)
    
    # ファイルを選択（Enter）
    print("\n5️⃣ Enterキーでファイルを選択...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開くボタンを押す（もう一度Enter）
    print("6️⃣ もう一度Enterで「開く」...")
    pyautogui.press('return')
    
    print("\n✅ PDFファイルを選択しました！")

if __name__ == "__main__":
    select_25_kaisei_pdf()