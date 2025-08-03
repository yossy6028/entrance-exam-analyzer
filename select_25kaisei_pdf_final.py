#!/usr/bin/env python3
"""
25開成.pdfを確実に選択
"""
import subprocess
import time
import pyautogui

def select_25kaisei_pdf_final():
    """25開成.pdfを確実に選択"""
    
    print("📄 25開成.pdfを選択します...")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルリストをクリックしてフォーカス
    print("\n1️⃣ ファイルリストにフォーカス...")
    pyautogui.click(600, 300)
    time.sleep(0.5)
    
    # ファイルの並び順から推測して移動
    # 15, 16, 17, 18, 19, 20, 21... の後に25がある
    
    # 「2」を入力して20番台へジャンプ
    print("\n2️⃣ 「2」を入力して20番台へ...")
    pyautogui.typewrite('2')
    time.sleep(0.5)
    
    # 下矢印で25まで移動
    print("3️⃣ 下矢印で25開成.pdfまで移動...")
    # 20, 21の後なので、数回下へ
    for i in range(6):
        pyautogui.press('down')
        time.sleep(0.3)
        print(f"   ↓ {i+1}/6")
    
    # ファイルを選択
    print("\n4️⃣ Enterでファイルを選択...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開くボタン
    print("5️⃣ もう一度Enterで「開く」...")
    pyautogui.press('return')
    
    print("\n✅ 25開成.pdfを選択しました！")

if __name__ == "__main__":
    select_25kaisei_pdf_final()