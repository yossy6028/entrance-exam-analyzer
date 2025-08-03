#!/bin/bash
# セットアップと実行スクリプト

echo "国語入試問題分析システムのセットアップを開始します..."

# 仮想環境の作成（まだない場合）
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境の有効化
echo "仮想環境を有効化中..."
source venv/bin/activate

# 依存パッケージのインストール
echo "依存パッケージをインストール中..."
pip install -r requirements.txt

# Google Cloud認証情報の確認
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "警告: GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません"
    echo "以下のコマンドで設定してください："
    echo "export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/service-account-key.json'"
    exit 1
fi

# サンプル実行
echo ""
echo "セットアップが完了しました！"
echo ""
echo "使用例："
echo "1. 単一ファイルの分析："
echo "   python main.py /path/to/exam.pdf --school '麻布中学校' --year '2025'"
echo ""
echo "2. 解答用紙も含めた分析："
echo "   python main.py /path/to/exam.pdf --answer /path/to/answer.pdf"
echo ""
echo "3. バッチ処理："
echo "   python main.py /path/to/pdf_directory --batch"