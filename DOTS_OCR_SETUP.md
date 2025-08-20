# DotsOCR セットアップガイド

## 概要

DotsOCRは、多言語ドキュメントレイアウト解析とOCR処理を単一のビジョン言語モデルで実現する最新のツールです。このガイドでは、entrance_exam_analyzerプロジェクトでDotsOCRを使用するためのセットアップ手順を説明します。

## DotsOCRの特徴

- **統合アーキテクチャ**: レイアウト検出とコンテンツ認識を単一モデルで処理
- **多言語対応**: 100以上の言語に対応（日本語、中国語、英語など）
- **高精度**: 1.7Bパラメータながら最先端の性能を実現
- **入試問題に最適**: 
  - 数式認識（LaTeX形式）
  - 表認識（HTML形式）
  - 縦書きテキスト対応
  - 複雑なレイアウト解析

## インストール手順

### 1. 環境準備

```bash
# Condaを使用（推奨）
conda create -n dots_ocr python=3.12
conda activate dots_ocr

# または、venvを使用
python3.12 -m venv dots_ocr_env
source dots_ocr_env/bin/activate  # macOS/Linux
# dots_ocr_env\Scripts\activate  # Windows
```

### 2. DotsOCRのクローン

```bash
# プロジェクトディレクトリに移動
cd /Users/yoshiikatsuhiko/entrance_exam_analyzer

# DotsOCRをクローン
git clone https://github.com/rednote-hilab/dots.ocr.git
cd dots.ocr
```

### 3. PyTorchのインストール

CUDAバージョンに応じて適切なPyTorchをインストール：

```bash
# CUDA 12.8の場合（GPUあり）
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128

# CUDA 11.8の場合
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu118

# CPU版（GPUなし）
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0
```

### 4. DotsOCRのインストール

```bash
# dots.ocrディレクトリ内で実行
pip install -e .
```

### 5. モデルのダウンロード

```bash
# モデルウェイトをダウンロード
python3 tools/download_model.py

# または、Hugging Faceから直接ダウンロード
# https://huggingface.co/rednote-hilab/dots.ocr
```

### 6. 追加の依存関係

```bash
# entrance_exam_analyzerディレクトリに戻る
cd ..

# 必要なパッケージをインストール
pip install pdf2image pillow
```

## 使用方法

### 基本的な使い方

```python
# DotsOCRを使ったPDF処理
from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor

# プロセッサーを初期化
processor = DotsOCRPDFProcessor(
    model_path="./weights/DotsOCR",  # モデルのパス
    use_gpu=True,                    # GPUを使用
    dpi=300                          # PDF変換時の解像度
)

# PDFを処理
pdf_path = Path("path/to/your.pdf")
result = processor.process_pdf(pdf_path)

# 結果を取得
print(f"抽出文字数: {len(result['full_text'])}")
print(f"検出された大問: {result['exam_structure']['sections']}")
```

### テストスクリプトの実行

```bash
# 基本テスト
python test_dots_ocr.py

# 特定のPDFでテスト
python test_dots_ocr.py --pdf /path/to/test.pdf

# Google Cloud Vision APIとの比較
python test_dots_ocr.py --compare
```

### コマンドラインインターフェース

```bash
# 単一画像の処理
python3 dots_ocr/parser.py demo/demo_image1.jpg

# PDFの処理（マルチスレッド）
python3 dots_ocr/parser.py demo/demo_pdf1.pdf --num_thread 64
```

## 既存システムとの統合

### 1. 自動フォールバック機能

DotsOCRが利用できない場合、自動的にGoogle Cloud Vision APIにフォールバック：

```python
# フォールバック付き処理
result = processor.process_with_fallback(pdf_path)
```

### 2. 互換性のあるデータ形式

既存のPDFOCRProcessorと同じインターフェースを提供：

```python
# 既存コード（Google Cloud Vision）
from modules.pdf_ocr_processor import PDFOCRProcessor
processor = PDFOCRProcessor()
result = processor.process_pdf(pdf_path)

# DotsOCRに置き換え（互換性あり）
from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor
processor = DotsOCRPDFProcessor()
result = processor.process_pdf(pdf_path)  # 同じインターフェース
```

## トラブルシューティング

### 1. ImportError: dots_ocr not found

```bash
# dots_ocrパッケージが見つからない場合
cd dots.ocr
pip install -e .
```

### 2. CUDA out of memory

```python
# GPUメモリ不足の場合、CPU版を使用
processor = DotsOCRPDFProcessor(use_gpu=False)
```

### 3. モデルファイルが見つからない

```bash
# モデルを再ダウンロード
cd dots.ocr
python3 tools/download_model.py
```

### 4. PDFの変換エラー

```bash
# poppler-utilsをインストール（macOS）
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

## パフォーマンス比較

| 項目 | DotsOCR | Google Cloud Vision |
|------|---------|-------------------|
| 処理速度 | 高速（ローカル処理） | 中速（API呼び出し） |
| 精度 | 高（特に日本語） | 高 |
| レイアウト解析 | 優秀 | 良好 |
| 数式認識 | LaTeX形式 | テキストのみ |
| 表認識 | HTML形式 | テキストのみ |
| コスト | 無料（ローカル） | 従量課金 |
| オフライン動作 | 可能 | 不可 |

## 注意事項

1. **GPU推奨**: DotsOCRは1.7Bパラメータのモデルのため、GPU使用を推奨
2. **メモリ要件**: 最低8GB RAM、推奨16GB以上
3. **ディスク容量**: モデルファイル用に約5GB必要
4. **初回実行**: 初回実行時はモデルのロードに時間がかかる場合があります

## 参考リンク

- [DotsOCR GitHub](https://github.com/rednote-hilab/dots.ocr)
- [DotsOCR Hugging Face](https://huggingface.co/rednote-hilab/dots.ocr)
- [DotsOCR 公式サイト](https://www.dotsocr.net)

## サポート

問題が発生した場合は、以下を確認してください：

1. Python バージョン（3.12推奨）
2. PyTorch のインストール状態
3. モデルファイルの存在
4. GPU/CUDAの設定（GPU使用時）

それでも解決しない場合は、Google Cloud Vision APIへの自動フォールバック機能により、処理は継続されます。