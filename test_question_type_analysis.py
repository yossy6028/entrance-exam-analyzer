#!/usr/bin/env python3
"""
文章ごとの設問タイプ別集計テスト
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.excel_manager import ExcelManager
from models import AnalysisResult, Section, ExamSource, Question
import pandas as pd

def test_question_type_analysis():
    """文章ごとの設問タイプ別集計のテスト"""
    
    # ExcelManagerを初期化
    manager = ExcelManager()
    manager.db_path = Path("test_output/test_question_types.xlsx")
    
    # 設問データ（文章1: 選択2問、記述1問、抜き出し1問）
    questions_text1 = [
        Question(number=1, text="問1", type="選択式", section=1),
        Question(number=2, text="問2", type="選択", section=1),
        Question(number=3, text="問3", type="記述式", section=1),
        Question(number=4, text="問4", type="抜き出し", section=1),
    ]
    
    # 設問データ（文章2: 選択1問、記述2問、その他1問）
    questions_text2 = [
        Question(number=5, text="問5", type="記号選択", section=2),
        Question(number=6, text="問6", type="記述", section=2),
        Question(number=7, text="問7", type="記述式", section=2),
        Question(number=8, text="問8", type="空欄補充", section=2),  # その他
    ]
    
    # 設問データ（文章3: 抜き出し2問、選択1問）
    questions_text3 = [
        Question(number=9, text="問9", type="抜き出し", section=3),
        Question(number=10, text="問10", type="抜出", section=3),
        Question(number=11, text="問11", type="選択", section=3),
    ]
    
    # セクションデータを作成
    sections = [
        Section(
            number=1,
            text="文章1のテキスト..." * 200,
            questions=questions_text1,
            section_type="小説・物語",
            is_text_problem=True,
            char_count=2000
        ),
        Section(
            number=2,
            text="文章2のテキスト..." * 150,
            questions=questions_text2,
            section_type="論説文",
            is_text_problem=True,
            char_count=1500
        ),
        Section(
            number=3,
            text="文章3のテキスト..." * 180,
            questions=questions_text3,
            section_type="随筆",
            is_text_problem=True,
            char_count=1800
        ),
    ]
    
    # 分析結果を作成
    result = AnalysisResult(
        school_name="テスト中学校",
        year="2025",
        total_characters=5300,
        sections=sections,
        questions=questions_text1 + questions_text2 + questions_text3,
        sources=[
            ExamSource(author="夏目漱石", title="坊っちゃん"),
            ExamSource(author="池上彰", title="現代を読む"),
            ExamSource(author="寺田寅彦", title="柿の種"),
        ],
        question_types={
            '選択': 4,
            '記述': 3,
            '抜き出し': 3,
            'その他': 1
        },
        genre="小説・物語",
        theme="人間観察"
    )
    
    # 保存を実行
    print("📝 設問タイプ別集計テストデータを保存中...")
    success = manager.save_analysis_result(result)
    
    if success:
        print("✅ 保存成功")
        
        # 保存されたファイルを読み込んで確認
        df = pd.read_excel(manager.db_path, sheet_name='テスト中学校')
        print("\n📊 保存されたデータの確認:")
        
        # 文章ごとの設問タイプ別集計を確認
        print("\n【文章1の設問タイプ別集計】")
        print(f"  出題形式: {df['文章1_出題形式'].iloc[0] if '文章1_出題形式' in df.columns else 'N/A'}")
        print(f"  選択問題数: {df['文章1_選択問題数'].iloc[0] if '文章1_選択問題数' in df.columns else 'N/A'}")
        print(f"  記述問題数: {df['文章1_記述問題数'].iloc[0] if '文章1_記述問題数' in df.columns else 'N/A'}")
        print(f"  抜き出し問題数: {df['文章1_抜き出し問題数'].iloc[0] if '文章1_抜き出し問題数' in df.columns else 'N/A'}")
        print(f"  その他問題数: {df['文章1_その他問題数'].iloc[0] if '文章1_その他問題数' in df.columns else 'N/A'}")
        
        print("\n【文章2の設問タイプ別集計】")
        print(f"  出題形式: {df['文章2_出題形式'].iloc[0] if '文章2_出題形式' in df.columns else 'N/A'}")
        print(f"  選択問題数: {df['文章2_選択問題数'].iloc[0] if '文章2_選択問題数' in df.columns else 'N/A'}")
        print(f"  記述問題数: {df['文章2_記述問題数'].iloc[0] if '文章2_記述問題数' in df.columns else 'N/A'}")
        print(f"  抜き出し問題数: {df['文章2_抜き出し問題数'].iloc[0] if '文章2_抜き出し問題数' in df.columns else 'N/A'}")
        print(f"  その他問題数: {df['文章2_その他問題数'].iloc[0] if '文章2_その他問題数' in df.columns else 'N/A'}")
        
        print("\n【文章3の設問タイプ別集計】")
        print(f"  出題形式: {df['文章3_出題形式'].iloc[0] if '文章3_出題形式' in df.columns else 'N/A'}")
        print(f"  選択問題数: {df['文章3_選択問題数'].iloc[0] if '文章3_選択問題数' in df.columns else 'N/A'}")
        print(f"  記述問題数: {df['文章3_記述問題数'].iloc[0] if '文章3_記述問題数' in df.columns else 'N/A'}")
        print(f"  抜き出し問題数: {df['文章3_抜き出し問題数'].iloc[0] if '文章3_抜き出し問題数' in df.columns else 'N/A'}")
        print(f"  その他問題数: {df['文章3_その他問題数'].iloc[0] if '文章3_その他問題数' in df.columns else 'N/A'}")
        
        # 期待値との比較
        print("\n📈 期待値との比較:")
        print("文章1: 選択2問、記述1問、抜き出し1問、その他0問")
        print("文章2: 選択1問、記述2問、抜き出し0問、その他1問")
        print("文章3: 選択1問、記述0問、抜き出し2問、その他0問")
        
    else:
        print("❌ 保存失敗")
    
    return success

if __name__ == "__main__":
    # 出力ディレクトリを作成
    Path("test_output").mkdir(exist_ok=True)
    
    # テスト実行
    test_question_type_analysis()