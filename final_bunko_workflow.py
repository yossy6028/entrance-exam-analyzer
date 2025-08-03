#!/usr/bin/env python3
"""
最終版：bunkoOCRワークフロー（上8回版）
"""
import pyautogui
import time
import subprocess
import pyperclip

def final_bunko_workflow():
    """完全なbunkoOCRワークフロー（修正版）"""
    
    print("🚀 bunkoOCR完全ワークフロー開始（最終版）")
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
    
    # 上8回（5回では足りない場合がある）
    for i in range(8):
        pyautogui.press('up')
        time.sleep(0.2)
        print(f"   ↑ {i+1}/8")
    
    # 下2回
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    print("   ✅ 「ファイルから選択」を選択")
    
    # 3. スペースキーで開く！！！
    print("\n3️⃣ 🔥 スペースキーで開く！！！")
    pyautogui.press('space')
    time.sleep(2)
    
    print("   ✅ ファイルダイアログが開きました！")
    
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
    
    # 7. 25開成.pdfを探す
    print("\n7️⃣ 下矢印で25開成.pdfを探す...")
    # ファイルリストを下に移動（15→16→...→25）
    for i in range(12):  # 十分な回数
        pyautogui.press('down')
        time.sleep(0.2)
        print(f"   ↓ {i+1}/12")
    
    # 8. ファイルを開く
    print("\n8️⃣ Enterキーでファイルを開く...")
    pyautogui.press('return')
    time.sleep(0.5)
    pyautogui.press('return')  # 開くボタン
    
    print("\n✅ 完了！OCR処理が開始されます")
    print("⏳ 処理には2-3分かかります")
    print("\n処理完了後: python check_latest_bunko_result.py")

if __name__ == "__main__":
    final_bunko_workflow()