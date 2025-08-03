#!/usr/bin/env python3
"""
右矢印キーでファイルリストに移動
"""
import subprocess
import time
import pyautogui

def right_arrow_to_files():
    """右矢印キーでファイルリストに移動"""
    
    print("➡️ 右矢印キーでファイルリストに移動")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # 右矢印キーでフォルダからファイルリストへ
    print("\n1️⃣ 右矢印キーで右側のファイルリストへ...")
    pyautogui.press('right')
    time.sleep(0.5)
    
    # ファイルリストの最初のファイルが選択されるはず
    print("\n2️⃣ 下矢印で25開成.pdfまで移動...")
    # 15開成.pdfから始まって、25まで移動
    for i in range(10):  # 適当に10回
        pyautogui.press('down')
        time.sleep(0.2)
        print(f"   ↓ {i+1}")
    
    # Enterで開く
    print("\n3️⃣ Enterキーでファイルを開く...")
    pyautogui.press('return')
    
    print("\n✅ 完了！")

if __name__ == "__main__":
    right_arrow_to_files()