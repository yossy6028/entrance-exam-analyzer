#!/usr/bin/env python3
"""
単純にEnterキーを押すだけ
"""
import pyautogui
import time


def just_press_enter():
    """Enterキーを押すだけ"""
    
    print("\n⌨️ Enterキーを押します...")
    
    # bunkoOCRをアクティブにする
    import subprocess
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # Enterキーを押す
    pyautogui.press('enter')
    print("✅ Enterキーを押しました")
    
    time.sleep(1)
    
    # もう一度念のため
    print("⌨️ もう一度Enterキーを押します...")
    pyautogui.press('return')
    print("✅ returnキーを押しました")


if __name__ == "__main__":
    just_press_enter()