#!/usr/bin/env python3
"""
2025年桜蔭中学校のデータをExcelに保存（修正版）
"""

import sys
from pathlib import Path
from datetime import datetime

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.flexible_excel_formatter import FlexibleExcelFormatter


def main():
    """分析結果をExcelに保存"""
    
    print("桜蔭2025年の分析結果を準備中...")
    
    # 手動で修正したデータ
    analysis_result = {
        'total_characters': 8303,
        'total_questions': 11,
        'sections': [
            {
                'number': 1,
                'source': None,  # ゴミ箱ロボットの話（出典不明）
                'characters': 4000,  # 推定
                'genre': '説明文',
                'theme': '科学・技術',
                'questions': [
                    {'number': '一', 'type': '漢字・語句'},
                    {'number': '二', 'type': '選択'},
                    {'number': '三', 'type': '記述'},
                    {'number': '四', 'type': '記述'},
                    {'number': '五', 'type': '記述'},
                    {'number': '六', 'type': '記述'}
                ]
            },
            {
                'number': 2,
                'source': {
                    'author': '植松三十里',
                    'work': 'イザベラ・バードと侍ボーイ'
                },
                'characters': 4303,  # 推定
                'genre': '小説・物語',
                'theme': '人間関係・成長',
                'questions': [
                    {'number': '一', 'type': '漢字・語句'},
                    {'number': '二', 'type': '漢字・語句'},
                    {'number': '三', 'type': '記述'},
                    {'number': '四', 'type': '記述'},
                    {'number': '五', 'type': '記述'}
                ]
            }
        ],
        'question_types': {
            '記述': 7,
            '選択': 1,
            '漢字・語句': 3
        }
    }
    
    # Excelフォーマッターを初期化
    formatter = FlexibleExcelFormatter(
        excel_path="entrance_exam_database.xlsx"
    )
    
    # 追加情報
    additional_info = {
        '記述_最大字数': None,
        '記述_最小字数': None,
        '図表_使用有無': 'なし',
        '詩歌_有無': 'なし',
        '出題傾向': 'ロボット工学の説明文と歴史小説の2題構成',
        '特記事項': '2025年度桜蔭中学校入試問題'
    }
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="桜蔭中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25桜蔭.txt",
        additional_info=additional_info
    )
    
    # データを保存
    print("\nExcelデータベースに保存中...")
    success = formatter.save_to_excel(
        school_name="桜蔭中学校",
        row_data=row_data,
        backup=True
    )
    
    if success:
        print("\n保存が完了しました！")
        print("\n【分析結果サマリー】")
        print(f"年度: 2025")
        print(f"総文字数: 8,303文字")
        print(f"大問数: 2問")
        print(f"総設問数: 11問")
        print("\n【大問1】")
        print(f"  ジャンル: 説明文")
        print(f"  テーマ: 科学・技術（ゴミ箱ロボット）")
        print(f"  設問数: 6問")
        print("\n【大問2】")
        print(f"  著者: 植松三十里")
        print(f"  作品: イザベラ・バードと侍ボーイ")
        print(f"  ジャンル: 小説・物語")
        print(f"  テーマ: 人間関係・成長")
        print(f"  設問数: 5問")
        
        # サマリーを表示
        summary = formatter.get_school_summary("桜蔭中学校")
        print("\n" + summary)
    else:
        print("\n保存に失敗しました。")


if __name__ == "__main__":
    main()