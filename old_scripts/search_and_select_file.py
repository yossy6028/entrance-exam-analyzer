#!/usr/bin/env python3
"""
検索機能を使って確実にファイルを選択
"""
import pyautogui
import time
import subprocess

def search_and_select_file(filename="25"):
    """検索機能を使って確実にファイルを選択"""
    
    print(f"🔍 検索機能を使って{filename}開成.pdfを選択")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルダイアログ内で検索
    print(f"\n1️⃣ 検索ボックスを開く（Cmd+F）...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    
    # 既存の検索をクリア
    pyautogui.hotkey('cmd', 'a')  # 全選択
    time.sleep(0.2)
    pyautogui.press('delete')      # 削除
    time.sleep(0.2)
    
    # ファイル名を入力
    print(f"2️⃣ 「{filename}開成」を入力...")
    pyautogui.typewrite(f"{filename}開成")
    time.sleep(1)
    
    # 検索結果にフォーカス
    print("3️⃣ 検索結果を選択...")
    pyautogui.press('escape')  # 検索ボックスを閉じる
    time.sleep(0.5)
    
    # 検索結果の最初のファイルが選択されているはず
    # 念のため下矢印→上矢印で確認
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('up')
    time.sleep(0.3)
    
    # ファイルを開く
    print("4️⃣ ファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print(f"\n✅ {filename}開成.pdfを選択しました！")

if __name__ == "__main__":
    # テスト：25開成.pdfを選択
    search_and_select_file("25")