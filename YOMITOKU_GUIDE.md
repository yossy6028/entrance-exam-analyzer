# Yomitoku OCR 導入ガイド

## 🎌 Yomitokuとは

Yomitokuは、**日本語文書に特化した高精度OCRツール**です。入試問題のような複雑なレイアウトの日本語文書を正確に読み取ることができます。

## ✨ 主な特徴

### DotsOCRとの比較

| 項目 | Yomitoku | DotsOCR | Google Cloud Vision |
|------|----------|---------|-------------------|
| **GPU要件** | 不要（CPU対応） | 必須（Flash Attention） | 不要（クラウド） |
| **日本語対応** | ◎（7,000字以上） | ○ | ○ |
| **縦書き対応** | ◎ | ○ | △ |
| **手書き文字** | ◎ | △ | △ |
| **表認識** | ◎（構造化） | ○ | △ |
| **処理速度** | 中速（CPU） | 高速（GPU） | 中速 |
| **コスト** | 無料 | 無料 | 従量課金 |
| **オフライン** | ◎ | ◎ | × |
| **インストール** | 簡単（pip） | 複雑 | 簡単 |

### 特筆すべき機能

1. **日本語特化**
   - 7,000以上の日本語文字を認識
   - ひらがな、カタカナ、漢字、記号を正確に識別
   - 縦書き・横書き混在文書に対応

2. **4つのAIモデル**
   - テキスト検出（TextDetector）
   - テキスト認識（TextRecognizer）
   - レイアウト解析（LayoutParser）
   - 表構造認識（TableStructureRecognizer）

3. **多様な出力形式**
   - Markdown（推奨）
   - JSON（構造化データ）
   - HTML（Webブラウザ表示）
   - CSV（表データ）
   - 検索可能PDF

## 📦 インストール

### 基本インストール（完了済み）
```bash
pip install yomitoku
```

### 必要なパッケージ
- Python 3.10-3.12
- PyTorch 2.5+
- OpenCV
- ONNX Runtime

## 🚀 使用方法

### 1. コマンドライン使用

```bash
# 基本的な使用（Markdown出力）
yomitoku input.pdf -f md -o output_dir

# 軽量モデル使用（高速）
yomitoku input.pdf -f md -o output_dir --lite

# 可視化付き
yomitoku input.pdf -f md -o output_dir -v

# 図表も抽出
yomitoku input.pdf -f md -o output_dir --figure
```

### 2. Pythonコードから使用

```python
from modules.yomitoku_processor import YomitokuProcessor

# プロセッサーを初期化
processor = YomitokuProcessor(
    use_lite=True,  # 軽量モデル（高速）
    device="cpu"    # CPUを使用
)

# PDFを処理
result = processor.process_pdf(
    pdf_path,
    output_format="md",  # 出力形式
    extract_figures=True  # 図表も抽出
)

# 結果を取得
print(f"抽出文字数: {len(result['full_text'])}")
print(f"検出された大問: {result['exam_structure']['sections']}")
```

### 3. 既存システムとの統合

```python
# フォールバック付き処理
result = processor.process_with_fallback(pdf_path)
# Yomitokuで処理し、失敗時はGoogle Cloud Visionに自動切り替え
```

## 🎯 入試問題処理に最適

### 認識可能な要素

✅ **文書構造**
- 大問番号（一、二、三...）
- 小問番号（問1、問2...）
- 選択肢（ア、イ、ウ...）

✅ **テキスト種別**
- 本文（縦書き・横書き）
- ルビ（ふりがな）
- 傍点・傍線

✅ **特殊要素**
- 表・グラフ
- 図形・イラスト
- 数式（基本的なもの）

## ⚡ パフォーマンス

### 処理速度（CPU環境）

| ページ数 | 処理時間 | メモリ使用量 |
|---------|---------|------------|
| 1ページ | 約10秒 | 1GB |
| 10ページ | 約100秒 | 2GB |
| 50ページ | 約8分 | 3GB |

### 推奨設定

```python
# 速度重視
processor = YomitokuProcessor(use_lite=True, device="cpu")

# 精度重視
processor = YomitokuProcessor(use_lite=False, device="cpu")

# GPU利用時（高速）
processor = YomitokuProcessor(use_lite=False, device="cuda")
```

## 📊 実際の処理例

### 入力: 入試問題PDF
```
第一問　次の文章を読んで、後の問いに答えなさい。

　春の朝、私は縁側に座って庭を眺めていた。
桜の花びらが風に舞い、...

問一　傍線部①について、筆者の心情を...
```

### 出力: 構造化データ
```json
{
  "exam_structure": {
    "sections": ["第一問", "第二問"],
    "question_count": 15,
    "has_answer_choices": true,
    "themes": ["人間関係・成長", "自然・環境"]
  },
  "pages": [
    {
      "text": "第一問　次の文章を読んで...",
      "tables": [],
      "figures": []
    }
  ]
}
```

## 🔧 トラブルシューティング

### メモリ不足エラー
```bash
# 軽量モデルを使用
yomitoku input.pdf --lite

# バッチサイズを減らす
export YOMITOKU_BATCH_SIZE=1
```

### 文字化け
```python
# エンコーディング指定
processor.process_pdf(pdf_path, encoding="utf-8")
```

### 処理が遅い
```python
# 並列処理を有効化
processor = YomitokuProcessor(use_lite=True, num_threads=4)
```

## 🎉 まとめ

### Yomitokuの利点

1. **即座に使用可能**
   - GPU不要、CPU環境で動作
   - pipで簡単インストール
   - 複雑な設定不要

2. **日本語に最適化**
   - 入試問題の複雑なレイアウトに対応
   - 縦書き・手書きも高精度認識
   - 表構造を正確に抽出

3. **実用的な性能**
   - CPUでも実用的な速度
   - 高い認識精度
   - 多様な出力形式

### 推奨使用シーン

✅ **最適**
- 日本語の入試問題
- 縦書き文書
- 表を含む文書
- オフライン環境

⚠️ **要検討**
- 大量のPDF処理（速度面）
- 複雑な数式（LaTeX形式不可）
- カラー画像の文字認識

## 📝 次のステップ

1. **テスト実行**
   ```bash
   python test_yomitoku.py
   ```

2. **バッチ処理スクリプト作成**
   ```python
   # 複数PDFを一括処理
   for pdf in pdf_list:
       result = processor.process_pdf(pdf)
   ```

3. **Excel出力との統合**
   ```python
   # 既存のExcel管理システムと連携
   from modules.excel_manager import ExcelManager
   ```

Yomitokuは、DotsOCRのようなGPU要件なしに、日本語文書を高精度でOCR処理できる優れたツールです。入試問題分析システムに最適な選択肢と言えるでしょう。