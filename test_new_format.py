#!/usr/bin/env python3
"""
新しい形式（文章1,2,3 その他1,2,3）でデータをフォーマットするテスト
"""

import json
from modules.content_type_formatter import ContentTypeFormatter

def test_new_format():
    """新形式でデータをフォーマット"""
    
    # 聖光学院のデバッグ結果を読み込み
    with open('seiko_debug_result.json', 'r', encoding='utf-8') as f:
        analysis_result = json.load(f)
    
    # 新しいフォーマッターを作成
    formatter = ContentTypeFormatter()
    
    # データをフォーマット
    formatted_data = formatter.format_data(
        analysis_result,
        school_name='聖光学院中学校',
        year=2025
    )
    
    # フォーマット済みデータを表示
    formatter.display_formatted_data(formatted_data)
    
    # Excelに保存
    formatter.save_to_excel(formatted_data, sheet_name='聖光学院中学校')
    
    print("\n✅ 新形式でのExcel保存が完了しました")
    print(f"ファイル: {formatter.excel_path}")

if __name__ == "__main__":
    test_new_format()