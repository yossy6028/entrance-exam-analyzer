#!/usr/bin/env python3
"""
スクリーンショットから正確な座標で「ファイルから選択」をクリック
"""
import pyautogui
import time
import subprocess
import pyperclip

def click_exact_file_select():
    """正確な座標で「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # スクリーンショットから判断した正確な座標
    # 「ファイルから選択」のアイコンとテキストの中央付近
    click_x = 90   # アイコンとテキストの中間
    click_y = 139  # 「ファイルから選択」の行の中央
    
    print(f"「ファイルから選択」をクリック")
    print(f"座標: ({click_x}, {click_y})")
    
    # クリック
    pyautogui.click(click_x, click_y)
    print("✅ クリックしました")
    
    # ファイルダイアログが開くのを待つ
    time.sleep(2)
    
    # 開成中のPDFパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    print("\n📁 ファイルダイアログでPDFを選択...")
    
    # パスをコピー
    pyperclip.copy(pdf_path)
    
    # Cmd+Shift+G でパス入力
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enter 2回
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')
    
    print("\n✅ PDFファイルを選択しました！")
    print("🔍 OCR処理が自動的に開始されます")
    print("\n⏳ 処理には2-3分かかります")
    print("\n完了後: python check_latest_bunko_result.py")

if __name__ == "__main__":
    click_exact_file_select()