#!/usr/bin/env python3
"""
DotsOCR簡単テストスクリプト
DotsOCRのparser.pyを直接使用してPDFを処理
"""
import sys
import os
import subprocess
from pathlib import Path
import json

def test_dots_ocr_cli():
    """DotsOCRのCLIを直接テスト"""
    
    # DotsOCRのパス
    dots_ocr_path = Path.home() / "dots.ocr"
    parser_script = dots_ocr_path / "dots_ocr" / "parser.py"
    
    if not parser_script.exists():
        print(f"エラー: parser.pyが見つかりません: {parser_script}")
        return
    
    # テスト用PDFファイルを探す
    test_pdfs = [
        Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf"),
        Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"),
    ]
    
    pdf_path = None
    for pdf in test_pdfs:
        if pdf.exists():
            pdf_path = pdf
            break
    
    if not pdf_path:
        print("テスト用PDFファイルが見つかりません")
        # デモファイルを使用
        demo_path = dots_ocr_path / "demo" / "demo_pdf1.pdf"
        if demo_path.exists():
            pdf_path = demo_path
            print(f"デモファイルを使用: {demo_path}")
        else:
            print("デモファイルも見つかりません")
            return
    
    print("=" * 70)
    print("DotsOCR CLIテスト")
    print("=" * 70)
    print(f"PDFファイル: {pdf_path.name}")
    print(f"Parser: {parser_script}")
    print()
    
    # 出力ディレクトリを作成
    output_dir = Path("dots_ocr_test_output")
    output_dir.mkdir(exist_ok=True)
    
    # DotsOCRを実行
    cmd = [
        sys.executable,
        str(parser_script),
        str(pdf_path),
        "--output_dir", str(output_dir),
        "--num_thread", "4"
    ]
    
    print("実行コマンド:")
    print(" ".join(cmd))
    print()
    print("処理中...")
    
    try:
        # 環境変数にDots.ocrのパスを追加
        env = os.environ.copy()
        env['PYTHONPATH'] = str(dots_ocr_path) + ":" + env.get('PYTHONPATH', '')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(dots_ocr_path)
        )
        
        if result.returncode == 0:
            print("✅ 処理成功!")
            print("\n出力:")
            print(result.stdout[:500])
            
            # 出力ファイルを確認
            output_files = list(output_dir.glob("*"))
            if output_files:
                print(f"\n生成されたファイル:")
                for file in output_files:
                    print(f"  - {file.name}")
                    
                # JSONファイルがあれば内容を確認
                json_files = list(output_dir.glob("*.json"))
                if json_files:
                    with open(json_files[0], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"\nJSONファイルの構造:")
                    print(f"  キー: {list(data.keys())}")
                    
                # Markdownファイルがあれば一部表示
                md_files = list(output_dir.glob("*.md"))
                if md_files:
                    with open(md_files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"\nMarkdown出力（最初の500文字）:")
                    print(content[:500])
        else:
            print("❌ 処理失敗")
            print(f"\nエラー出力:")
            print(result.stderr)
            
            # よくあるエラーの対処法を表示
            if "ModuleNotFoundError" in result.stderr:
                print("\n対処法: DotsOCRが正しくインストールされていません")
                print("以下を実行してください:")
                print(f"cd {dots_ocr_path}")
                print("pip install -e .")
            elif "model" in result.stderr.lower() or "weight" in result.stderr.lower():
                print("\n対処法: モデルファイルが見つかりません")
                print("以下を実行してモデルをダウンロードしてください:")
                print(f"cd {dots_ocr_path}")
                print("python3 tools/download_model.py")
                
    except Exception as e:
        print(f"実行エラー: {e}")
        import traceback
        traceback.print_exc()


def check_installation():
    """インストール状態を確認"""
    print("DotsOCRインストール確認")
    print("=" * 70)
    
    # DotsOCRディレクトリ
    dots_ocr_path = Path.home() / "dots.ocr"
    print(f"DotsOCRパス: {dots_ocr_path}")
    print(f"  存在: {'✅' if dots_ocr_path.exists() else '❌'}")
    
    if dots_ocr_path.exists():
        # 重要なファイルの確認
        important_files = [
            "dots_ocr/parser.py",
            "dots_ocr/__init__.py",
            "setup.py",
            "requirements.txt"
        ]
        
        for file in important_files:
            file_path = dots_ocr_path / file
            print(f"  {file}: {'✅' if file_path.exists() else '❌'}")
        
        # weightsディレクトリの確認
        weights_dir = dots_ocr_path / "weights"
        if weights_dir.exists():
            print(f"\nモデルディレクトリ: ✅")
            model_files = list(weights_dir.glob("*"))
            if model_files:
                print("  モデルファイル:")
                for f in model_files[:5]:
                    print(f"    - {f.name}")
        else:
            print(f"\nモデルディレクトリ: ❌ (ダウンロードが必要)")
    
    # Pythonパッケージの確認
    print("\nPythonパッケージ:")
    required_packages = [
        "transformers",
        "torch",
        "qwen_vl_utils",
        "gradio",
        "PyMuPDF"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  {package}: ✅")
        except ImportError:
            print(f"  {package}: ❌")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DotsOCR簡単テスト')
    parser.add_argument('--check', action='store_true',
                       help='インストール状態のみ確認')
    parser.add_argument('--pdf', type=str,
                       help='テストするPDFファイルのパス')
    
    args = parser.parse_args()
    
    if args.check:
        check_installation()
    else:
        check_installation()
        print()
        test_dots_ocr_cli()
    
    print("\nテスト完了")