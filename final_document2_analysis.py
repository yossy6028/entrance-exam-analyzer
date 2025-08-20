#!/usr/bin/env python3
"""
聖光学院2025年国語 文章2（永井佳子）最終調査
正確な設問分析と不整合検証
"""

import re
from typing import List, Dict, Tuple

def main():
    """メイン分析関数"""
    # OCRテキストを読み込み
    with open('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).ocr.txt', 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    print("=== 聖光学院2025年国語 文章2（永井佳子）設問不整合調査 ===")
    print()
    
    # 永井佳子文章の設問部分を特定
    doc2_questions = extract_questions_manually(full_text)
    
    # 各設問を詳細分析
    print("=== 設問詳細分析 ===")
    print()
    
    question_analysis = []
    for q_num, q_data in doc2_questions.items():
        analysis = analyze_detailed_question_type(q_data['text'])
        question_analysis.append({
            'number': q_num,
            'type': analysis['type'],
            'details': analysis['details'],
            'text_sample': q_data['text'][:100] + "..." if len(q_data['text']) > 100 else q_data['text']
        })
        
        print(f"{q_num}: {analysis['type']} - {analysis['details']}")
        print(f"  内容: {q_data['text'][:80]}...")
        print()
    
    # 統計分析
    print("=== 設問タイプ別集計 ===")
    type_counts = {}
    descriptive_questions = []
    
    for qa in question_analysis:
        q_type = qa['type']
        if q_type not in type_counts:
            type_counts[q_type] = 0
        type_counts[q_type] += 1
        
        if '記述' in q_type:
            descriptive_questions.append(f"{qa['number']}: {qa['details']}")
    
    for q_type, count in type_counts.items():
        print(f"{q_type}: {count}問")
    
    print()
    print("=== 記述問題詳細分析 ===")
    
    # 記述問題の分類
    word_limit_questions = []
    no_word_limit_questions = []
    
    for qa in question_analysis:
        if qa['type'] == '記述（文字数指定あり）':
            word_limit_questions.append(f"{qa['number']}: {qa['details']}")
        elif qa['type'] == '記述（文字数指定なし）':
            no_word_limit_questions.append(f"{qa['number']}: {qa['details']}")
    
    print(f"文字数指定あり記述: {len(word_limit_questions)}問")
    for q in word_limit_questions:
        print(f"  {q}")
    
    print(f"文字数指定なし記述: {len(no_word_limit_questions)}問")
    for q in no_word_limit_questions:
        print(f"  {q}")
    
    total_descriptive = len(word_limit_questions) + len(no_word_limit_questions)
    print(f"記述問題総数: {total_descriptive}問")
    
    # 不整合の検証
    print()
    print("=== 不整合検証結果 ===")
    print("="*50)
    
    # 表示での記述問題数（仮定：3問と表示されている）
    expected_descriptive = 3
    
    if total_descriptive != expected_descriptive:
        print(f"【不整合を発見】")
        print(f"表示では記述問題{expected_descriptive}問とあるが、実際は{total_descriptive}問")
        print()
        print(f"実際の内訳:")
        print(f"  - 文字数指定あり: {len(word_limit_questions)}問")
        print(f"  - 文字数指定なし: {len(no_word_limit_questions)}問")
        
        if len(word_limit_questions) == 2 and len(no_word_limit_questions) == 0:
            print()
            print("【原因分析】")
            print("文字数指定ありの記述問題のみ2問存在（20字以内1問、80字以内1問）")
            print("表示では3問となっているが、実際は2問のみ")
        
        if len(word_limit_questions) == 2 and len(no_word_limit_questions) == 2:
            print()
            print("【原因分析】")
            print("記述問題が実際は4問存在している")
            print("表示の「3問」は誤りの可能性")
    else:
        print("【不整合なし】表示と実際の設問数が一致")
    
    print()
    print("=== 修正案 ===")
    if len(word_limit_questions) == 2 and len(no_word_limit_questions) == 0:
        print("表示を「記述問題2問（20字以内1問、80字以内1問）」に修正")
    elif len(word_limit_questions) == 2 and len(no_word_limit_questions) == 2:
        print("表示を「記述問題4問（20字以内1問、80字以内1問、文字数指定なし2問）」に修正")
    else:
        print(f"表示を「記述問題{total_descriptive}問」に修正し、詳細内訳を確認")

def extract_questions_manually(text: str) -> Dict:
    """
    OCRテキストから永井佳子文章の設問を手動で正確に抽出
    """
    questions = {}
    
    # 永井佳子文章の設問部分を特定（熟語構成問題から開始）
    # 問一: 熟語構成問題
    q1_start = text.find('線部A「様相」、B「往来」、C「注力」について、熟語の構成として同じもの')
    if q1_start != -1:
        q1_end = text.find('問二', q1_start)
        if q1_end == -1:
            q1_end = q1_start + 500
        questions['問一'] = {
            'text': text[q1_start:q1_end].strip()
        }
    
    # 問二: 空欄補充問題
    q2_pattern = r'問二[^問]*☑[^問]*同じ言葉が入ります[^問]*'
    q2_match = re.search(q2_pattern, text, re.DOTALL)
    if q2_match:
        questions['問二'] = {
            'text': q2_match.group().strip()
        }
    
    # 問三: 菌類仕事中の説明問題（選択）
    q3_pattern = r'問三[^問]*《菌類仕事中》[^問]*記号で答えなさい[^問]*'
    q3_match = re.search(q3_pattern, text, re.DOTALL)
    if q3_match:
        questions['問三'] = {
            'text': q3_match.group().strip()
        }
    
    # 問四: 20字以内記述問題
    q4_pattern = r'線部②.*二十字以内で説明しなさい'
    q4_match = re.search(q4_pattern, text, re.DOTALL)
    if q4_match:
        questions['問四'] = {
            'text': q4_match.group().strip()
        }
    
    # 問五: 選択問題（抽象の力）
    q5_pattern = r'問五[^問]*抽象の力[^問]*記号で答えなさい'
    q5_match = re.search(q5_pattern, text, re.DOTALL)
    if q5_match:
        questions['問五'] = {
            'text': q5_match.group().strip()
        }
    
    # 問六: 1行記述問題
    q6_pattern = r'問六[^問]*菌類についてもそうである[^問]*一行で説明しなさい'
    q6_match = re.search(q6_pattern, text, re.DOTALL)
    if q6_match:
        questions['問六'] = {
            'text': q6_match.group().strip()
        }
    
    # 問七: 選択問題（自立し次の課題へ）
    q7_pattern = r'問七[^問]*それが自立し[^問]*記号で答えなさい'
    q7_match = re.search(q7_pattern, text, re.DOTALL)
    if q7_match:
        questions['問七'] = {
            'text': q7_match.group().strip()
        }
    
    # 問八: 80字以内記述問題
    q8_pattern = r'問八[^問]*八十字以内で説明しなさい'
    q8_match = re.search(q8_pattern, text, re.DOTALL)
    if q8_match:
        questions['問八'] = {
            'text': q8_match.group().strip()
        }
    
    return questions

def analyze_detailed_question_type(text: str) -> Dict:
    """
    設問テキストから詳細なタイプを分析
    """
    text_clean = text.replace('\n', ' ').strip()
    
    # 記述問題（文字数指定あり）
    if re.search(r'二十字以内', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '20字以内'}
    if re.search(r'八十字以内', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '80字以内'}
    if re.search(r'一行で.*説明しなさい', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '1行（約40字程度）'}
    
    # 選択問題
    if re.search(r'記号で答えなさい', text_clean):
        # 選択肢数を数える
        choices = re.findall(r'[アイウエオカキクケコ]', text_clean)
        unique_choices = sorted(set(choices))
        if len(unique_choices) >= 2:
            return {'type': '選択', 'details': f'{len(unique_choices)}択（{"-".join(unique_choices)}）'}
        else:
            return {'type': '選択', 'details': '択数不明'}
    
    # 記述問題（文字数指定なし）
    if re.search(r'説明しなさい', text_clean) and not re.search(r'字以内|一行で', text_clean):
        return {'type': '記述（文字数指定なし）', 'details': '自由記述'}
    
    # 抜き出し問題
    if re.search(r'抜き出[しせ]', text_clean):
        return {'type': '抜き出し', 'details': '本文から抜き出し'}
    
    # 熟語構成問題
    if re.search(r'熟語の構成.*同じもの', text_clean):
        return {'type': '選択', 'details': '熟語構成（6択程度）'}
    
    # 空欄補充
    if re.search(r'同じ言葉が入ります', text_clean):
        return {'type': '選択', 'details': '空欄補充（5択程度）'}
    
    return {'type': '不明', 'details': f'分類不可（{text_clean[:50]}...）'}

if __name__ == '__main__':
    main()