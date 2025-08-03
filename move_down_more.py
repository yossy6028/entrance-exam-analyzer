#!/usr/bin/env python3
"""
もう少し下に移動して25開成.pdfを選択
"""
import subprocess
import time
import pyautogui

def move_down_more():
    """さらに下に移動して25開成.pdfを選択"""
    
    print("⬇️ もう少し下に移動して25開成.pdfを探します")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # 現在選択されているファイルから下へ移動
    print("\n📄 下矢印で25開成.pdfまで移動...")
    for i in range(5):  # さらに5回下へ
        pyautogui.press('down')
        time.sleep(0.3)
        print(f"   ↓ {i+1}/5")
    
    # Enterで開く
    print("\n✅ Enterキーでファイルを開く...")
    pyautogui.press('return')
    
    print("\n🎯 今度こそ25開成.pdfを開きました！")

if __name__ == "__main__":
    move_down_more()