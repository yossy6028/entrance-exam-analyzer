#!/usr/bin/env python3
"""
25開成.pdfを直接クリック
"""
import subprocess
import time
import pyautogui

def click_25_kaisei_directly():
    """ファイルを直接クリックして選択"""
    
    print("🎯 bunkoOCRをアクティブに...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 検索をキャンセル
    print("❌ 検索をキャンセル...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # ファイルリストの下の方をスクロール
    print("\n📜 下にスクロール...")
    pyautogui.click(600, 350)  # ファイルリストにフォーカス
    time.sleep(0.5)
    
    # End キーでリストの最後へ
    print("⬇️ Endキーでリストの最後へ...")
    pyautogui.press('end')
    time.sleep(0.5)
    
    # 上矢印で少し戻る（25開成.pdfを探す）
    print("⬆️ 上矢印で25開成.pdfを探す...")
    for i in range(5):
        pyautogui.press('up')
        time.sleep(0.3)
    
    # ファイルを選択
    print("\n✅ Enterでファイルを選択...")
    pyautogui.press('return')
    time.sleep(0.5)
    
    # 開く
    print("📂 もう一度Enterで開く...")
    pyautogui.press('return')

if __name__ == "__main__":
    click_25_kaisei_directly()