#!/usr/bin/env python3
"""
一括分析のテスト実行
"""

import sys
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from batch_analyzer import BatchAnalyzer


def test_batch_analysis():
    """テスト実行"""
    
    # 分析対象のフォルダ（既知のファイルがある場所）
    test_folders = [
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成",
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭",
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋"
    ]
    
    # アナライザーを初期化
    analyzer = BatchAnalyzer("test_batch_results.xlsx")
    
    # 各フォルダを分析
    for folder in test_folders:
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"\n分析中: {folder}")
            results = analyzer.analyze_folder(folder, "25*.txt")  # 2025年のファイルのみ
            print(f"  → {len(results)}件のファイルを分析")
    
    # サマリーを表示
    analyzer.print_summary()
    
    # Excelに保存
    if analyzer.results:
        print("\nExcelファイルに保存中...")
        success = analyzer.save_to_excel()
        if success:
            print("✅ 保存完了: test_batch_results.xlsx")
        else:
            print("⚠️ 保存に失敗しました")
    else:
        print("\n分析結果がありません")


if __name__ == "__main__":
    test_batch_analysis()