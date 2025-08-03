#!/usr/bin/env python3
"""
本気で開成PDFを選択する
"""
import pyautogui
import time
import subprocess

def serious_file_selection():
    """本気で確実にファイルを選択"""
    
    print("💪 本気で開成PDFを選択します！")
    
    # bunkoOCRのファイルダイアログをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイル名で直接選択を試みる
    print("\n📝 ファイル名を直接入力...")
    
    # 現在の検索をクリア
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # ファイル名の最初の文字を入力（リストビューで素早く移動）
    print("「2」を入力してファイルリストを移動...")
    pyautogui.typewrite('2')
    time.sleep(0.5)
    
    # 続けて「025」を入力
    pyautogui.typewrite('025')
    time.sleep(0.5)
    
    # さらに「年開成」を入力
    pyautogui.typewrite('年開成')
    time.sleep(0.5)
    
    # ファイルが選択されているはずなのでEnter
    print("\n⏎ Enterキーでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開くボタンを押す（もう一度Enter）
    pyautogui.press('return')
    
    print("\n🎯 ファイルを選択しました！")

if __name__ == "__main__":
    serious_file_selection()