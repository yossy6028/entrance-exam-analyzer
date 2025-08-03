#!/usr/bin/env python3
"""
シンプルに下矢印で25開成.pdfまで移動
"""
import subprocess
import time
import pyautogui

def simple_down_arrow_navigation():
    """下矢印だけで25開成.pdfまで移動"""
    
    print("🎯 bunkoOCRのファイルダイアログで25開成.pdfを選択")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルリストをクリック（21開成.pdfの辺り）
    print("\n📂 ファイルリストをクリック...")
    pyautogui.click(550, 380)  # 21開成.pdfの辺り
    time.sleep(0.5)
    
    # 下矢印で25まで移動（21の後に25があるはず）
    print("\n⬇️ 下矢印で25開成.pdfまで移動...")
    for i in range(4):  # 21→22→23→24→25
        pyautogui.press('down')
        time.sleep(0.5)
        print(f"   ↓ {i+1}/4")
    
    # ファイルを選択
    print("\n✅ ファイルを選択（Enter）...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開く
    print("📂 開く（もう一度Enter）...")
    pyautogui.press('return')
    
    print("\n🎉 完了！")

if __name__ == "__main__":
    simple_down_arrow_navigation()