#!/usr/bin/env python3
"""
聖光学院のセクション分割を修正して再分析
"""

import json
from modules.final_content_extractor import FinalContentExtractor
from modules.content_type_formatter import ContentTypeFormatter

def fix_and_reanalyze():
    """セクション分割を修正して再分析"""
    
    # OCRテキストを読み込み
    with open('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/2025過去問/聖光25.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 手動でセクションを定義（正しい構造に基づいて）
    sections = []
    
    # セクション1: 漢字・語句問題（最初の部分、出典なし）
    kanji_end = text.find('送られてきたメール')  # 小説の開始位置
    if kanji_end > 0:
        kanji_section = text[:kanji_end]
        sections.append({
            'number': 1,
            'text': kanji_section,
            'source': None,
            'is_kanji': True,
            'genre': '漢字・語句',
            'theme': '漢字・語句'
        })
    
    # セクション2: 森沢明夫の小説（問一〜問八）
    morisawa_start = text.find('送られてきたメール')
    morisawa_end = text.find('――永井佳子')
    if morisawa_start > 0 and morisawa_end > 0:
        morisawa_section = text[morisawa_start:morisawa_end]
        sections.append({
            'number': 2,
            'text': morisawa_section,
            'source': {
                'author': '森沢明夫',
                'work': '本が紡いだ五つの奇跡'
            },
            'is_kanji': False,
            'genre': '小説・物語',
            'theme': '人間関係・成長'
        })
    
    # セクション3: 永井佳子のエッセイ（問一〜問八）
    nagai_start = morisawa_end
    nagai_section = text[nagai_start:]
    sections.append({
        'number': 3,
        'text': nagai_section,
        'source': {
            'author': '永井佳子',
            'work': '見えないキノコの勤勉な日々'
        },
        'is_kanji': False,
        'genre': '論説文',
        'theme': '自然・環境'
    })
    
    # 結果をまとめる
    result = {
        'total_characters': len(text.replace(' ', '').replace('\\n', '')),
        'total_questions': 0,
        'sections': [],
        'question_types': {
            '選択': 0,
            '記述': 0,
            '抜き出し': 0,
            '漢字・語句': 0
        }
    }
    
    # 各セクションを処理
    extractor = FinalContentExtractor()
    for section_info in sections:
        # 設問を抽出
        questions = extractor._extract_questions_from_section(section_info['text'])
        
        # セクション情報を構築
        section_data = {
            'number': section_info['number'],
            'source': section_info.get('source'),
            'characters': len(section_info['text'].replace(' ', '').replace('\\n', '')),
            'questions': questions,
            'genre': section_info['genre'],
            'theme': section_info['theme'],
            'is_kanji': section_info.get('is_kanji', False)
        }
        
        result['sections'].append(section_data)
        result['total_questions'] += len(questions)
        
        # 設問タイプを分類
        for q in questions:
            q_type = extractor._classify_question(q['text'])
            q['type'] = q_type
            if q_type in result['question_types']:
                result['question_types'][q_type] += 1
    
    # デバッグ出力
    print("修正後のセクション構成:")
    for i, section in enumerate(result['sections']):
        print(f"\nセクション{i+1}:")
        if section.get('source'):
            print(f"  出典: {section['source']['author']} 『{section['source']['work']}』")
        else:
            print(f"  出典: なし（{section['genre']}）")
        print(f"  文字数: {section['characters']:,}")
        print(f"  設問数: {len(section['questions'])}")
        if section['questions']:
            print(f"  設問番号: {', '.join([q['number'] for q in section['questions']])}")
    
    # 新形式でフォーマット
    formatter = ContentTypeFormatter()
    formatted_data = formatter.format_data(
        result,
        school_name='聖光学院中学校',
        year=2025
    )
    
    # 表示
    formatter.display_formatted_data(formatted_data)
    
    # 保存
    formatter.save_to_excel(formatted_data, sheet_name='聖光学院中学校')
    
    print("\n✅ 修正版をExcelに保存しました")
    
    # JSONでも保存
    with open('seiko_fixed_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

if __name__ == "__main__":
    fix_and_reanalyze()