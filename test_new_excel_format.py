#!/usr/bin/env python3
"""
新しいExcel形式のテスト
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.flexible_excel_formatter import FlexibleExcelFormatter
import pandas as pd

def test_new_format():
    """新しいExcel形式をテスト"""
    
    # フォーマッターを初期化
    formatter = FlexibleExcelFormatter(
        excel_path="test_output/test_new_format.xlsx",
        max_text_sections=3,
        max_other_sections=2
    )
    
    # テスト用の分析結果を作成
    test_result = {
        'total_characters': 5000,
        'total_questions': 15,
        'sections': [
            {
                'genre': '小説・物語',
                'theme': '友情と成長',
                'characters': 2500,
                'source': {
                    'author': '夏目漱石',
                    'work': 'こころ'
                },
                'questions': [
                    {'type': '記述'},
                    {'type': '選択'},
                    {'type': '抜き出し'},
                ]
            },
            {
                'genre': '論説文',
                'theme': '環境問題',
                'characters': 2000,
                'source': {
                    'author': '山田太郎',
                    'work': '地球の未来'
                },
                'questions': [
                    {'type': '記述'},
                    {'type': '選択'},
                ]
            },
            {
                'genre': '漢字・語句',
                'questions': [
                    {'type': '漢字'},
                    {'type': '漢字'},
                    {'type': '語句'},
                ]
            }
        ],
        'question_types': {
            '記述': 2,
            '選択': 2,
            '抜き出し': 1,
            '漢字': 2,
            '語句': 1
        }
    }
    
    # データを整形
    formatted_data = formatter.format_analysis_data(
        school_name='テスト中学校',
        year=2025,
        analysis_result=test_result
    )
    
    # Excelに保存
    success = formatter.save_to_excel(
        school_name='テスト中学校',
        row_data=formatted_data,
        backup=False
    )
    
    if success:
        print("✅ テスト成功")
        
        # 保存されたファイルを読み込んで確認
        df = pd.read_excel("test_output/test_new_format.xlsx", sheet_name='テスト中学校')
        print("\n📊 保存されたデータの確認:")
        
        # 主要な列を表示
        important_cols = [
            '年度',
            '文章1_出題形式',
            '文章1_出典',
            '文章1_文字数',
            '文章2_出題形式',
            '文章2_出典',
            'その他1_出題形式',
            'その他1_設問数'
        ]
        
        for col in important_cols:
            if col in df.columns:
                print(f"  {col}: {df[col].iloc[0]}")
    else:
        print("❌ テスト失敗")

if __name__ == "__main__":
    # 出力ディレクトリを作成
    Path("test_output").mkdir(exist_ok=True)
    
    test_new_format()