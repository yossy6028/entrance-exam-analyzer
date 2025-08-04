#!/bin/bash

# 入試問題分析アプリケーション起動スクリプト
# ダブルクリックで実行可能

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Pythonバージョン確認
echo "入試問題分析システムを起動しています..."
echo "================================="

# Python3が利用可能か確認
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python3がインストールされていません"
    echo "Homebrewでインストールしてください: brew install python3"
    exit 1
fi

# 必要なライブラリの確認
echo "必要なライブラリを確認中..."
python3 -c "import pandas" 2>/dev/null || {
    echo "pandasをインストールしています..."
    pip3 install pandas
}

python3 -c "import openpyxl" 2>/dev/null || {
    echo "openpyxlをインストールしています..."
    pip3 install openpyxl
}

python3 -c "from PIL import Image" 2>/dev/null || {
    echo "Pillowをインストールしています..."
    pip3 install Pillow
}

# アプリケーションを起動
echo "アプリケーションを起動中..."
python3 run_app.py

# エラーが発生した場合は、ウィンドウを閉じる前に確認できるようにする
if [ $? -ne 0 ]; then
    echo ""
    echo "エラーが発生しました。"
    echo "Enterキーを押してウィンドウを閉じてください..."
    read
fi