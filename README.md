# 国語入試問題分析システム

中学入試の国語問題（縦書きPDF）から出題傾向と出典情報を自動的に抽出・分析するシステムです。

## 機能

- **出題傾向分析**: 大問数、設問数、設問タイプの分類
- **出典情報抽出**: 著者名、作品タイトルの自動抽出
- **解答用紙分析**: 配点、解答形式の分析（オプション）
- **Excel出力**: 分析結果を見やすくExcel形式で出力
- **バッチ処理**: 複数ファイルの一括処理

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Vision APIの設定

1. Google Cloud Consoleでプロジェクトを作成
2. Vision APIを有効化
3. サービスアカウントキーを作成してダウンロード
4. 環境変数を設定:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

または `.env` ファイルを作成:

```bash
cp .env.example .env
# .envファイルを編集して認証情報のパスを設定
```

## 使い方

### 単一ファイルの分析

```bash
python main.py /path/to/exam.pdf --school "麻布中学校" --year "2025"
```

### 解答用紙も含めた分析

```bash
python main.py /path/to/exam.pdf --answer /path/to/answer.pdf
```

### バッチ処理

```bash
python main.py /path/to/pdf_directory --batch
```

## コマンドラインオプション

- `input_path`: 分析対象のPDFファイルまたはディレクトリ（必須）
- `--answer`: 解答用紙のPDFファイル
- `--school`: 学校名
- `--year`: 年度
- `--credentials`: Google Cloud認証情報のパス
- `--batch`: バッチ処理モード

## 出力

分析結果は以下の形式でExcelファイルに出力されます：

- **サマリーシート**: 基本情報、設問タイプ別集計
- **詳細分析シート**: 各設問の詳細情報
- **出典一覧シート**: 各大問の出典情報

## ディレクトリ構成

```
entrance_exam_analyzer/
├── main.py                 # メインプログラム
├── config.py              # 設定ファイル
├── requirements.txt       # 依存パッケージ
├── modules/              # 各種モジュール
├── data/
│   ├── input/           # 入力PDFフォルダ
│   └── output/          # 出力フォルダ
└── logs/                # ログフォルダ
```

## 注意事項

- Google Cloud Vision APIは月1000枚まで無料、それ以降は有料
- OCR精度は100%ではないため、重要な情報は手動確認を推奨
- 極端に画質が悪いPDFは処理できない場合があります