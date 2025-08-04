#!/usr/bin/env python3
"""
フォルダをナビゲートして開成PDFを見つける
"""
import pyautogui
import time

def navigate_folders_seriously():
    """フォルダを順番に開いて開成PDFを見つける"""
    
    print("📂 フォルダナビゲーション開始！")
    
    # まず検索をクリア
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # リストビューで「開成」を探す
    print("\n🔍 「開成」フォルダを探します...")
    
    # 「か」を入力してカ行まで移動
    pyautogui.typewrite('か')
    time.sleep(0.5)
    
    # 下矢印で「開成」まで移動（開成中学校フォルダの可能性）
    for i in range(5):
        pyautogui.press('down')
        time.sleep(0.2)
        print(f"↓ {i+1}/5")
    
    # Enterでフォルダを開く
    print("\n📁 フォルダを開く...")
    pyautogui.press('return')
    time.sleep(2)
    
    # フォルダ内で「2025」を含むファイルを選択
    print("\n📄 「2025」で始まるファイルを選択...")
    pyautogui.typewrite('2')
    time.sleep(0.3)
    pyautogui.typewrite('0')
    time.sleep(0.3)
    pyautogui.typewrite('2')
    time.sleep(0.3)
    pyautogui.typewrite('5')
    time.sleep(0.5)
    
    # ファイルを開く
    print("\n✅ ファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n🎉 完了！")

if __name__ == "__main__":
    navigate_folders_seriously()