#!/usr/bin/env python3
"""
文章問題とその他問題の分類テスト
聖光学院のような実際のケースをシミュレート
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.excel_manager import ExcelManager
from models import AnalysisResult, Section, ExamSource, Question
import pandas as pd

def test_seiko_pattern():
    """聖光学院パターンのテスト（文章2つ、その他1つ）"""
    
    # ExcelManagerを初期化
    manager = ExcelManager()
    manager.db_path = Path("test_output/test_seiko_pattern.xlsx")
    
    # セクションデータを作成
    sections = [
        Section(
            number=1,
            text="長い文章のテキスト..." * 200,  # 2000文字以上
            questions=[],
            section_type="小説・物語",
            is_text_problem=True,
            char_count=2000
        ),
        Section(
            number=2,
            text="論説文のテキスト..." * 150,  # 1500文字以上
            questions=[],
            section_type="論説文",
            is_text_problem=True,
            char_count=1500
        ),
        Section(
            number=3,
            text="次の漢字の読みを答えなさい。",  # 短いテキスト
            questions=[],
            section_type="漢字・語句",
            is_text_problem=False,
            char_count=50
        )
    ]
    
    # 設問データ
    questions = [
        Question(number=1, text="問1", type="記述", section=1),
        Question(number=2, text="問2", type="選択", section=1),
        Question(number=3, text="問3", type="記述", section=2),
        Question(number=4, text="問4", type="選択", section=2),
        Question(number=5, text="問5", type="漢字", section=3),
        Question(number=6, text="問6", type="語句", section=3),
    ]
    
    # 分析結果を作成
    result = AnalysisResult(
        school_name="聖光学院",
        year="2025",
        total_characters=3550,
        sections=sections,
        questions=questions,
        sources=[
            ExamSource(author="芥川龍之介", title="羅生門"),
            ExamSource(author="池上彰", title="現代社会の見方"),
            None  # 漢字・語句には出典なし
        ],
        question_types={
            '記述': 2,
            '選択': 2,
            '漢字': 1,
            '語句': 1
        },
        genre="小説・物語",
        theme="人間の葛藤"
    )
    
    # 保存を実行
    print("📝 聖光学院パターンでデータを保存中...")
    success = manager.save_analysis_result(result)
    
    if success:
        print("✅ 保存成功")
        
        # 保存されたファイルを読み込んで確認
        df = pd.read_excel(manager.db_path, sheet_name='聖光学院')
        print("\n📊 保存されたデータの確認:")
        
        # 重要な列を確認
        check_cols = [
            ('文章1_出題形式', '文章1の出題形式'),
            ('文章1_出典', '文章1の出典'),
            ('文章1_文字数', '文章1の文字数'),
            ('文章2_出題形式', '文章2の出題形式'),
            ('文章2_出典', '文章2の出典'),
            ('文章2_文字数', '文章2の文字数'),
            ('文章3_出題形式', '文章3（存在しないはず）'),
            ('その他1_出題形式', 'その他1の出題形式'),
            ('その他1_設問数', 'その他1の設問数'),
        ]
        
        print("\n📋 列の内容:")
        for col, desc in check_cols:
            if col in df.columns:
                value = df[col].iloc[0] if not df.empty else 'N/A'
                if pd.notna(value):
                    print(f"  ✓ {desc}: {value}")
                else:
                    print(f"  ○ {desc}: （空欄）")
            else:
                print(f"  ✗ {desc}: 列が存在しません")
        
        # 実際に文章が2つ、その他が1つになっているか確認
        text_count = sum(1 for col in df.columns if col.startswith('文章') and '出典' in col and pd.notna(df[col].iloc[0]))
        other_count = sum(1 for col in df.columns if col.startswith('その他') and '出題形式' in col and pd.notna(df[col].iloc[0]))
        
        print(f"\n📈 集計結果:")
        print(f"  文章問題数: {text_count} （期待値: 2）")
        print(f"  その他問題数: {other_count} （期待値: 1）")
        
        if text_count == 2 and other_count == 1:
            print("\n🎉 正しく分類されています！")
        else:
            print("\n⚠️ 分類に問題があります")
            
    else:
        print("❌ 保存失敗")
    
    return success

if __name__ == "__main__":
    # 出力ディレクトリを作成
    Path("test_output").mkdir(exist_ok=True)
    
    # テスト実行
    test_seiko_pattern()