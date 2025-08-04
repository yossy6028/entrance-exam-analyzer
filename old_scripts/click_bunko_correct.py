#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」を手動で確認してクリック
"""
import pyautogui
import time
import subprocess

def manual_click_position():
    """手動でボタン位置を確認してクリック"""
    
    print("📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    print("\n⚠️  手動操作が必要です:")
    print("1. bunkoOCRウィンドウで「ファイルから選択」ボタンを見つけてください")
    print("2. 5秒後にマウスの位置を記録します")
    print("3. マウスを「ファイルから選択」ボタンの上に置いてください")
    
    for i in range(5, 0, -1):
        print(f"\r{i}秒...", end='', flush=True)
        time.sleep(1)
    
    # 現在のマウス位置を取得
    x, y = pyautogui.position()
    print(f"\n\n✅ ボタン位置を記録: x={x}, y={y}")
    
    # 位置を保存
    with open("bunko_button_correct_position.txt", "w") as f:
        f.write(f"ファイルから選択ボタン: x={x}, y={y}\n")
        f.write(f"記録日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # クリックする
    print("\n🖱️ クリックします...")
    pyautogui.click(x, y)
    
    print("\n✅ クリックしました！")
    print(f"📝 位置情報を bunko_button_correct_position.txt に保存しました")
    
    return x, y

if __name__ == "__main__":
    manual_click_position()