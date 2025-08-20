#!/usr/bin/env python3
"""
Yomitoku OCRのテストスクリプト
日本語特化OCRの動作確認とGoogle Cloud Vision APIとの比較
"""
import sys
import os
from pathlib import Path
import time
import json

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.yomitoku_processor import YomitokuProcessor


def test_yomitoku_simple():
    """Yomitokuの簡単なテスト"""
    
    print("=" * 70)
    print("Yomitoku OCR テスト")
    print("=" * 70)
    
    # テスト用PDFファイルを探す
    test_pdfs = [
        Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"),
        Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf"),
        Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/22年度ツール/家庭教師/2022過去問/2022開成.pdf"),
    ]
    
    pdf_path = None
    for pdf in test_pdfs:
        if pdf.exists():
            pdf_path = pdf
            break
    
    if not pdf_path:
        print("テスト用PDFファイルが見つかりません")
        return
    
    print(f"PDFファイル: {pdf_path.name}")
    print(f"ファイルサイズ: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    # Yomitokuプロセッサーを初期化
    print("Yomitokuを初期化中...")
    processor = YomitokuProcessor(
        use_lite=True,  # 軽量モデルを使用（高速）
        device="cpu"    # CPUを使用
    )
    
    # 処理開始
    start_time = time.time()
    
    print("処理を開始します...")
    print("（初回実行時はモデルのダウンロードが必要な場合があります）")
    print()
    
    try:
        # PDFの最初の3ページのみ処理（テスト用）
        result = processor.process_pdf(
            pdf_path,
            output_format="md",  # Markdown形式で出力
            output_dir=Path("yomitoku_test_output"),
            extract_figures=True,  # 図表も抽出
            visualize=False  # 可視化は省略
        )
        
        # 処理時間
        processing_time = time.time() - start_time
        
        # 結果を表示
        print("\n" + "=" * 70)
        print("処理結果:")
        print(f"  - 処理時間: {processing_time:.2f} 秒")
        print(f"  - ファイル名: {result['file_name']}")
        print(f"  - 総ページ数: {result['total_pages']}")
        print(f"  - 抽出文字数: {len(result['full_text'])}")
        
        # ページごとの情報
        if result['pages']:
            print("\nページごとの情報:")
            for page in result['pages'][:3]:  # 最初の3ページ
                print(f"  - ページ {page['page_number']}: {len(page['text'])} 文字")
                if page.get('tables'):
                    print(f"    表: {len(page['tables'])}個")
                if page.get('figures'):
                    print(f"    図: {len(page['figures'])}個")
        
        # 入試問題構造の検出結果
        if 'exam_structure' in result:
            structure = result['exam_structure']
            print("\n" + "=" * 70)
            print("検出された入試問題構造:")
            print(f"  - 複数の大問: {'あり' if structure.get('has_multiple_sections') else 'なし'}")
            if structure.get('sections'):
                print(f"  - 大問: {', '.join(structure['sections'][:5])}")
            print(f"  - 問題数: {structure.get('question_count', 0)}")
            print(f"  - 選択肢: {'あり' if structure.get('has_answer_choices') else 'なし'}")
            
            if structure.get('source_info'):
                print("  - 出典情報:")
                for key, value in structure['source_info'].items():
                    print(f"    - {key}: {value}")
                    
            if structure.get('themes'):
                print(f"  - 推定テーマ: {', '.join(structure['themes'])}")
        
        # テキストのサンプルを表示
        print("\n" + "=" * 70)
        print("抽出されたテキスト（最初の500文字）:")
        print("-" * 70)
        print(result['full_text'][:500])
        print("-" * 70)
        
        # 結果をファイルに保存
        output_dir = Path("yomitoku_test_output")
        output_dir.mkdir(exist_ok=True)
        
        # テキストファイルに保存
        text_output = output_dir / f"{pdf_path.stem}_yomitoku.txt"
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        print(f"\nテキストを保存: {text_output}")
        
        # JSON形式で詳細情報を保存
        json_output = output_dir / f"{pdf_path.stem}_yomitoku_summary.json"
        save_result = {
            'file_name': result['file_name'],
            'total_pages': result['total_pages'],
            'text_length': len(result['full_text']),
            'exam_structure': result.get('exam_structure', {}),
            'processing_time': processing_time
        }
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(save_result, f, ensure_ascii=False, indent=2)
        print(f"詳細情報を保存: {json_output}")
        
        print("\n✅ テスト成功！")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


def compare_ocr_methods():
    """YomitokuとGoogle Cloud Vision APIの比較"""
    
    pdf_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/22年度ツール/家庭教師/2022過去問/2022開成.pdf")
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        return
    
    print("=" * 70)
    print("OCR方法の比較テスト")
    print("=" * 70)
    print(f"PDFファイル: {pdf_path.name}")
    print()
    
    results_comparison = {}
    
    # 1. Yomitokuでテスト
    print("1. Yomitokuで処理中...")
    try:
        yomitoku_processor = YomitokuProcessor(use_lite=True, device="cpu")
        start_time = time.time()
        yomitoku_result = yomitoku_processor.process_pdf(
            pdf_path,
            output_format="json",
            output_dir=Path("comparison_output/yomitoku")
        )
        yomitoku_time = time.time() - start_time
        
        results_comparison['Yomitoku'] = {
            'time': yomitoku_time,
            'text_length': len(yomitoku_result['full_text']),
            'pages': yomitoku_result['total_pages'],
            'success': True
        }
        print(f"   完了: {yomitoku_time:.2f}秒, {len(yomitoku_result['full_text'])}文字")
        
    except Exception as e:
        print(f"   エラー: {e}")
        results_comparison['Yomitoku'] = {'success': False, 'error': str(e)}
    
    # 2. Google Cloud Vision APIでテスト
    print("\n2. Google Cloud Vision APIで処理中...")
    try:
        from modules.pdf_ocr_processor import PDFOCRProcessor
        
        # 環境変数を設定
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/yoshiikatsuhiko/.config/gcloud/application_default_credentials.json'
        
        gcv_processor = PDFOCRProcessor()
        start_time = time.time()
        gcv_result = gcv_processor.process_pdf(
            pdf_path,
            output_dir=Path("comparison_output/gcv")
        )
        gcv_time = time.time() - start_time
        
        results_comparison['Google Cloud Vision'] = {
            'time': gcv_time,
            'text_length': len(gcv_result['full_text']),
            'pages': gcv_result['total_pages'],
            'success': True
        }
        print(f"   完了: {gcv_time:.2f}秒, {len(gcv_result['full_text'])}文字")
        
    except Exception as e:
        print(f"   エラー: {e}")
        results_comparison['Google Cloud Vision'] = {'success': False, 'error': str(e)}
    
    # 比較結果を表示
    print("\n" + "=" * 70)
    print("比較結果:")
    print("-" * 70)
    
    for method, result in results_comparison.items():
        print(f"\n{method}:")
        if result['success']:
            print(f"  - 処理時間: {result['time']:.2f} 秒")
            print(f"  - 抽出文字数: {result['text_length']:,} 文字")
            print(f"  - ページ数: {result['pages']}")
        else:
            print(f"  - エラー: {result['error']}")
    
    # 速度比較
    if all(r.get('success', False) for r in results_comparison.values()):
        yomitoku_time = results_comparison['Yomitoku']['time']
        gcv_time = results_comparison['Google Cloud Vision']['time']
        
        print("\n" + "-" * 70)
        if yomitoku_time < gcv_time:
            speedup = gcv_time / yomitoku_time
            print(f"Yomitokuの方が {speedup:.1f}倍 高速")
        else:
            speedup = yomitoku_time / gcv_time
            print(f"Google Cloud Visionの方が {speedup:.1f}倍 高速")
        
        # 文字数の比較
        yomitoku_chars = results_comparison['Yomitoku']['text_length']
        gcv_chars = results_comparison['Google Cloud Vision']['text_length']
        
        diff_percent = abs(yomitoku_chars - gcv_chars) / max(yomitoku_chars, gcv_chars) * 100
        print(f"\n文字数の差: {diff_percent:.1f}%")
        
        if yomitoku_chars > gcv_chars:
            print(f"Yomitokuの方が {yomitoku_chars - gcv_chars:,} 文字多く抽出")
        else:
            print(f"Google Cloud Visionの方が {gcv_chars - yomitoku_chars:,} 文字多く抽出")


def test_cli():
    """Yomitoku CLIの直接テスト"""
    
    print("=" * 70)
    print("Yomitoku CLI テスト")
    print("=" * 70)
    
    # テスト用画像を探す
    test_image = Path("~/dots.ocr/demo/demo_image1.jpg").expanduser()
    
    if not test_image.exists():
        print("テスト画像が見つかりません")
        # PDFから画像を生成
        from modules.yomitoku_processor import YomitokuProcessor
        processor = YomitokuProcessor()
        # ここでPDFから画像を生成する処理を追加可能
        return
    
    # Yomitoku CLIを実行
    import subprocess
    
    cmd = [
        "yomitoku",
        str(test_image),
        "-f", "md",
        "-o", "yomitoku_cli_test",
        "--lite",
        "-v"
    ]
    
    print("実行コマンド:")
    print(" ".join(cmd))
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ CLI実行成功")
        print("\n出力:")
        print(result.stdout[:500])
        
    except subprocess.CalledProcessError as e:
        print("❌ CLI実行失敗")
        print(f"エラー: {e.stderr}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Yomitoku OCR テスト')
    parser.add_argument('--compare', action='store_true',
                       help='YomitokuとGoogle Cloud Vision APIを比較')
    parser.add_argument('--cli', action='store_true',
                       help='Yomitoku CLIを直接テスト')
    parser.add_argument('--pdf', type=str,
                       help='テストするPDFファイルのパス')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_ocr_methods()
    elif args.cli:
        test_cli()
    else:
        test_yomitoku_simple()
    
    print("\nテスト完了")
    print("=" * 70)