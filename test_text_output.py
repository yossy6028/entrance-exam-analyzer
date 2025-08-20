#!/usr/bin/env python3
"""
テキストファイル出力機能のテスト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.text_file_manager import TextFileManager
from models import AnalysisResult, Section, ExamSource, Question

def test_text_output():
    """テキスト出力機能をテスト"""
    
    # テストデータを作成
    result = AnalysisResult(
        school_name="聖光学院",
        year=2025,
        total_characters=19422,
        sections=[],
        questions=[],
        question_types={},
        sources=[]
    )
    
    # セクション1: 小説
    section1 = Section(
        number=1,
        title="文章1",
        section_type="文章1",
        char_count=8500,
        question_count=11
    )
    section1.genre = "小説"
    section1.theme = "本を通じた人と人との繋がり"
    section1.source = ExamSource(
        author="森沢明夫",
        title="本が紡いだ五つの奇跡"
    )
    
    # 問題を追加
    questions1 = [
        Question(number=i, text="", type="選択式", section=1) for i in range(1, 7)
    ]
    questions1.extend([
        Question(number=7, text="", type="記述式", section=1),
        Question(number=8, text="", type="記述式", section=1),
        Question(number=9, text="", type="記述式", section=1),
        Question(number=10, text="", type="抜き出し", section=1),
        Question(number=11, text="", type="その他", section=1)
    ])
    section1.questions = questions1
    
    # セクション2: 随筆
    section2 = Section(
        number=2,
        title="文章2",
        section_type="文章2",
        char_count=7200,
        question_count=10
    )
    section2.genre = "随筆"
    section2.theme = "自然界の見えない営みと生命の神秘"
    section2.source = ExamSource(
        author="永井玲子",
        title="見えないキノコの勤勉な日々"
    )
    
    # 問題を追加
    questions2 = [
        Question(number=i, text="", type="選択式", section=2) for i in range(1, 6)
    ]
    questions2.extend([
        Question(number=6, text="", type="記述式", section=2),
        Question(number=7, text="", type="記述式", section=2),
        Question(number=8, text="", type="記述式", section=2),
        Question(number=9, text="", type="抜き出し", section=2),
        Question(number=10, text="", type="その他", section=2)
    ])
    section2.questions = questions2
    
    # セクション3: 漢字・語句
    section3 = Section(
        number=3,
        title="漢字・語句",
        section_type="漢字・語句",
        char_count=0,
        question_count=15
    )
    
    result.sections = [section1, section2, section3]
    
    # 設問タイプを集計
    result.question_types = {
        "選択式": 11,
        "記述式": 6,
        "抜き出し": 2,
        "漢字・語句": 15,
        "その他": 2
    }
    
    # TextFileManagerを初期化（テスト用ディレクトリ）
    test_dir = Path.home() / "Desktop" / "test_output"
    test_dir.mkdir(exist_ok=True)
    
    manager = TextFileManager(str(test_dir))
    
    # 結果を辞書形式に変換
    result_dict = {
        'school_name': result.school_name,
        'year': result.year,
        'basic_info': {
            'total_chars': result.total_characters,
            'total_pages': 32,
            'test_time': 60
        },
        'sections': [],
        'features': [
            '文学的文章（小説）と論理的文章（科学随筆）のバランス',
            '現代的なテーマを扱いつつ、深い思考を促す内容',
            '記述問題は段階的な字数設定（30字→50字→80-100字）',
            '選択問題は基本的な読解力を問う4択が中心',
            '抜き出し問題で文章の精読力を確認'
        ],
        'time_allocation': [
            '文章1（小説）: 20-25分',
            '文章2（随筆）: 20-25分',
            '漢字・語句: 10-15分',
            '見直し: 5分'
        ]
    }
    
    # セクション情報を追加
    for section in result.sections:
        section_dict = {
            'type': section.section_type,
            'question_count': section.question_count,
            'char_count': section.char_count if hasattr(section, 'char_count') else 0
        }
        
        if hasattr(section, 'genre'):
            section_dict['genre'] = section.genre
            
        if hasattr(section, 'theme'):
            section_dict['theme'] = section.theme
            section_dict['summary'] = f"{section.theme}を描く{section.genre}"
            
        if hasattr(section, 'source'):
            section_dict['source'] = f"{section.source.author}『{section.source.title}』"
        
        # 設問タイプ別集計
        if hasattr(section, 'questions'):
            question_types = {}
            for q in section.questions:
                q_type = q.type
                if q_type == "選択式":
                    q_type = "選択"
                elif q_type == "記述式":
                    q_type = "記述"
                question_types[q_type] = question_types.get(q_type, 0) + 1
            section_dict['question_types'] = question_types
            
            # 詳細情報
            if question_types.get('選択', 0) > 0:
                section_dict['choice_details'] = {
                    '4択問題': 4,
                    '5択問題': 2
                }
            
            if question_types.get('記述', 0) > 0:
                section_dict['description_lengths'] = [
                    '30字以内: 1問',
                    '50字以内: 1問',
                    '80字以内: 1問'
                ]
        
        result_dict['sections'].append(section_dict)
    
    # テキストファイルに保存
    saved_path = manager.save_analysis_result(
        result_dict,
        "聖光学院",
        "2025"
    )
    
    print(f"✅ テキストファイルを保存しました: {saved_path}")
    
    # 保存したファイルを読み込んで確認
    content = manager.read_saved_file("聖光学院", "2025")
    if content:
        print("\n--- 保存されたファイルの内容 ---")
        print(content[:1000])  # 最初の1000文字を表示
        print("...")
    
    # 保存されたファイル一覧を表示
    files = manager.list_saved_files()
    print(f"\n保存されているファイル数: {len(files)}")
    for file in files:
        print(f"  - {file.name}")

if __name__ == "__main__":
    test_text_output()