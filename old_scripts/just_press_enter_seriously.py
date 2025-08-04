#!/usr/bin/env python3
"""
Enterキーだけを確実に押す
"""
import pyautogui
import time
import subprocess

def just_press_enter_seriously():
    """Enterキーを複数の方法で確実に押す"""
    
    print("⏎ Enterキーを確実に押します！")
    
    # bunkoOCRが最前面にあることを確認
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # 方法1: 通常のreturn
    print("1️⃣ return キー")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 方法2: enter キー
    print("2️⃣ enter キー")
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 方法3: キーコード36（Enter）を直接送信
    print("3️⃣ AppleScriptでキーコード36")
    applescript = '''
    tell application "System Events"
        tell process "bunkoOCR"
            key code 36
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
    time.sleep(0.5)
    
    # 方法4: keystroke return
    print("4️⃣ AppleScriptでkeystroke return")
    applescript2 = '''
    tell application "System Events"
        keystroke return
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript2])
    
    print("\n✅ Enterキーを押しました！")

if __name__ == "__main__":
    just_press_enter_seriously()