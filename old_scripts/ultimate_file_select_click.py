#!/usr/bin/env python3
"""
究極の「ファイルから選択」クリック方法
"""
import pyautogui
import time
import subprocess

def ultimate_file_select_click():
    """あらゆる方法で「ファイルから選択」をクリック"""
    
    print("🔥 絶対に「ファイルから選択」をクリックします！")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 方法1: 画像認識でクリック
    print("\n🎯 方法1: 画像認識を試します...")
    try:
        # ファイルアイコンの位置を探す
        file_icon = pyautogui.locateOnScreen('/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns', confidence=0.5)
        if file_icon:
            pyautogui.click(file_icon)
            print("✅ アイコンを見つけてクリック！")
            return
    except:
        pass
    
    # 方法2: テキスト「ファイル」を含む領域をクリック
    print("\n🎯 方法2: より広い範囲をクリック...")
    # 上から3番目のメニュー項目の領域全体をクリック
    y_positions = [130, 135, 139, 140, 145, 150]  # 複数のY座標
    x_positions = [40, 60, 80, 100, 120, 140]     # 複数のX座標
    
    for y in y_positions:
        for x in x_positions:
            print(f"   クリック: ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(0.2)
    
    # 方法3: ダブルクリック
    print("\n🎯 方法3: ダブルクリックを試します...")
    pyautogui.doubleClick(100, 139)
    time.sleep(1)
    
    # 方法4: 右クリックしてから左クリック
    print("\n🎯 方法4: 右クリック後に左クリック...")
    pyautogui.rightClick(100, 139)
    time.sleep(0.5)
    pyautogui.click(100, 139)
    
    # 方法5: ドラッグ操作
    print("\n🎯 方法5: ドラッグ操作...")
    pyautogui.moveTo(40, 139)
    pyautogui.dragTo(140, 139, duration=0.5)
    pyautogui.click()
    
    print("\n🔥 全ての方法を試しました！")
    print("📂 ファイルダイアログが開いているはずです")

if __name__ == "__main__":
    ultimate_file_select_click()