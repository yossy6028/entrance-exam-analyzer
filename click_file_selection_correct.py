#!/usr/bin/env python3
"""
bunkoOCRで「ファイルから選択」ボタンを正確にクリック
"""
import subprocess
import time
import pyautogui


def click_file_selection_menu():
    """「ファイルから選択」メニューを正確にクリック"""
    
    print(f"\n{'='*60}")
    print(f"bunkoOCRで「ファイルから選択」をクリック")
    print(f"{'='*60}")
    
    # bunkoOCRを起動
    print("\n📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 上から3つ目のメニュー「ファイルから選択」をクリック
    # OCRを行う → 写真ライブラリから選択 → ファイルから選択（3つ目）
    print("\n🖱️ 「ファイルから選択」（上から3つ目）をクリック...")
    
    # より正確な座標で試す
    # テキストの左側のアイコン部分をクリック
    pyautogui.click(x=40, y=139)  # アイコン部分
    time.sleep(1)
    
    # それでも開かない場合は、テキスト部分もクリック
    pyautogui.click(x=103, y=139)  # "ファイルから選択"のテキスト部分
    
    print("\n⏳ ファイルダイアログが開くのを待っています...")
    time.sleep(2)
    
    print("\nファイルダイアログが開いたら:")
    print("1. 開成のPDFを探す（ファイル名に「開成」「25」などが含まれるもの）")
    print("2. ファイルを選択してEnterキーを押す")
    print("3. OCR処理が完了するまで2-3分待つ")
    print("4. 完了したら以下のコマンドを実行：")
    print("   python check_latest_bunko_result.py")


def main():
    """メイン処理"""
    click_file_selection_menu()


if __name__ == "__main__":
    main()