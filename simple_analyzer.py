#!/usr/bin/env python3
"""
入試問題テキスト分析システム - シンプル版
ドラッグ&ドロップまたはファイル選択で分析実行
"""
import sys
import os
from pathlib import Path
from typing import Optional

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.application import EntranceExamAnalyzer
from utils.display_utils import print_header, print_success, print_error, print_warning, clear_screen
from utils.text_utils import clean_path_string


def main():
    """メイン処理"""
    try:
        # アプリケーションを初期化
        app = EntranceExamAnalyzer()
        
        # コマンドライン引数をチェック
        file_path = None
        if len(sys.argv) > 1:
            # ドラッグ&ドロップされたファイル
            raw_path = ' '.join(sys.argv[1:])  # スペースを含むパスに対応
            file_path = clean_path_string(raw_path)
            
            # パスの存在確認
            if not Path(file_path).exists():
                print_error(f"ファイルが見つかりません: {file_path}")
                return 1
        
        # アプリケーションを実行
        success = app.run(file_path)
        
        if success:
            print_success("\n✅ 分析が完了しました！")
            print("結果は entrance_exam_database.xlsx に保存されました。")
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print_warning("\n\n中断されました。")
        return 130
    except Exception as e:
        print_error(f"\nエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())