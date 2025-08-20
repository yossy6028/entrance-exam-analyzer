#!/usr/bin/env python3
"""
聖光学院2025年国語 文章2（永井佳子）設問不整合調査スクリプト
記述問題の表示数と実際の内訳の不整合を分析
"""

import re
from typing import List, Dict, Tuple

def extract_document2_questions(text: str) -> Tuple[str, List[Dict]]:
    """
    文章2（永井佳子）の設問部分を抽出・分析
    
    Returns:
        設問テキストと設問リスト
    """
    # 永井佳子の文章開始位置を特定
    nagaii_start_match = re.search(r'永井佳子.*見えないキノコ.*勤勉な日々', text)
    
    if not nagaii_start_match:
        # 代替検索：四章から探す
        doc2_start_match = re.search(r'問一.*線部A.*様相.*往来.*注力', text)
        if doc2_start_match:
            doc2_start = doc2_start_match.start()
        else:
            print("ERROR: 文章2（永井佳子）の設問が見つかりません")
            return "", []
    else:
        # 永井佳子の文章が見つかった場合、その後の問一を探す
        nagaii_end = nagaii_start_match.end()
        after_nagaii = text[nagaii_end:]
        doc2_start_match = re.search(r'問一', after_nagaii)
        if doc2_start_match:
            doc2_start = nagaii_end + doc2_start_match.start()
        else:
            print("ERROR: 永井佳子の文章後の設問が見つかりません")
            return "", []
    
    # 文章2の設問部分を抽出
    doc2_text = text[doc2_start:doc2_start + 15000]
    
    # 解答用紙部分を除外
    answer_sheet_match = re.search(r'聖光学院中学校.*解答用紙|氏名.*番号', doc2_text)
    if answer_sheet_match:
        doc2_text = doc2_text[:answer_sheet_match.start()]
    
    print("=== 文章2（永井佳子）設問分析 ===")
    print(f"抽出範囲: {len(doc2_text)}文字")
    print(f"抽出開始: {text[doc2_start:doc2_start+100]}...")
    
    # より詳細な設問抽出
    questions = []
    
    # まず永井佳子文章の設問部分を正確に特定
    # 「様相・往来・注力」の熟語問題が問一のはず
    question_texts = {
        '問一': '',
        '問二': '',
        '問三': '',
        '問四': '',
        '問五': '',
        '問六': '',
        '問七': '',
        '問八': ''
    }
    
    # 各問を詳細に検索
    for i in range(1, 9):
        question_num = f'問{["", "一", "二", "三", "四", "五", "六", "七", "八"][i]}'
        
        # 問iの位置を探す
        pattern = f'{question_num}.*?(?=問[一二三四五六七八]|$)'
        matches = re.findall(pattern, doc2_text, re.DOTALL)
        
        if matches:
            question_text = matches[0].strip()
            question_texts[question_num] = question_text
            
            # 設問タイプを分析
            question_type = analyze_question_type(question_text)
            questions.append({
                'name': question_num,
                'text': question_text[:300] + "..." if len(question_text) > 300 else question_text,
                'type': question_type['type'],
                'details': question_type['details'],
                'full_text': question_text  # デバッグ用
            })
            
            print(f"\n{question_num}: {question_type['type']} - {question_type['details']}")
            print(f"  内容: {question_text[:100]}...")
    
    return doc2_text, questions

def analyze_question_type(text: str) -> Dict:
    """
    設問のタイプと詳細を分析
    """
    text_clean = text.replace('\n', ' ').replace('\r', ' ')
    
    # 記述問題（文字数指定あり）
    word_limit_patterns = [
        (r'二十字以内', '20字以内'),
        (r'八十字以内', '80字以内'),
        (r'一行で', '1行'),
        (r'([0-9]+)字以内', lambda m: f"{m.group(1)}字以内"),
    ]
    
    for pattern, detail_func in word_limit_patterns:
        match = re.search(pattern, text_clean)
        if match:
            detail = detail_func(match) if callable(detail_func) else detail_func
            return {
                'type': '記述（文字数指定あり）',
                'details': detail
            }
    
    # 選択問題（記号で答える）
    if re.search(r'記号[でを]?答え', text_clean):
        # 選択肢を数える（より正確に）
        choices = []
        
        # カタカナ選択肢
        katakana_choices = re.findall(r'[アイウエオカキクケコ]', text_clean)
        if katakana_choices:
            choices = sorted(set(katakana_choices))
        
        # アルファベット選択肢
        if not choices:
            alpha_choices = re.findall(r'[A-E]', text_clean)
            if alpha_choices:
                choices = sorted(set(alpha_choices))
        
        # 数字選択肢
        if not choices:
            num_choices = re.findall(r'[1-5]', text_clean)
            if num_choices:
                choices = sorted(set(num_choices))
        
        if choices:
            return {
                'type': '選択',
                'details': f"{len(choices)}択（{'-'.join(choices)}）"
            }
        else:
            return {
                'type': '選択',
                'details': '択数不明'
            }
    
    # 抜き出し問題
    if re.search(r'抜[きく]出[しせ]', text_clean) or re.search(r'書[きく]抜[きけ]', text_clean):
        return {
            'type': '抜き出し',
            'details': '本文から抜き出し'
        }
    
    # 記述問題（文字数指定なし）の詳細判定
    if re.search(r'説明[しせ]なさい', text_clean):
        return {
            'type': '記述（文字数指定なし）',
            'details': '説明記述'
        }
    
    if re.search(r'書[きけ]なさい', text_clean):
        return {
            'type': '記述（文字数指定なし）',
            'details': '自由記述'
        }
    
    if re.search(r'答え[なさい]', text_clean):
        return {
            'type': '記述（文字数指定なし）',
            'details': '答え記述'
        }
    
    # 熟語の構成問題（文章2特有）
    if re.search(r'熟語の構成.*同じもの', text_clean):
        return {
            'type': '選択',
            'details': '熟語構成問題（文字数不明）'
        }
    
    # 空欄補充問題
    if re.search(r'☑.*入ります', text_clean) or re.search(r'同じ言葉が入ります', text_clean):
        return {
            'type': '選択',
            'details': '空欄補充選択'
        }
    
    return {
        'type': '不明',
        'details': f'タイプを特定できません（内容: {text_clean[:50]}...）'
    }

