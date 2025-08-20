# DotsOCR 使用方法まとめ

## 現在の状況

✅ **完了した作業:**
- DotsOCRのクローン（`~/dots.ocr`に配置）
- 必要なパッケージのインストール（transformers, torch, torchvision等）
- モデルファイルのダウンロード（約5.7GB、`~/dots.ocr/weights/DotsOCR`に配置）
- テストスクリプトの作成

## DotsOCRの2つの実行モード

### 1. vLLMサーバーモード（高速・推奨）

vLLMサーバーを起動してから使用：

```bash
# サーバー起動（別ターミナルで実行）
cd ~/dots.ocr
python3 -m vllm.entrypoints.openai.api_server \
    --model ./weights/DotsOCR \
    --served-model-name DotsOCR \
    --trust-remote-code \
    --port 8000

# クライアントから使用
python3 dots_ocr/parser.py your_pdf.pdf --output ./output
```

### 2. Hugging Face直接実行モード（簡単だが遅い）

```bash
cd ~/dots.ocr
PYTHONPATH=. python3 dots_ocr/parser.py your_pdf.pdf \
    --output ./output \
    --use_hf True \
    --dpi 150 \
    --num_thread 2
```

## entrance_exam_analyzerでの使用方法

### 方法1: 作成済みモジュールを使用

```python
from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor

# プロセッサーを初期化
processor = DotsOCRPDFProcessor(
    model_path="/Users/yoshiikatsuhiko/dots.ocr/weights/DotsOCR",
    use_gpu=True
)

# PDFを処理（自動的にフォールバック機能付き）
result = processor.process_with_fallback(pdf_path)

# 結果を表示
print(f"抽出文字数: {len(result['full_text'])}")
print(f"レイアウト要素数: {len(result.get('layout_elements', []))}")
```

### 方法2: コマンドラインから直接実行

```bash
# 単一ファイル処理
cd ~/dots.ocr
PYTHONPATH=. python3 dots_ocr/parser.py \
    "/path/to/exam.pdf" \
    --output ./output \
    --use_hf True

# 出力ファイル：
# - output/exam.json（レイアウト情報）
# - output/exam.md（マークダウン形式のテキスト）
# - output/exam_vis.png（視覚化画像）
```

## トラブルシューティング

### エラー: Connection refused
**原因**: vLLMサーバーが起動していない
**解決策**: `--use_hf True`オプションを付けるか、vLLMサーバーを起動

### エラー: ModuleNotFoundError
**原因**: パッケージ不足
**解決策**: 
```bash
pip install torch torchvision transformers qwen-vl-utils openai gradio PyMuPDF
```

### エラー: CUDA out of memory
**原因**: GPUメモリ不足
**解決策**: CPUモードで実行するか、バッチサイズを減らす

## 既存システムとの統合

作成済みのモジュール（`modules/dots_ocr_pdf_processor.py`）は、既存の`PDFOCRProcessor`と互換性があるため、簡単に置き換え可能：

```python
# 既存コード
from modules.pdf_ocr_processor import PDFOCRProcessor
processor = PDFOCRProcessor()

# DotsOCRに置き換え
from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor
processor = DotsOCRPDFProcessor()  # インターフェースは同じ
```

## 主な特徴

- **レイアウト解析**: 表、数式、図表を個別に認識
- **多言語対応**: 日本語、英語、中国語など100以上の言語
- **出力形式**: 
  - 数式: LaTeX形式
  - 表: HTML形式
  - テキスト: Markdown形式
- **入試問題に最適**: 大問構造、設問番号、選択肢を自動認識

## 次のステップ

1. vLLMサーバーの自動起動スクリプト作成
2. バッチ処理用のスクリプト作成
3. Excel出力との統合
4. 処理速度の最適化