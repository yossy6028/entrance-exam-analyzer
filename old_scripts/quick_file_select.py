#!/usr/bin/env python3
"""
素早くファイルから選択を選ぶ
"""
import pyautogui
import time
import subprocess

def quick_file_select():
    """素早くナビゲートして選択"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    print("素早く「ファイルから選択」を選択します")
    
    # Tabキーで最初の項目にフォーカス
    pyautogui.press('tab')
    time.sleep(0.2)  # 短い待機
    
    # 下矢印キーを2回押して3番目の項目へ
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    
    # すぐにEnterキーで選択
    pyautogui.press('return')
    print("選択しました！")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    print("\nファイルダイアログが開いたら：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    quick_file_select()