#!/usr/bin/env python3
"""
bunkoOCRに完全にフォーカスしてからファイル選択
"""
import subprocess
import time
import pyautogui

def focus_bunko_and_select():
    """bunkoOCRに完全にフォーカスしてファイル選択"""
    
    print("🎯 bunkoOCRのファイルダイアログに完全にフォーカス")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルダイアログ内をクリックしてフォーカス
    print("\n1️⃣ ファイルダイアログ内をクリック...")
    pyautogui.click(550, 300)  # ファイルリストエリア
    time.sleep(0.5)
    
    # もう一度クリックして確実にフォーカス
    pyautogui.click(550, 350)
    time.sleep(0.5)
    
    # ファイルリストの最初に戻る
    print("\n2️⃣ Homeキーでリストの最初へ...")
    pyautogui.press('home')
    time.sleep(0.5)
    
    # 25開成.pdfまで下矢印で移動
    print("\n3️⃣ 下矢印で25開成.pdfまで移動...")
    # 15→16→17→18→19→20→21→22→23→24→25 (10回)
    for i in range(10):
        pyautogui.press('down')
        time.sleep(0.3)
        print(f"   ↓ {i+1}/10 → {15+i+1}開成.pdf")
    
    # ファイルを開く
    print("\n4️⃣ Enterでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n✅ 25開成.pdfを選択しました！")

if __name__ == "__main__":
    focus_bunko_and_select()