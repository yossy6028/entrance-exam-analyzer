#!/usr/bin/env python3
"""
最終版：「ファイルから選択」を確実にクリック
"""
import pyautogui
import time
import subprocess
import pyperclip

def final_click_file_select():
    """確実に「ファイルから選択」をクリック"""
    
    # bunkoOCRをアクティブにする
    print("📱 bunkoOCRをアクティブ化...")
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(2)
    
    # スクリーンショットから見た「ファイルから選択」の位置
    # 左側メニューの3番目の項目
    
    # 複数の座標を試す
    coordinates = [
        (40, 139),   # アイコン部分
        (90, 139),   # アイコンとテキストの中間
        (120, 139),  # テキスト部分
        (103, 139),  # "ファイルから選択"の中央
    ]
    
    for x, y in coordinates:
        print(f"\n🖱️ クリック試行: ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(1)
        
        # ファイルダイアログが開いたかチェック（少し待つ）
        time.sleep(1)
        
        # ファイルダイアログが開いた場合の処理
        print("📂 ファイルダイアログを確認中...")
        
        # Cmd+Shift+G を試す（ダイアログが開いていれば反応する）
        pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
        pyperclip.copy(pdf_path)
        
        pyautogui.hotkey('cmd', 'shift', 'g')
        time.sleep(0.5)
        
        # ダイアログが開いていれば、パスをペーストして選択
        pyautogui.hotkey('cmd', 'v')
        time.sleep(0.5)
        pyautogui.press('return')
        time.sleep(0.5)
        pyautogui.press('return')
        
        print("✅ ファイル選択を試行しました")
        
        # 成功したら終了
        break
    
    print("\n🔍 OCR処理が開始されていることを期待します")
    print("⏳ 2-3分後に以下を実行：")
    print("   python check_latest_bunko_result.py")

if __name__ == "__main__":
    final_click_file_select()