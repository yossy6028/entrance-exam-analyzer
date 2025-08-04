#!/bin/bash

# Entrance Exam Analyzer - Quick Start
# Double-click to run

cd "$(dirname "$0")"
clear

echo "┌─────────────────────────────────────┐"
echo "│    入試問題分析システム v1.0        │"
echo "│    Entrance Exam Analyzer           │"
echo "└─────────────────────────────────────┘"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3が見つかりません"
    echo "   brew install python3 でインストールしてください"
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Run application
python3 run_app.py

# Keep window open if error occurs
if [ $? -ne 0 ]; then
    echo ""
    echo "Press Enter to close..."
    read
fi