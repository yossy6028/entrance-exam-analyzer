#!/usr/bin/env python3
"""
過去に成功した座標でbunkoOCRを操作して開成中PDFを選択
"""
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path


def click_and_select_kaisei_with_success_coords():
    """過去に成功した座標(689, 475)でファイルダイアログを開いて開成中PDFを選択"""
    
    print(f"\n{'='*60}")
    print(f"bunkoOCRを使用した開成中学校2025年度分析（成功座標使用）")
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
    
    # 過去に成功した座標でクリック
    print("\n📂 PDFファイル選択ボタンをクリック...")
    print("   座標: x=689, y=475（過去の成功座標）")
    pyautogui.click(x=689, y=475)  # PDFファイル選択ボタン
    time.sleep(2)
    
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
    time.sleep(2)
    
    print("\n✅ PDFファイルを選択しました！")
    
    # OCR実行ボタンをクリック（y座標を調整）
    print("\n🔍 OCR処理を実行...")
    print("   座標: x=689, y=680（実行ボタン）")
    pyautogui.click(x=689, y=680)  # 実行ボタン
    
    print("\n⏳ OCR処理が開始されました")
    print("   処理には2-3分かかります...")
    print("\n処理が完了したら、以下のコマンドを実行してください：")
    print("   cd /Users/yoshiikatsuhiko/entrance_exam_analyzer")
    print("   python check_latest_bunko_result.py")


def main():
    """メイン処理"""
    click_and_select_kaisei_with_success_coords()


if __name__ == "__main__":
    main()