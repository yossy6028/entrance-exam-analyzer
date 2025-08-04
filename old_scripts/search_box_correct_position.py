#!/usr/bin/env python3
"""
検索窓の正確な位置をクリック
"""
import pyautogui
import time
import subprocess

def search_box_correct_position():
    """検索窓の正確な位置をクリック"""
    
    print("🔍 検索窓を正確にクリックします")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットから見た検索窓の位置
    # 虫眼鏡アイコンの右側のテキストフィールド部分
    print("\n1️⃣ 検索窓をクリック...")
    # 検索窓のテキストフィールド部分を正確にクリック
    pyautogui.click(700, 39)  # より正確な座標
    time.sleep(0.5)
    
    # クリックがうまくいかない場合は、虫眼鏡アイコンをクリック
    print("2️⃣ 虫眼鏡アイコンもクリック...")
    pyautogui.click(530, 39)  # 虫眼鏡アイコン
    time.sleep(0.5)
    
    # タブキーで検索フィールドに移動
    print("3️⃣ タブキーで検索フィールドへ...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # テキストをクリア
    print("4️⃣ 検索窓をクリア...")
    pyautogui.hotkey('cmd', 'a')
    pyautogui.press('delete')
    
    # 25を入力
    print("5️⃣ 「25」を入力...")
    pyautogui.typewrite('25')
    time.sleep(1)
    
    print("\n✅ 検索窓に「25」を入力しました")

if __name__ == "__main__":
    search_box_correct_position()