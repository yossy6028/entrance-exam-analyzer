#!/usr/bin/env python3
"""
bunkoOCR自動実行スクリプト
手動操作を最小限にした効率的な処理
"""
import subprocess
import time
from pathlib import Path
from datetime import datetime


def launch_bunko_ocr_for_files(pdf_files):
    """複数のPDFファイルをbunkoOCRで順番に開く"""
    
    bunko_app = "/Applications/bunkoOCR.app"
    
    print("=== bunkoOCR 自動起動スクリプト ===\n")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 ファイル {i}/{len(pdf_files)}: {Path(pdf_path).name}")
        
        # bunkoOCRでファイルを開く
        subprocess.run(["open", "-a", bunko_app, pdf_path])
        
        print("\n【手動操作】")
        print("1. bunkoOCRでOCRボタンをクリック")
        print("2. 処理完了後、テキストファイルを保存")
        print("3. 次のファイルに進む場合はこのウィンドウに戻る")
        
        if i < len(pdf_files):
            input("\nEnterキーで次のファイルへ...")
        
    print("\n✅ すべてのファイルの起動が完了しました")


def create_processing_guide():
    """処理ガイドを作成"""
    
    guide = """
=== bunkoOCR 処理ガイド ===

【事前準備】
1. bunkoOCRの設定を確認
   - 2pass OCR: ON
   - PDF dpi: 300以上
   - Transformerによる無補正: ON
   - 見開き2ページとして処理: ON

【処理フロー】
1. このスクリプトを実行
   python bunko_ocr_auto_runner.py

2. bunkoOCRが起動してPDFが開く

3. 画面下部のOCRボタンをクリック

4. 処理完了後の保存方法：
   - メニュー > ファイル > テキストファイルを保存
   - または Command + S
   - ファイル名: [元のファイル名]_bunko.txt

5. 複数ファイルの場合は、ターミナルでEnterキーを押して次へ

【結果の確認】
- 保存場所: 指定したフォルダまたはデスクトップ
- iCloud結果: ~/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results/

【トラブルシューティング】
- 文字化けがある場合: 設定で「全角文字に揃える」をON
- 縦書きが正しく認識されない: 「見開き2ページとして処理」を確認
- 処理が遅い: PDF dpiを下げる（ただし精度も下がる）
"""
    
    print(guide)
    
    # ガイドをファイルに保存
    with open("bunkoOCR_guide.txt", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("\n📝 ガイドを bunkoOCR_guide.txt に保存しました")


def find_exam_pdfs():
    """入試問題PDFを検索"""
    
    base_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問")
    
    # 各学校のPDFを探す
    schools = ["渋渋", "桜蔭", "開成", "麻布", "武蔵"]
    found_pdfs = []
    
    for school in schools:
        school_path = base_path / school
        if school_path.exists():
            pdfs = list(school_path.glob("*.pdf"))
            for pdf in pdfs[:2]:  # 各学校最大2ファイル
                found_pdfs.append(str(pdf))
    
    return found_pdfs


def main():
    """メイン実行"""
    
    print("bunkoOCR 自動起動スクリプト\n")
    
    # 処理対象を選択
    print("処理対象を選択してください:")
    print("1. 渋渋15年度のみ")
    print("2. 複数の入試問題PDF")
    print("3. 処理ガイドを表示")
    
    # 自動的に1を選択（スクリプト実行時）
    choice = "1"
    
    if choice == "3":
        create_processing_guide()
        return
    
    elif choice == "2":
        pdf_files = find_exam_pdfs()
        if pdf_files:
            print(f"\n見つかったPDF: {len(pdf_files)}ファイル")
            for pdf in pdf_files[:5]:  # 最初の5ファイルを表示
                print(f"  - {Path(pdf).name}")
            
            launch_bunko_ocr_for_files(pdf_files[:3])  # 最初の3ファイル
        else:
            print("PDFファイルが見つかりません")
    
    else:  # choice == "1"
        pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
        
        if Path(pdf_path).exists():
            print(f"\n対象ファイル: {Path(pdf_path).name}")
            print(f"ファイルサイズ: {Path(pdf_path).stat().st_size / 1024 / 1024:.1f} MB")
            
            # bunkoOCRで開く
            print("\nbunkoOCRを起動します...")
            subprocess.run(["open", "-a", "/Applications/bunkoOCR.app", pdf_path])
            
            print("\n" + "="*60)
            print("bunkoOCRが起動しました")
            print("="*60)
            print("\n【次の手順】")
            print("1. bunkoOCRウィンドウでOCRボタンをクリック")
            print("2. 処理完了後、メニューから「テキストファイルを保存」")
            print("3. ファイル名: 15渋渋_bunko.txt として保存")
            print("\n処理時間の目安: 3-5分（PDFのページ数による）")
            
            # 結果の場所を案内
            print("\n【結果の保存場所】")
            print("1. 手動保存: 選択したフォルダ")
            print("2. 自動保存（iCloud）:")
            print(f"   ~/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results/")
            
        else:
            print(f"エラー: ファイルが見つかりません: {pdf_path}")


if __name__ == "__main__":
    main()
    
    # 処理完了の確認
    print("\n" + "="*60)
    print("スクリプト実行完了")
    print("bunkoOCRでの処理を続けてください")
    print("="*60)