#!/usr/bin/env python3
"""
右側のファイルリストで25開成.pdfをクリック
"""
import subprocess
import time
import pyautogui

def click_pdf_in_file_list():
    """右側のファイルリストでPDFをクリック"""
    
    print("📄 右側のファイルリストで25開成.pdfをクリック")
    
    # bunkoOCRをアクティブに
    subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
    time.sleep(0.5)
    
    # 右側のファイルリストエリアをクリック
    print("\n1️⃣ 右側のファイルリストをクリック...")
    pyautogui.click(550, 300)  # 右側のファイルリストエリア
    time.sleep(0.5)
    
    # リストの一番下へ
    print("2️⃣ Endキーでリストの最後へ...")
    pyautogui.press('end')
    time.sleep(0.5)
    
    # 25開成.pdfは最後の方にあるはず
    # 上矢印で少し戻る
    print("3️⃣ 上矢印で25開成.pdfを探す...")
    for i in range(3):
        pyautogui.press('up')
        time.sleep(0.3)
    
    # ダブルクリックで開く
    print("\n4️⃣ ダブルクリックで開く...")
    pyautogui.doubleClick()
    
    print("\n✅ PDFファイルを開きました！")

if __name__ == "__main__":
    click_pdf_in_file_list()