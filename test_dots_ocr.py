#!/usr/bin/env python3
"""
DotsOCR機能のテストスクリプト
DotsOCRを使用したPDF処理のテストと、既存のGoogle Cloud Vision APIとの比較
"""
import sys
import os
from pathlib import Path
import json
import time

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor
from modules.pdf_ocr_processor import PDFOCRProcessor


def test_dots_ocr_pdf():
    """DotsOCR PDF処理のテスト"""
    
    # テスト用PDFファイル（例として早稲田実業のPDFを使用）
    pdf_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf")
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        print("別のPDFファイルを指定してください")
        return
    
    print("=" * 70)
    print("DotsOCR PDF処理テスト")
    print("=" * 70)
    print(f"PDFファイル: {pdf_path.name}")
    print(f"ファイルサイズ: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        # DotsOCRプロセッサーを初期化
        print("DotsOCRプロセッサーを初期化中...")
        processor = DotsOCRPDFProcessor(
            model_path="./weights/DotsOCR",  # モデルパス（要インストール）
            use_gpu=True,
            dpi=300
        )
        
        # 処理開始時刻を記録
        start_time = time.time()
        
        # PDFをOCR処理
        print("DotsOCRでPDF処理を開始します...")
        print("（初回実行時はモデルのダウンロードが必要な場合があります）")
        print()
        
        result = processor.process_with_fallback(pdf_path)
        
        # 処理時間を計算
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
            for page in result['pages'][:3]:  # 最初の3ページのみ表示
                print(f"  - ページ {page['page_number']}: "
                      f"{len(page['text'])} 文字, "
                      f"縦書き: {'はい' if page['is_vertical'] else 'いいえ'}")
        
        # レイアウト要素の情報（DotsOCR特有）
        if 'layout_elements' in result and result['layout_elements']:
            print(f"\nレイアウト要素数: {len(result['layout_elements'])}")
            
            # 要素タイプ別の集計
            element_types = {}
            for element in result['layout_elements']:
                elem_type = element.get('type', 'Unknown')
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            print("要素タイプ別集計:")
            for elem_type, count in sorted(element_types.items()):
                print(f"  - {elem_type}: {count}")
        
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
        
        # テキストのサンプルを表示
        print("\n" + "=" * 70)
        print("抽出されたテキスト（最初の500文字）:")
        print("-" * 70)
        print(result['full_text'][:500])
        print("-" * 70)
        
        # 結果をファイルに保存
        output_dir = Path("dots_ocr_test_output")
        output_dir.mkdir(exist_ok=True)
        
        # テキストファイルに保存
        text_output = output_dir / f"{pdf_path.stem}_dots_ocr.txt"
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        print(f"\nテキストを保存: {text_output}")
        
        # JSON形式で詳細情報を保存
        json_output = output_dir / f"{pdf_path.stem}_dots_ocr.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            # layout_elementsは大きくなる可能性があるため、簡略化
            save_result = {
                'file_name': result['file_name'],
                'total_pages': result['total_pages'],
                'text_length': len(result['full_text']),
                'exam_structure': result.get('exam_structure', {}),
                'processing_time': processing_time,
                'layout_element_count': len(result.get('layout_elements', []))
            }
            json.dump(save_result, f, ensure_ascii=False, indent=2)
        print(f"詳細情報を保存: {json_output}")
        
    except ImportError as e:
        print(f"\nエラー: 必要なライブラリがインストールされていません")
        print(f"詳細: {e}")
        print("\nDotsOCRを使用するには、以下の手順でインストールしてください:")
        print("1. conda create -n dots_ocr python=3.12")
        print("2. conda activate dots_ocr")
        print("3. git clone https://github.com/rednote-hilab/dots.ocr.git")
        print("4. cd dots.ocr")
        print("5. pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128")
        print("6. pip install -e .")
        print("7. python3 tools/download_model.py")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


def compare_ocr_methods():
    """DotsOCRとGoogle Cloud Vision APIの比較"""
    
    pdf_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf")
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        return
    
    print("=" * 70)
    print("OCR方法の比較テスト")
    print("=" * 70)
    print(f"PDFファイル: {pdf_path.name}")
    print()
    
    results_comparison = {}
    
    # 1. DotsOCRでテスト
    print("1. DotsOCRで処理中...")
    try:
        dots_processor = DotsOCRPDFProcessor()
        start_time = time.time()
        dots_result = dots_processor.process_pdf(pdf_path, use_cli=True)
        dots_time = time.time() - start_time
        
        results_comparison['DotsOCR'] = {
            'time': dots_time,
            'text_length': len(dots_result['full_text']),
            'pages': dots_result['total_pages'],
            'layout_elements': len(dots_result.get('layout_elements', [])),
            'success': True
        }
        print(f"   完了: {dots_time:.2f}秒, {len(dots_result['full_text'])}文字")
        
    except Exception as e:
        print(f"   エラー: {e}")
        results_comparison['DotsOCR'] = {'success': False, 'error': str(e)}
    
    # 2. Google Cloud Vision APIでテスト
    print("\n2. Google Cloud Vision APIで処理中...")
    try:
        # 環境変数を設定
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/yoshiikatsuhiko/.config/gcloud/application_default_credentials.json'
        
        gcv_processor = PDFOCRProcessor()
        start_time = time.time()
        gcv_result = gcv_processor.process_pdf(pdf_path)
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
            if 'layout_elements' in result:
                print(f"  - レイアウト要素: {result['layout_elements']}")
        else:
            print(f"  - エラー: {result['error']}")
    
    # 速度比較
    if all(r['success'] for r in results_comparison.values()):
        dots_time = results_comparison['DotsOCR']['time']
        gcv_time = results_comparison['Google Cloud Vision']['time']
        
        print("\n" + "-" * 70)
        if dots_time < gcv_time:
            speedup = gcv_time / dots_time
            print(f"DotsOCRの方が {speedup:.1f}倍 高速")
        else:
            speedup = dots_time / gcv_time
            print(f"Google Cloud Visionの方が {speedup:.1f}倍 高速")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DotsOCR テストスクリプト')
    parser.add_argument('--compare', action='store_true',
                       help='DotsOCRとGoogle Cloud Vision APIを比較')
    parser.add_argument('--pdf', type=str,
                       help='テストに使用するPDFファイルのパス')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_ocr_methods()
    else:
        test_dots_ocr_pdf()
        
    print("\nテスト完了")
    print("=" * 70)