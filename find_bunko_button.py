#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」ボタンの位置を特定するスクリプト
"""
import subprocess
import time
import pyautogui
import pyperclip


def find_file_select_button():
    """bunkoOCRの「ファイルから選択」ボタンの位置を特定"""
    
    print("🔍 bunkoOCRのボタン位置を特定します...")
    print("\n【準備】")
    print("1. bunkoOCRを起動します")
    print("2. マウスを「ファイルから選択」ボタンの上に置いてください")
    print("3. 5秒後に位置を記録します")
    
    # bunkoOCRを起動
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    print("\n⏳ マウスを「ファイルから選択」ボタンの上に置いてください...")
    for i in range(5, 0, -1):
        print(f"{i}秒...", end=' ', flush=True)
        time.sleep(1)
    
    # マウスの位置を取得
    x, y = pyautogui.position()
    print(f"\n\n✅ ボタンの位置: x={x}, y={y}")
    
    # 位置を保存
    with open("bunko_button_positions.txt", "w") as f:
        f.write(f"ファイルから選択ボタン: x={x}, y={y}\n")
    
    print(f"\n📝 位置情報を bunko_button_positions.txt に保存しました")
    
    # テストクリック
    print("\n🖱️ テストクリックを実行しますか？ (y/n): ", end='')
    
    return x, y


def quick_launch_with_position():
    """保存された位置でbunkoOCRを操作"""
    
    print("\n📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # アプリケーションウィンドウの上から3つ目のメニュー「ファイルから選択」
    # 一般的な位置（調整が必要な場合があります）
    print("\n🖱️ 「ファイルから選択」をクリックします...")
    
    # ウィンドウの中央付近、上から3つ目のボタンあたり
    # これは推定値なので、実際の位置に合わせて調整が必要
    pyautogui.click(x=700, y=300)  # 仮の座標
    
    print("✅ クリックしました")
    print("\nもし正しくクリックされていない場合は、")
    print("python find_bunko_button.py を実行して正確な位置を特定してください")


if __name__ == "__main__":
    print("1. ボタン位置を特定する")
    print("2. 推定位置でクリックを試す")
    choice = input("\n選択 (1/2): ")
    
    if choice == "1":
        find_file_select_button()
    else:
        quick_launch_with_position()