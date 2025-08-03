#!/usr/bin/env python3
"""
Tabキーで右側のファイルリストに移動してPDFを選択
"""
import subprocess
import time
import pyautogui

def tab_to_file_list():
    """Tabキーで右側のファイルリストに移動"""
    
    print("⌨️ キーボードで右側のファイルリストに移動")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # Tabキーでフォーカスを移動
    print("\n1️⃣ Tabキーで右側のファイルリストへ...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # もう一度Tabが必要かも
    print("2️⃣ もう一度Tab...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # ファイルリストの最初のファイルが選択される
    print("\n3️⃣ 下矢印で25開成.pdfまで移動...")
    # 15, 16, 17, 18, 19, 20, 21... と下に移動
    for i in range(10):  # 25まで移動
        pyautogui.press('down')
        time.sleep(0.2)
        print(f"   ↓ {i+1}/10")
    
    # ファイルを開く（Enter）
    print("\n4️⃣ Enterキーでファイルを開く...")
    pyautogui.press('return')
    
    print("\n✅ 完了！")

if __name__ == "__main__":
    tab_to_file_list()