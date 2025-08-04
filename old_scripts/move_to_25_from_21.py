#!/usr/bin/env python3
"""
21開成.pdfから25開成.pdfへ移動
"""
import subprocess
import time
import pyautogui

def move_to_25_from_21():
    """21から25へ移動（4つ下）"""
    
    print("📄 21開成.pdfから25開成.pdfへ移動します")
    print("   21 → 22 → 23 → 24 → 25")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 下矢印4回で25へ
    print("\n⬇️ 下矢印4回で25開成.pdfへ...")
    for i in range(4):
        pyautogui.press('down')
        time.sleep(0.5)
        print(f"   ↓ {i+1}/4 → {21+i+1}開成.pdf")
    
    print("\n✅ 25開成.pdfを選択しました！")
    
    # Enterで開く
    print("📂 Enterキーでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # もう一度Enterで「開く」ボタン
    print("📂 もう一度Enterで「開く」...")
    pyautogui.press('return')
    
    print("\n🎉 25開成.pdfを開きました！")
    print("🔍 OCR処理が開始されます")

if __name__ == "__main__":
    move_to_25_from_21()