#!/usr/bin/env python3
"""
bunkoOCRで任意の年度の開成PDFを選択できる汎用版
"""
import pyautogui
import time
import subprocess
import pyperclip
import sys

def bunko_ocr_select_any_year(year="25"):
    """
    任意の年度の開成PDFを選択
    
    Args:
        year: 年度（例: "25", "21", "15"）
    """
    
    print(f"🚀 bunkoOCRで{year}開成.pdfを選択します")
    print("=" * 60)
    
    # 1. bunkoOCRをアクティブ化
    print("\n1️⃣ bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(2)
    
    # 2. キーボードナビゲーション
    print("\n2️⃣ キーボードナビゲーション...")
    print("   Tab → 上8回 → 下2回")
    
    # Tab
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # 上8回
    for i in range(8):
        pyautogui.press('up')
        time.sleep(0.2)
    
    # 下2回
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    print("   ✅ 「ファイルから選択」を選択")
    
    # 3. スペースキーで開く
    print("\n3️⃣ スペースキーでファイルダイアログを開く...")
    pyautogui.press('space')
    time.sleep(2)
    
    # 4. 過去問フォルダに移動
    print("\n4️⃣ 過去問フォルダに移動...")
    folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
    pyperclip.copy(folder_path)
    
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(2)
    
    # 5. 開成フォルダを探す
    print("\n5️⃣ 開成フォルダを検索...")
    pyautogui.hotkey('cmd', 'f')
    time.sleep(0.5)
    pyautogui.typewrite('開成')
    time.sleep(1)
    
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('return')  # フォルダを開く
    time.sleep(2)
    
    # 6. 右矢印でファイルリストへ移動
    print("\n6️⃣ 右矢印でファイルリストへ移動...")
    pyautogui.press('right')
    time.sleep(0.5)
    
    # 7. 年度に応じてファイルを探す
    print(f"\n7️⃣ {year}開成.pdfを探す...")
    
    # ファイルの順序マップ（実際のファイルリスト順）
    file_order = {
        "15": 0,
        "16": 1,
        "17": 2,
        "18": 3,
        "19": 4,
        "20": 5,
        "21": 6,
        "22": 7,
        "23": 8,
        "24": 9,
        "25": 10
    }
    
    # 目標ファイルの位置を取得
    if year in file_order:
        target_position = file_order[year]
        print(f"   目標: リストの{target_position + 1}番目")
        
        # 最初のファイル（15開成.pdf）から目標まで移動
        for i in range(target_position):
            pyautogui.press('down')
            time.sleep(0.3)
            print(f"   ↓ {i+1}/{target_position}")
    else:
        # 年度が不明な場合は文字入力で探す
        print(f"   「{year}」を入力してファイルを探す...")
        pyautogui.typewrite(year)
        time.sleep(1)
    
    # 8. ファイルを開く
    print(f"\n8️⃣ {year}開成.pdfを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print(f"\n✅ {year}開成.pdfを選択しました！")
    print("🔍 OCR処理が開始されます")
    print("⏳ 処理には2-3分かかります")

def main():
    """メイン処理"""
    # コマンドライン引数から年度を取得
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = "25"  # デフォルト
    
    bunko_ocr_select_any_year(year)

if __name__ == "__main__":
    main()