def analyze_inconsistency(questions: List[Dict]) -> Dict:
    """
    記述問題の不整合を分析
    """
    # 設問タイプ別に集計
    type_counts = {}
    descriptive_details = []
    
    for q in questions:
        q_type = q['type']
        if q_type not in type_counts:
            type_counts[q_type] = 0
        type_counts[q_type] += 1
        
        if '記述' in q_type:
            descriptive_details.append(f"{q['name']}: {q['details']}")
    
    # 記述問題の詳細分析
    word_limit_count = sum(1 for q in questions if '文字数指定あり' in q['type'])
    no_word_limit_count = sum(1 for q in questions if '文字数指定なし' in q['type'])
    total_descriptive = word_limit_count + no_word_limit_count
    
    print("\n=== 設問タイプ別集計 ===")
    for q_type, count in type_counts.items():
        print(f"{q_type}: {count}問")
    
    print("\n=== 記述問題詳細 ===")
    print(f"文字数指定あり: {word_limit_count}問")
    print(f"文字数指定なし: {no_word_limit_count}問")
    print(f"記述問題総数: {total_descriptive}問")
    
    for detail in descriptive_details:
        print(f"  {detail}")
    
    # 不整合の確認
    inconsistency = {}
    
    # もし表示が「記述問題3問」だったとしても実際の内訳を確認
    if total_descriptive != 3:
        inconsistency['total_count'] = f"記述問題総数が期待値と異なる: 実際{total_descriptive}問"
    
    if word_limit_count == 2 and total_descriptive == 2:
        inconsistency['missing_third'] = "記述問題が2問しかない（表示では3問となっているはず）"
    
    return {
        'type_counts': type_counts,
        'word_limit_count': word_limit_count,
        'no_word_limit_count': no_word_limit_count,
        'total_descriptive': total_descriptive,
        'descriptive_details': descriptive_details,
        'inconsistencies': inconsistency
    }

def main():
    """メイン実行関数"""
    # OCRテキストを読み込み
    with open('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).ocr.txt', 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    # 文章2の設問を抽出・分析
    doc2_text, questions = extract_document2_questions(full_text)
    
    if not questions:
        print("ERROR: 設問が見つかりませんでした")
        return
    
    # 不整合を分析
    analysis = analyze_inconsistency(questions)
    
    print("\n" + "="*50)
    print("=== 不整合分析結果 ===")
    print("="*50)
    
    if analysis['inconsistencies']:
        print("【不整合を発見】")
        for key, message in analysis['inconsistencies'].items():
            print(f"  {message}")
    else:
        print("【不整合なし】設問数と内訳は一致しています")
    
    print(f"\n【最終結果】")
    print(f"記述問題総数: {analysis['total_descriptive']}問")
    print(f"  - 文字数指定あり: {analysis['word_limit_count']}問")
    print(f"  - 文字数指定なし: {analysis['no_word_limit_count']}問")
    
    # 具体的な設問リスト
    print(f"\n【記述問題の内訳】")
    for detail in analysis['descriptive_details']:
        print(f"  {detail}")
    
    # 修正案を提示
    print("\n【修正案】")
    if analysis['total_descriptive'] == 2 and analysis['word_limit_count'] == 2:
        print("- 表示を「記述問題2問（20字以内1問、80字以内1問）」に修正")
    elif analysis['total_descriptive'] == 3:
        print("- 問題なし、現在の表示が正しい")
    else:
        print("- 実際の設問数に合わせて表示を修正してください")

if __name__ == '__main__':
    main()