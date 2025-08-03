"""
設定ファイル
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).parent

# データディレクトリ
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# ディレクトリの作成
for dir_path in [INPUT_DIR, OUTPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Google Cloud Vision API設定
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# 処理設定
MAX_PAGES_PER_PDF = 20  # PDFの最大ページ数
IMAGE_DPI = 300  # PDF to Image変換時のDPI
BATCH_SIZE = 10  # バッチ処理時のサイズ

# 分析設定
QUESTION_PATTERNS = {
    '記号選択': [
        r'[ア-ン]\s*から選び',
        r'[A-H]\s*から選び',
        r'次の[ア-ン]〜[ア-ン]から',
        r'選択肢から選び'
    ],
    '抜き出し': [
        r'抜き出し[てなさい]',
        r'書き抜き[てなさい]',
        r'そのまま抜き出し'
    ],
    '記述': [
        r'\d+字以内で',
        r'\d+字程度で',
        r'\d+字〜\d+字で',
        r'説明しなさい',
        r'述べなさい',
        r'書きなさい',
        r'答えなさい',
        r'まとめなさい',
        r'どのような',
        r'なぜ.*か',
        r'理由を',
        r'〜について'
    ],
    '脱文挿入': [
        r'空欄に入る',
        r'（\s*）に入る',
        r'［\s*］に入る'
    ],
    '漢字・語句': [
        r'漢字で書き',
        r'読みを答え',
        r'意味を答え',
        r'同じ意味の'
    ]
}

# 出典情報パターン
SOURCE_PATTERNS = [
    r'（([^）]+)『([^』]+)』',
    r'出典[:：]\s*([^『]+)『([^』]+)』',
    r'([^「]+)「([^」]+)」より',
    r'※\s*([^『]+)『([^』]+)』'
]

# Excel出力設定
EXCEL_SHEET_NAMES = {
    'summary': 'サマリー',
    'detail': '詳細分析',
    'source': '出典一覧'
}