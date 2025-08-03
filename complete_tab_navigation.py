#!/usr/bin/env python3
"""
完全なタブナビゲーション：タブ → 上5回 → 下2回 → Enter
"""
import pyautogui
import time
import subprocess


def complete_tab_navigation():
    """タブナビゲーションを完全に実行"""
    
    print("\n📱 bunkoOCRをアクティブにします...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    print("\n⌨️ タブキーでメニューにフォーカス...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    print("⬆️ 上矢印キーを5回押して最上部へ...")
    for i in range(5):
        pyautogui.press('up')
        print(f"  上 {i+1}/5")
        time.sleep(0.2)
    
    print("\n⬇️ 下矢印キーを2回押して「ファイルから選択」へ...")
    pyautogui.press('down')
    print("  下 1/2")
    time.sleep(0.5)
    
    pyautogui.press('down')
    print("  下 2/2")
    time.sleep(0.5)
    
    print("\n✅ 「ファイルから選択」が選択されました")
    print("⏎ Enterキーで決定...")
    pyautogui.press('return')
    
    print("\n✅ ファイルダイアログが開きました！")


if __name__ == "__main__":
    complete_tab_navigation()