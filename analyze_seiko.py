#!/usr/bin/env python3
"""
聖光学院の国語問題をYomitokuでOCR解析
"""
from pathlib import Path
from modules.yomitoku_processor import YomitokuProcessor

def analyze_seiko_pdf():
    # PDFファイルのパス
    pdf_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).pdf")
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        return
    
    print("=" * 70)
    print(f"聖光学院 国語問題 OCR解析")
    print("=" * 70)
    print(f"ファイル: {pdf_path.name}")
    print(f"サイズ: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    # Yomitokuプロセッサーを初期化
    print("Yomitokuを初期化中...")
    processor = YomitokuProcessor(
        use_lite=True,  # 軽量モデル（高速）
        device="cpu"
    )
    
    # PDFを処理
    print("OCR処理を開始します...")
    print("（しばらくお待ちください...）")
    print()
    
    try:
        result = processor.process_pdf(
            pdf_path,
            output_format="md",
            output_dir=Path("seiko_output"),
            extract_figures=True,
            visualize=False
        )
        
        # 結果を表示
        print("=" * 70)
        print("OCR解析結果")
        print("=" * 70)
        print(f"総ページ数: {result['total_pages']}")
        print(f"抽出文字数: {len(result['full_text'])}")
        print()
        
        # 入試問題構造
        if 'exam_structure' in result:
            structure = result['exam_structure']
            print("【検出された問題構造】")
            print(f"大問: {', '.join(structure.get('sections', [])[:10])}")
            print(f"問題数: {structure.get('question_count', 0)}")
            print(f"選択肢: {'あり' if structure.get('has_answer_choices') else 'なし'}")
            if structure.get('source_info'):
                print("出典情報:")
                for k, v in structure['source_info'].items():
                    print(f"  {k}: {v}")
            print()
        
        # テキストを保存
        output_file = Path("seiko_output") / "seiko_kokugo_text.txt"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        
        print(f"テキストファイル保存: {output_file}")
        
        # 全文を返す
        return result['full_text']
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    text = analyze_seiko_pdf()
    
    if text:
        print("\n" + "=" * 70)
        print("抽出されたテキスト（全文）")
        print("=" * 70)
        print(text)