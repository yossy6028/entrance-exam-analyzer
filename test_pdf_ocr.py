#!/usr/bin/env python3
"""
PDF OCR機能のテストスクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.pdf_ocr_processor import PDFOCRProcessor


def test_pdf_ocr():
    """PDF OCR処理のテスト"""
    
    # テスト用PDFファイル（例として早稲田実業のPDFを使用）
    pdf_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf")
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        return
    
    print(f"PDFファイル: {pdf_path.name}")
    print("=" * 60)
    
    try:
        # 環境変数を設定（Google Cloud認証用）
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/yoshiikatsuhiko/.config/gcloud/application_default_credentials.json'
        
        # PDFOCRプロセッサーを初期化
        processor = PDFOCRProcessor(dpi=300)
        
        # PDFをOCR処理
        print("OCR処理を開始します...")
        result = processor.process_pdf(
            pdf_path,
            save_images=True,
            output_dir=Path("test_pdf_images")
        )
        
        # 結果を表示
        print("\n" + "=" * 60)
        print("OCR処理結果:")
        print(f"  - ファイル名: {result['file_name']}")
        print(f"  - 総ページ数: {result['total_pages']}")
        print(f"  - 抽出文字数: {len(result['full_text'])}")
        
        # 各ページの情報
        print("\nページごとの情報:")
        for page in result['pages']:
            print(f"  - ページ {page['page_number']}: "
                  f"{len(page['text'])} 文字, "
                  f"信頼度: {page['confidence']:.1%}, "
                  f"縦書き: {'はい' if page['is_vertical'] else 'いいえ'}")
        
        # テキストのサンプルを表示
        print("\n" + "=" * 60)
        print("抽出されたテキスト（最初の1000文字）:")
        print(result['full_text'][:1000])
        
        # 入試問題の構造を検出
        structure = processor.detect_exam_structure(result['full_text'])
        print("\n" + "=" * 60)
        print("検出された入試問題構造:")
        print(f"  - 複数の大問: {'あり' if structure['has_multiple_sections'] else 'なし'}")
        if structure['sections']:
            print(f"  - 大問: {', '.join(structure['sections'][:5])}")
        print(f"  - 問題数: {structure['question_count']}")
        print(f"  - 選択肢: {'あり' if structure['has_answer_choices'] else 'なし'}")
        
        # OCR結果をファイルに保存
        output_file = pdf_path.with_suffix('.ocr.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        print(f"\nOCR結果を保存しました: {output_file}")
        
    except ImportError as e:
        print(f"エラー: 必要なライブラリがインストールされていません")
        print(f"詳細: {e}")
        print("\n以下のコマンドでインストールしてください:")
        print("pip install google-cloud-vision pdf2image pillow")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


def test_main_app_with_pdf():
    """メインアプリケーションでPDFを処理するテスト"""
    from core.application import Application
    
    print("\n" + "=" * 60)
    print("メインアプリケーションでPDFを処理")
    print("=" * 60)
    
    app = Application()
    
    # PDFファイルのパスを直接指定
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf"
    
    # アプリケーションを実行
    success = app.run(pdf_path)
    
    if success:
        print("\n✅ PDFの処理が正常に完了しました")
    else:
        print("\n❌ PDFの処理に失敗しました")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF OCR機能のテスト")
    parser.add_argument("--full", action="store_true", 
                       help="メインアプリケーションでの完全なテストを実行")
    
    args = parser.parse_args()
    
    if args.full:
        test_main_app_with_pdf()
    else:
        test_pdf_ocr()