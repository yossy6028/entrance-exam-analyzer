#!/usr/bin/env python3
"""
キーボードナビゲーションで選択してEnterを確実に押す
"""
import pyautogui
import time
import subprocess

def keyboard_nav_with_enter():
    """タブ、上下キーで選択し、確実にEnterを押す"""
    
    print("📱 bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1.5)
    
    print("\n⌨️ キーボードナビゲーション開始...")
    
    # Tabキーでメニューにフォーカス
    print("1️⃣ Tabキーでメニューにフォーカス")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # 上矢印5回で最上部へ
    print("2️⃣ 上矢印5回で最上部へ")
    for i in range(5):
        pyautogui.press('up')
        print(f"   ↑ {i+1}/5")
        time.sleep(0.2)
    
    # 下矢印2回で「ファイルから選択」へ
    print("3️⃣ 下矢印2回で「ファイルから選択」へ")
    pyautogui.press('down')
    print("   ↓ 1/2")
    time.sleep(0.5)
    
    pyautogui.press('down')
    print("   ↓ 2/2")
    time.sleep(0.5)
    
    print("\n✅ 「ファイルから選択」が選択されました")
    
    # Enterキーを複数の方法で押す
    print("\n4️⃣ Enterキーを押します...")
    
    # 方法1: 通常のEnter
    print("   方法1: pyautogui.press('return')")
    pyautogui.press('return')
    time.sleep(1)
    
    # 方法2: keyDownとkeyUpを使う
    print("   方法2: keyDown/keyUp")
    pyautogui.keyDown('return')
    time.sleep(0.1)
    pyautogui.keyUp('return')
    time.sleep(1)
    
    # 方法3: AppleScriptでEnterキーを送信
    print("   方法3: AppleScriptでEnter")
    applescript = '''
    tell application "System Events"
        key code 36  -- Enterキーのキーコード
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
    
    print("\n✅ Enterキーを押しました！")
    print("📂 ファイルダイアログが開いているはずです")

if __name__ == "__main__":
    keyboard_nav_with_enter()