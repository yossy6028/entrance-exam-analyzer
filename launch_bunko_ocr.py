#!/usr/bin/env python3
"""
bunkoOCRアプリを起動してPDFを処理する方法
"""
import subprocess
import os
import time
from pathlib import Path


def launch_bunko_ocr():
    """bunkoOCRアプリを起動"""
    
    app_path = "/Applications/bunkoOCR.app"
    
    # アプリが存在するか確認
    if not os.path.exists(app_path):
        print("bunkoOCRアプリが見つかりません")
        return False
    
    print("bunkoOCRアプリを起動します...")
    
    # 方法1: openコマンドを使用（推奨）
    try:
        subprocess.run(["open", app_path], check=True)
        print("✅ bunkoOCRが起動しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"起動エラー: {e}")
        return False


def launch_bunko_ocr_with_file(file_path: str):
    """bunkoOCRアプリを特定のファイルで起動"""
    
    app_path = "/Applications/bunkoOCR.app"
    
    if not os.path.exists(file_path):
        print(f"ファイルが見つかりません: {file_path}")
        return False
    
    print(f"bunkoOCRでファイルを開きます: {file_path}")
    
    # ファイルを指定して起動
    try:
        subprocess.run(["open", "-a", app_path, file_path], check=True)
        print("✅ bunkoOCRが起動し、ファイルが開かれました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"起動エラー: {e}")
        return False


def wait_for_bunko_ocr_result(output_dir: str, timeout: int = 300):
    """bunkoOCRの処理結果を待つ"""
    
    results_dir = Path("/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results")
    
    print(f"bunkoOCRの処理を待っています（最大{timeout}秒）...")
    
    # 処理開始前の結果フォルダ数を記録
    initial_results = set(results_dir.iterdir()) if results_dir.exists() else set()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 新しい結果フォルダを探す
        current_results = set(results_dir.iterdir()) if results_dir.exists() else set()
        new_results = current_results - initial_results
        
        if new_results:
            # 新しい結果が見つかった
            latest_result = max(new_results, key=lambda x: x.stat().st_mtime)
            print(f"✅ 新しい結果が見つかりました: {latest_result.name}")
            return latest_result
        
        time.sleep(2)  # 2秒待機
    
    print("⚠️ タイムアウト: 結果が見つかりませんでした")
    return None


def process_pdf_with_bunko_ocr(pdf_path: str):
    """PDFをbunkoOCRで処理する完全なワークフロー"""
    
    print(f"\n=== bunkoOCRでPDFを処理 ===")
    print(f"対象: {pdf_path}")
    
    # 1. bunkoOCRでPDFを開く
    if not launch_bunko_ocr_with_file(pdf_path):
        return None
    
    print("\n【次の手順を実行してください】")
    print("1. bunkoOCRアプリが起動します")
    print("2. PDFが表示されたら、OCR処理を開始してください")
    print("3. 処理が完了するまで待ちます")
    print("4. 処理結果は自動的に検出されます")
    
    # 2. 結果を待つ
    result_dir = wait_for_bunko_ocr_result("", timeout=300)
    
    if result_dir:
        # 3. 結果のテキストファイルを結合
        text_files = sorted(result_dir.glob("text*.txt"))
        
        if text_files:
            combined_text = []
            for text_file in text_files:
                with open(text_file, 'r', encoding='utf-8') as f:
                    combined_text.append(f.read())
            
            # 結果を保存
            output_path = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_bunko.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(combined_text))
            
            print(f"\n✅ OCR結果を保存しました: {output_path}")
            print(f"   総文字数: {sum(len(t) for t in combined_text)}文字")
            
            return output_path
    
    return None


def main():
    """使用例"""
    
    # 渋渋15年度PDFを処理
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    
    # 基本的な起動
    print("【基本的な起動方法】")
    launch_bunko_ocr()
    
    print("\n【ファイルを指定して起動】")
    launch_bunko_ocr_with_file(pdf_path)
    
    print("\n【自動処理の流れ】")
    print("1. bunkoOCRアプリでPDFを開く")
    print("2. 手動でOCR処理を開始")
    print("3. 結果が保存されるのを待つ")
    print("4. テキストファイルを自動的に取得")
    
    # 実際の処理
    # result = process_pdf_with_bunko_ocr(pdf_path)
    # if result:
    #     print(f"\n処理完了: {result}")


if __name__ == "__main__":
    main()