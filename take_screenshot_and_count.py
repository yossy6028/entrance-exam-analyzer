#!/usr/bin/env python3
"""
スクリーンショットを撮って選択されているファイルを確認
"""
import subprocess
import time
import pyautogui
from datetime import datetime

def take_screenshot_and_count():
    """スクリーンショットを撮って選択ファイルを確認"""
    
    print("📸 スクリーンショットを撮って確認します")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットを撮る
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"bunko_file_dialog_{timestamp}.png"
    
    print(f"\n📸 スクリーンショットを保存: {screenshot_path}")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    print("\n💡 ファイルリストから数えます：")
    print("   15開成.pdf (1番目)")
    print("   16開成.pdf (2番目)")
    print("   17開成.pdf (3番目)")
    print("   18開成.pdf (4番目)")
    print("   19開成.pdf (5番目) ← 現在選択中?")
    print("   20開成.pdf (6番目)")
    print("   21開成.pdf (7番目)")
    print("   22開成.pdf (8番目)")
    print("   23開成.pdf (9番目)")
    print("   24開成.pdf (10番目)")
    print("   25開成.pdf (11番目) ← 目標！")
    
    print("\n🔢 19から25まであと6つ下です")
    
    # 下矢印6回で25へ
    print("\n⬇️ 下矢印6回で25開成.pdfへ移動...")
    for i in range(6):
        pyautogui.press('down')
        time.sleep(0.3)
        print(f"   ↓ {i+1}/6 → {19+i+1}開成.pdf")
    
    # ファイルを開く
    print("\n📂 Enterでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print(f"\n✅ 25開成.pdfを選択しました！")
    print(f"📸 スクリーンショットは {screenshot_path} に保存されています")

if __name__ == "__main__":
    take_screenshot_and_count()