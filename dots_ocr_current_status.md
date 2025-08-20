# DotsOCR 現在の状況と対応策

## 現在の課題

DotsOCRは高性能なOCRツールですが、以下の課題があることが判明しました：

### 1. Flash Attentionの依存関係
- **問題**: モデルがflash_attnパッケージを必須としている
- **原因**: 高速化のためにFlash Attention 2を使用
- **影響**: CPUのみの環境では動作しない

### 2. 必要なリソース
- **GPU**: Flash AttentionはGPU（CUDA）が必要
- **メモリ**: 約6GB以上のGPUメモリが推奨
- **ディスク**: モデルファイルだけで約5.7GB

## 解決策

### オプション1: vLLMサーバーモード（推奨）

vLLMサーバーを起動して、APIとして使用：

```bash
# サーバー起動（別ターミナル）
cd ~/dots.ocr
python3 -m vllm.entrypoints.openai.api_server \
    --model ./weights/DotsOCR \
    --served-model-name DotsOCR \
    --trust-remote-code \
    --port 8000 \
    --max-model-len 8192

# クライアントから使用
python3 dots_ocr/parser.py your_pdf.pdf --output ./output
```

### オプション2: Google Cloud Vision APIを継続使用

既存のGoogle Cloud Vision APIベースのシステムを使用：

```python
from modules.pdf_ocr_processor import PDFOCRProcessor

processor = PDFOCRProcessor()
result = processor.process_pdf(pdf_path)
```

### オプション3: 他のOCRツールの検討

- **EasyOCR**: 軽量で日本語対応
- **Tesseract**: オープンソースの定番OCR
- **PaddleOCR**: 高精度な中国製OCR

## 推奨事項

### 現時点での最適解

1. **Google Cloud Vision APIを主要OCRとして継続使用**
   - 安定性が高い
   - CPUのみで動作
   - 既に実装済み

2. **DotsOCRは研究用として保持**
   - GPU環境が整ったら再検討
   - 特に複雑なレイアウトの文書で試験的に使用

3. **ハイブリッドアプローチ**
   ```python
   # 作成済みのフォールバック機能を活用
   from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor
   
   processor = DotsOCRPDFProcessor()
   # DotsOCRを試み、失敗したらGoogle Cloud Visionに自動切り替え
   result = processor.process_with_fallback(pdf_path)
   ```

## 実装済みのファイル

以下のファイルは既に作成済みで、GPU環境が整えば使用可能：

1. `modules/dots_ocr_handler.py` - DotsOCR基本処理
2. `modules/dots_ocr_pdf_processor.py` - 互換インターフェース
3. `test_dots_ocr.py` - テストスクリプト
4. `test_dots_ocr_simple.py` - 簡易テスト
5. `run_dots_ocr.py` - 実行スクリプト

## 今後の展望

### GPU環境が利用可能になったら

1. Flash Attentionのインストール
   ```bash
   pip install flash-attn --no-build-isolation
   ```

2. DotsOCRの本格運用
   - vLLMサーバーの常駐化
   - バッチ処理の最適化
   - 処理速度の比較評価

### 代替案の評価

1. **EasyOCRの導入テスト**
   ```bash
   pip install easyocr
   ```

2. **PaddleOCRの評価**
   ```bash
   pip install paddlepaddle paddleocr
   ```

## まとめ

DotsOCRは優れたOCRツールですが、現在のCPU環境では制限があります。当面は既存のGoogle Cloud Vision APIを使用し、将来的にGPU環境が整った際にDotsOCRへの移行を検討することを推奨します。

作成済みのコードは、環境が整えばすぐに使用可能な状態で保存されています。