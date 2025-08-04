#!/usr/bin/env python3
"""
テキスト分析アプリケーションランチャー
GUIが使える場合はGUI版、そうでない場合はCLI版を起動
"""

import sys
from pathlib import Path

def main():
    """メイン関数"""
    try:
        # tkinterが利用可能かチェック
        import tkinter
        print("✅ GUI版を起動します...")
        from text_analyzer_app import main as gui_main
        gui_main()
    except ImportError:
        print("⚠️  tkinterが利用できません。CLI版を起動します...")
        from text_analyzer_app_cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()