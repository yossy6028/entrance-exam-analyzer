#!/usr/bin/env python3
"""
正確にファイルを選択する改良版
"""
import subprocess
import time
import pyautogui

def accurate_file_selection():
    """現在の位置から25開成.pdfを正確に選択"""
    
    print("🎯 現在選択されているファイルから25開成.pdfへ移動")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 一旦リストの最初に戻る
    print("\n1️⃣ Homeキーでリストの最初へ...")
    pyautogui.press('home')
    time.sleep(1)
    
    # ファイル名を入力して直接ジャンプ
    print("\n2️⃣ 「25」を入力して25開成.pdfへジャンプ...")
    pyautogui.typewrite('25')
    time.sleep(1)
    
    # 念のため下矢印で微調整
    print("\n3️⃣ 念のため下矢印で確認...")
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('up')  # 戻る
    time.sleep(0.5)
    
    # ファイルを開く
    print("\n4️⃣ Enterキーでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n✅ ファイルを選択しました！")

if __name__ == "__main__":
    accurate_file_selection()