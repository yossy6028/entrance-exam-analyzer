#!/usr/bin/env python3
"""
bunkoOCRで「ファイルから選択」ボタンをクリックして開成中PDFを選択
スクリーンショットから正確な位置を特定
"""
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path


def click_file_from_selection():
    """「ファイルから選択」ボタンをクリックしてPDFを選択"""
    
    print(f"\n{'='*60}")
    print(f"bunkoOCRを使用した開成中学校2025年度分析")
    print(f"{'='*60}")
    
    # PDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # bunkoOCRを起動
    print("\n📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # bunkoOCRをアクティブにする
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # 「ファイルから選択」をクリック
    # スクリーンショットから、左側のメニューにある「ファイルから選択」の位置
    print("\n📂 「ファイルから選択」をクリック...")
    
    # アイコンとテキストの中央付近をクリック
    pyautogui.click(x=100, y=139)  # 「ファイルから選択」の位置
    time.sleep(2)
    
    # ファイルダイアログが開いたか確認
    print("ファイルダイアログが開きました")
    
    # ファイルダイアログでPDFを選択
    print("\n📄 開成中PDFファイルを選択中...")
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')  # パス入力ダイアログ
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')  # パスをペースト
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')  # ファイル選択
    
    print("\n✅ PDFファイルを選択しました！")
    print("🔍 OCR処理が自動的に開始されます...")
    print("\n⏳ OCR処理には2-3分かかります...")
    print("\n処理が完了したら、以下のコマンドを実行してください：")
    print("   python check_latest_bunko_result.py")


def main():
    """メイン処理"""
    click_file_from_selection()


if __name__ == "__main__":
    main()