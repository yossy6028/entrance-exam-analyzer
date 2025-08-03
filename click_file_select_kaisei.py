#!/usr/bin/env python3
"""
bunkoOCRで「ファイルから選択」をクリックして開成中PDFを選択
"""
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path


def click_and_select_kaisei():
    """クリックでファイルダイアログを開いて開成中PDFを選択"""
    
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
    
    # まず上部のメニューをクリックして確実にフォーカス
    print("\n🖱️ bunkoOCRウィンドウにフォーカス...")
    pyautogui.click(x=1000, y=200)  # ウィンドウ上部をクリック
    time.sleep(0.5)
    
    # 「ファイルから選択」の位置を複数試す
    print("\n📂 「ファイルから選択」をクリックします...")
    
    # 候補1: ウィンドウ中央付近、上から3つ目のボタン
    click_positions = [
        (1000, 300),  # 上の方
        (1000, 350),  # 中間
        (1000, 400),  # 少し下
        (1071, 300),  # 前回の座標を上に調整
        (1071, 350),
    ]
    
    # 各位置を試す
    for i, (x, y) in enumerate(click_positions):
        print(f"\n試行 {i+1}: 座標({x}, {y})をクリック...")
        pyautogui.click(x=x, y=y)
        time.sleep(1)
        
        # ファイルダイアログが開いたかチェック（Cmd+Shift+Gが使えるか試す）
        try:
            pyperclip.copy("test")
            pyautogui.hotkey('cmd', 'shift', 'g')
            time.sleep(0.5)
            
            # ダイアログが開いた場合はEscで閉じて本番へ
            pyautogui.press('escape')
            time.sleep(0.5)
            
            print("✅ ファイルダイアログが開きました！")
            
            # 本番のパス入力
            print("\n📄 開成中PDFファイルを選択中...")
            pyperclip.copy(pdf_path)
            pyautogui.hotkey('cmd', 'shift', 'g')
            time.sleep(0.5)
            pyautogui.hotkey('cmd', 'v')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(1)
            pyautogui.press('return')  # ファイル選択
            
            print("\n✅ ファイルを選択しました！")
            print("🔍 OCR処理が開始されます...")
            
            return True
            
        except:
            print("❌ この位置ではダイアログが開きませんでした")
            continue
    
    # どれも失敗した場合
    print("\n⚠️  自動クリックに失敗しました")
    print("手動で「ファイルから選択」をクリックしてください")
    
    return False


def wait_for_ocr_completion():
    """OCR処理の完了を待機"""
    
    print("\n⏳ OCR処理中... (約2-3分)")
    
    # 3分待機
    for i in range(18):
        print(f"\r処理中... {i*10}/180秒", end='', flush=True)
        time.sleep(10)
    
    print("\n\n✅ OCR処理が完了しました！")
    
    # 結果を確認
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
                    return output_file
                else:
                    print("\n⚠️  異なるPDFが処理されている可能性があります")
    
    return None


def main():
    """メイン処理"""
    
    # ファイル選択
    if click_and_select_kaisei():
        # OCR完了を待機
        text_file = wait_for_ocr_completion()
        
        if text_file:
            print(f"\n🎯 次のステップ:")
            print(f"python analyze_kaisei_2025_bunko.py を実行してください")
    else:
        print("\n手動で操作を続けてください")


if __name__ == "__main__":
    main()