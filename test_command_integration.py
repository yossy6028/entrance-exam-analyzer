#!/usr/bin/env python3
"""
コマンドファイル統合テスト
main.py経由でExcelManagerが新しい形式で動作するか確認
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.excel_manager import ExcelManager
from models import AnalysisResult, Section, ExamSource, Question
import pandas as pd

def test_excel_manager():
    """ExcelManagerが新しい形式で動作するかテスト"""
    
    # ExcelManagerを初期化
    manager = ExcelManager()
    manager.db_path = Path("test_output/test_command_integration.xlsx")
    
    # 設問データを作成
    questions = [
        Question(number=1, text="問1", type="記述", section=1),
        Question(number=2, text="問2", type="選択", section=1),
        Question(number=3, text="問3", type="抜き出し", section=1),
        Question(number=4, text="問1", type="記述", section=2),
        Question(number=5, text="問2", type="選択", section=2),
        Question(number=6, text="問1", type="漢字", section=3),
        Question(number=7, text="問2", type="漢字", section=3),
        Question(number=8, text="問3", type="語句", section=3),
    ]
    
    # テスト用の分析結果を作成
    result = AnalysisResult(
        school_name="テスト中学校",
        year="2025",
        total_characters=5000,
        questions=questions,
        genre="小説・物語",  # 最初のセクションのジャンル
        theme="友情と成長",
        sections=[
            Section(
                number=1,
                text="これは小説のテキストです..." * 100,
                questions=questions[0:3],
                section_type="小説・物語",
                is_text_problem=True,
                char_count=1500
            ),
            Section(
                number=2,
                text="これは論説文のテキストです..." * 80,
                questions=questions[3:5],
                section_type="論説文",
                is_text_problem=True,
                char_count=1200
            ),
            Section(
                number=3,
                text="",
                questions=questions[5:8],
                section_type="漢字・語句",
                is_text_problem=False,
                char_count=0
            )
        ],
        sources=[
            ExamSource(author="夏目漱石", title="こころ"),
            ExamSource(author="山田太郎", title="地球の未来"),
            None
        ],
        question_types={
            '記述': 2,
            '選択': 2,
            '抜き出し': 1,
            '漢字': 2,
            '語句': 1
        }
    )
    
    # 保存を実行
    print("📝 ExcelManagerでデータを保存中...")
    success = manager.save_analysis_result(result)
    
    if success:
        print("✅ 保存成功")
        
        # 保存されたファイルを読み込んで確認
        df = pd.read_excel(manager.db_path, sheet_name='テスト中学校')
        print("\n📊 保存されたデータの確認:")
        print(f"  インデックス付き: {df.index.tolist()}")
        
        # 新しい形式の列を確認
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
        
        print("\n📋 列の内容:")
        for col in important_cols:
            if col in df.columns:
                print(f"  ✓ {col}: {df[col].iloc[0]}")
            else:
                print(f"  ✗ {col}: 列が存在しません")
                
        # データフレーム全体を表示
        print("\n📄 データフレーム全体:")
        print(df.to_string())
        
    else:
        print("❌ 保存失敗")
        
    return success

if __name__ == "__main__":
    # 出力ディレクトリを作成
    Path("test_output").mkdir(exist_ok=True)
    
    # テスト実行
    test_excel_manager()