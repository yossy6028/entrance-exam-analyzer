#!/usr/bin/env python3
"""
シンプルに正確な座標でクリック
"""
import pyautogui
import time
import subprocess

# フェイルセーフを一時的に無効化
pyautogui.FAILSAFE = False

def simple_precise_click():
    """シンプルに正確な座標でクリック"""
    
    print("📍 「ファイルから選択」を正確にクリックします")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1.5)
    
    # スクリーンショットから判断した正確な座標
    # 「ファイルから選択」の中央
    x = 103  # "ファイルから選択"のテキスト中央
    y = 139  # 3番目のメニュー項目の中央
    
    print(f"🎯 座標 ({x}, {y}) をクリック")
    
    # 確実にクリック
    pyautogui.moveTo(x, y, duration=0.5)  # ゆっくり移動
    time.sleep(0.5)
    pyautogui.click()  # クリック
    
    print("✅ クリックしました！")
    
    # 少し待つ
    time.sleep(2)
    
    # もう一度クリック（念のため）
    print("🎯 もう一度クリック（念のため）")
    pyautogui.click(x, y)
    
    print("\n📂 ファイルダイアログが開いているはずです")
    
    # フェイルセーフを元に戻す
    pyautogui.FAILSAFE = True

if __name__ == "__main__":
    simple_precise_click()