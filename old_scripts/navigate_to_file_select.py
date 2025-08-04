#!/usr/bin/env python3
"""
キーボードナビゲーションでファイルから選択を選ぶ
"""
import pyautogui
import time
import subprocess

def navigate_to_file_select():
    """キーボードで3番目の項目まで移動"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    print("キーボードナビゲーションで「ファイルから選択」に移動します")
    
    # Tabキーで最初の項目にフォーカス
    pyautogui.press('tab')
    time.sleep(0.5)
    print("1番目の項目（カメラ撮影）にフォーカス")
    
    # 下矢印キーで2番目の項目へ
    pyautogui.press('down')
    time.sleep(0.5)
    print("2番目の項目（写真ライブラリから選択）に移動")
    
    # 下矢印キーで3番目の項目へ
    pyautogui.press('down')
    time.sleep(0.5)
    print("3番目の項目（ファイルから選択）に移動")
    
    # Enterキーで選択
    pyautogui.press('return')
    print("Enterキーで選択しました")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    print("\nファイルダイアログが開いたら：")
    print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
    print("2. 15渋渋.pdf を選択")
    print("3. 「開く」ボタンをクリック")

if __name__ == "__main__":
    navigate_to_file_select()