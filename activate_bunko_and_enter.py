#!/usr/bin/env python3
"""
bunkoOCRを完全にアクティブにしてEnter
"""
import subprocess
import time

def activate_bunko_and_enter():
    """bunkoOCRウィンドウを完全にアクティブにしてEnter"""
    
    print("🎯 bunkoOCRを完全にアクティブ化します...")
    
    # bunkoOCRを最前面に
    applescript = '''
    tell application "bunkoOCR"
        activate
        set frontmost to true
    end tell
    delay 1
    
    tell application "System Events"
        tell process "bunkoOCR"
            set frontmost to true
            -- ウィンドウ1をクリックしてフォーカス
            click window 1
            delay 0.5
            -- Enterキーを送信
            key code 36
        end tell
    end tell
    '''
    
    subprocess.run(["osascript", "-e", applescript])
    
    print("✅ bunkoOCRをアクティブにしてEnterキーを押しました！")

if __name__ == "__main__":
    activate_bunko_and_enter()