#!/usr/bin/env python3
"""
AppleScriptを使って「ファイルから選択」をクリック
"""
import subprocess
import time

def click_with_applescript():
    """AppleScriptでbunkoOCRのメニューをクリック"""
    
    print("📱 bunkoOCRで「ファイルから選択」をクリックします...")
    
    # AppleScriptでクリック
    applescript = '''
    tell application "System Events"
        tell process "bunkoOCR"
            -- ウィンドウをアクティブにする
            set frontmost to true
            delay 1
            
            -- ウィンドウの要素を取得
            tell window 1
                -- 「ファイルから選択」ボタンをクリック
                -- 上から3番目のボタン
                click button 3
            end tell
        end tell
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print("✅ 「ファイルから選択」をクリックしました")
    except subprocess.CalledProcessError:
        print("❌ AppleScriptでのクリックに失敗しました")
        print("代替方法：座標クリックを試します")
        
        # 代替方法：座標でクリック
        import pyautogui
        subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
        time.sleep(1)
        
        # ファイルから選択の位置をクリック
        pyautogui.click(100, 140)
    
    time.sleep(2)
    print("\n📂 ファイルダイアログが開いているはずです")
    print("開成中のPDFファイルを選択してください")

if __name__ == "__main__":
    click_with_applescript()