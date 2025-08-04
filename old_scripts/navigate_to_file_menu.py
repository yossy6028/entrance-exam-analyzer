#!/usr/bin/env python3
"""
キーボードナビゲーションで「ファイルから選択」を選択
"""
import pyautogui
import time
import subprocess

def navigate_to_file_menu():
    """キーボードで確実にメニューを選択"""
    
    print("📱 bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    print("\n⌨️ キーボードナビゲーション開始...")
    
    # メニューバーからファイルメニューを開く方法を試す
    print("1. Control+F2でメニューバーにフォーカス...")
    pyautogui.hotkey('ctrl', 'f2')
    time.sleep(0.5)
    
    # またはTabキーでUI要素を巡回
    print("\n2. Tabキーでメニューを巡回...")
    for i in range(10):  # 最大10回タブを押す
        pyautogui.press('tab')
        time.sleep(0.3)
        print(f"   Tab {i+1}/10")
        
        # スペースキーで選択を試みる
        if i == 2:  # 3番目の要素で試す
            print("   → スペースキーで選択を試みます")
            pyautogui.press('space')
            time.sleep(1)
            
            # またはEnterキー
            pyautogui.press('return')
            break
    
    print("\n✅ メニュー選択を試行しました")

if __name__ == "__main__":
    navigate_to_file_menu()