# 頻用コマンドパターン

## デバッグ・分析コマンド

### OCRテキストの構造確認
```bash
# 大問番号を探す
grep -n "^[一二三四五六七八九十]、" [OCRファイル]

# 設問を探す
grep -n "問[一二三四五六七八九十]" [OCRファイル]

# 出典を探す
grep -n "による$" [OCRファイル]
```

### Python分析スクリプト
```python
# セクション分割のデバッグ
python3 -c "
import json
with open('seiko_debug_result.json', 'r') as f:
    data = json.load(f)
for i, s in enumerate(data['sections']):
    print(f'セクション{i+1}: 設問{len(s[\"questions\"])}個')
    if s['questions']:
        print(f'  番号: {[q[\"number\"] for q in s[\"questions\"]]}')"
```

### Excel確認
```python
# 新形式Excelの内容確認
python3 check_new_excel.py

# 旧形式との比較
python3 check_main_excel_file.py
```

## 実行コマンド

### 基本的な分析実行
```bash
# アプリケーション起動（GUI）
python3 run_app.py

# バッチ分析
python3 batch_analyzer.py --school "聖光学院" --year 2025

# 特定PDFの分析
python3 analyze_single_pdf.py "/path/to/pdf"
```

### デバッグモード実行
```bash
# デバッグ出力付き
python3 analyze_with_debug.py --pdf [PDFファイル] --debug

# セクション修正版
python3 fix_section_division.py
```

## トラブルシューティング

### セクション分割がおかしい場合
```python
# 1. デバッグ結果を確認
cat seiko_debug_result.json | jq '.sections[] | {number, questions: .questions | length, genre}'

# 2. 設問番号の連続性を確認
python3 -c "
import json
with open('seiko_debug_result.json') as f:
    data = json.load(f)
for s in data['sections']:
    if s['questions']:
        nums = [q['number'] for q in s['questions']]
        print(f'設問番号: {nums}')"

# 3. 手動修正
python3 fix_section_division.py
```

### Excel出力の問題
```python
# Excelファイルの破損チェック
python3 -c "
import pandas as pd
try:
    pd.read_excel('path/to/excel.xlsx')
    print('✅ Excelファイル正常')
except Exception as e:
    print(f'❌ エラー: {e}')"
```

## 検証用コマンド

### 問題数カウントの検証
```python
# 実際の問題数をカウント
python3 -c "
from modules.final_content_extractor import FinalContentExtractor
extractor = FinalContentExtractor()
# OCRテキストを読み込み
with open('[OCRファイル]', 'r') as f:
    text = f.read()
result = extractor.extract_all_content(text)
print(f'総設問数: {result[\"total_questions\"]}')"
```

### 出典抽出の検証
```python
# 出典情報を確認
grep -A2 -B2 "『.*』" [OCRファイル] | head -20
```

## 便利なワンライナー

```bash
# PDFファイル一覧
find . -name "*.pdf" -type f | sort

# 最新の分析結果
ls -lt *.json | head -5

# Excelシート名一覧
python3 -c "import pandas as pd; print(pd.ExcelFile('[Excel]').sheet_names)"

# 文字数カウント
wc -m [OCRファイル]

# 設問タイプ別集計
python3 -c "
import json
with open('[分析結果.json]') as f:
    print(json.load(f)['question_types'])"
```

## Git関連

```bash
# 変更内容の確認
git diff modules/

# 特定ファイルの履歴
git log -p modules/final_content_extractor.py

# ブランチ作成
git checkout -b fix/section-division
```

## テスト実行

```bash
# 単体テスト
python3 -m pytest tests/

# 特定のテスト
python3 -m pytest tests/test_extractor.py::test_section_division

# カバレッジ付き
python3 -m pytest --cov=modules tests/
```