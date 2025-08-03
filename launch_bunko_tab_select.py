#!/usr/bin/env python3
"""
bunkoOCRでタブキーを使って「ファイルから選択」を選択
"""
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path


def launch_bunko_ocr_kaisei_with_tab():
    """タブキーでメニューを選択してbunkoOCRで開成中2025年を処理"""
    
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
    
    # タブキーで「ファイルから選択」まで移動
    print("\n⌨️ タブキーでメニューを選択...")
    print("1つ目: カメラ撮影")
    print("2つ目: 写真ライブラリから選択")
    print("3つ目: ファイルから選択 ← これを選択します")
    
    # タブキーを押してメニューにフォーカス
    print("\nタブキーを押してメニューにフォーカス...")
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # 上矢印キーを5回押して上限まで移動
    print("上矢印キーを5回押して上限まで移動...")
    for _ in range(5):
        pyautogui.press('up')
        time.sleep(0.2)
    
    # 下矢印キーを2回押して「ファイルから選択」に移動
    print("下矢印キーを2回押して「ファイルから選択」に移動...")
    pyautogui.press('down')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.5)
    
    print("\n✅ 「ファイルから選択」を選択しました")
    
    # Enterキーで決定
    print("📂 Enterキーで選択を確定...")
    pyautogui.press('return')
    time.sleep(2)
    
    # ファイルダイアログでPDFを選択
    print("\n📄 PDFファイルを選択中...")
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')  # パス入力ダイアログ
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')  # パスをペースト
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')  # ファイル選択
    
    print("\n🔍 自動OCR処理が開始されました...")
    print("⏳ 処理完了まで約2-3分お待ちください...")
    
    # 処理完了を待つ（3分）
    for i in range(18):
        print(f"\r処理中... {i*10}/180秒", end='', flush=True)
        time.sleep(10)
    
    print("\n\n✅ OCR処理が完了しました！")
    
    # 結果の場所を確認
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    
    # 最新のフォルダを取得
    folders = [d for d in results_dir.iterdir() if d.is_dir()]
    if folders:
        latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
        print(f"\n📁 OCR結果フォルダ: {latest_folder.name}")
        
        # テキストファイルを結合
        text_files = sorted(latest_folder.glob("text*.txt"))
        if text_files:
            combined_text = []
            for txt_file in text_files:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_text.append(f"=== {txt_file.name} ===\n{content}")
            
            # 結合したテキストを保存
            output_file = "開成2025_bunko.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(combined_text))
            
            print(f"✅ 結合テキストを保存: {output_file}")
            print(f"   総ページ数: {len(text_files)}")
            
            # 最初のページを確認
            with open(text_files[0], 'r', encoding='utf-8') as f:
                first_page = f.read()[:200]
                print(f"\n📄 最初のページの内容:")
                print(first_page)
                
                # 開成中学校の確認
                if "開成" in first_page or "令和七年度" in first_page:
                    print("\n✅ 開成中学校のPDFが正しく処理されました！")
                else:
                    print("\n⚠️  異なるPDFが処理されている可能性があります")
            
            return output_file
    
    return None


def main():
    """メイン処理"""
    
    # bunkoOCRで処理
    text_file = launch_bunko_ocr_kaisei_with_tab()
    
    if text_file:
        print(f"\n🎯 次のステップ:")
        print(f"1. python analyze_kaisei_2025_bunko.py を実行")
        print(f"2. 分析結果を確認")
    else:
        print("\n❌ OCR処理に失敗しました")


if __name__ == "__main__":
    main()