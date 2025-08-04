#!/usr/bin/env python3
"""
入試問題分析アプリケーション ランチャー
"""

import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPYTHONPATHに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# tkinterが利用可能かチェック
try:
    import tkinter
    # GUIバージョンを起動
    from entrance_exam_app import main
except ImportError:
    print("⚠️  GUIライブラリ（tkinter）が利用できません")
    print("   CLIバージョンを起動します...")
    print()
    # CLIバージョンを起動
    from entrance_exam_app_cli import main

if __name__ == "__main__":
    main()