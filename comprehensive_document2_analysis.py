#!/usr/bin/env python3
"""
聖光学院2025年国語 文章2（永井佳子）包括的分析
正確な設問抽出と不整合検証
"""

import re
from typing import List, Dict, Tuple

def main():
    """メイン分析関数"""
    with open('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).ocr.txt', 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    print("=== 聖光学院2025年国語 文章2（永井佳子）包括的設問分析 ===")
    print()
    
    # 永井佳子文章の設問を正確に抽出
    questions = extract_document2_questions_precise(full_text)
    
    print("=== 各設問の詳細分析 ===")
    print()
    
    analysis_results = []
    for q_num in ['問一', '問二', '問三', '問四', '問五', '問六', '問七', '問八']:
        if q_num in questions:
            analysis = analyze_question_precisely(questions[q_num])
            analysis_results.append({
                'number': q_num,
                'type': analysis['type'],
                'details': analysis['details'],
                'content': questions[q_num][:100] + "..." if len(questions[q_num]) > 100 else questions[q_num]
            })
            
            print(f"{q_num}: {analysis['type']} - {analysis['details']}")
            print(f"  内容例: {questions[q_num][:80]}...")
            print()
        else:
            print(f"{q_num}: 設問が見つかりませんでした")
            print()
    
    # 統計分析
    type_summary = {}
    descriptive_questions = []
    choice_questions = []
    other_questions = []
    
    for result in analysis_results:
        q_type = result['type']
        if q_type not in type_summary:
            type_summary[q_type] = 0
        type_summary[q_type] += 1
        
        if '記述' in q_type:
            descriptive_questions.append(f"{result['number']}: {result['details']}")
        elif '選択' in q_type:
            choice_questions.append(f"{result['number']}: {result['details']}")
        else:
            other_questions.append(f"{result['number']}: {result['details']}")
    
    print("=== 設問タイプ別統計 ===")
    for q_type, count in type_summary.items():
        print(f"{q_type}: {count}問")
    
    print()
    print("=== 記述問題詳細 ===")
    
    word_limit_desc = []
    no_word_limit_desc = []
    
    for desc in descriptive_questions:
        if '字以内' in desc or '一行' in desc:
            word_limit_desc.append(desc)
        else:
            no_word_limit_desc.append(desc)
    
    print(f"文字数指定あり記述問題: {len(word_limit_desc)}問")
    for q in word_limit_desc:
        print(f"  {q}")
    
    print(f"文字数指定なし記述問題: {len(no_word_limit_desc)}問")
    for q in no_word_limit_desc:
        print(f"  {q}")
    
    total_descriptive = len(descriptive_questions)
    print(f"記述問題総数: {total_descriptive}問")
    
    print()
    print("=== 選択問題詳細 ===")
    print(f"選択問題総数: {len(choice_questions)}問")
    for q in choice_questions:
        print(f"  {q}")
    
    if other_questions:
        print()
        print("=== その他問題 ===")
        for q in other_questions:
            print(f"  {q}")
    
    # 不整合検証
    print()
    print("=== 不整合検証結果 ===")
    print("="*60)
    
    # 問題の表示データ（表題など）から推測される構成
    expected_descriptive = 3  # 表示では「記述問題3問」となっているらしい
    
    print(f"【検証】表示上の記述問題数: {expected_descriptive}問（推定）")
    print(f"【実際】実際の記述問題数: {total_descriptive}問")
    
    if total_descriptive != expected_descriptive:
        print()
        print("🚨 【不整合を発見】")
        print(f"表示では記述問題{expected_descriptive}問とされているが、実際は{total_descriptive}問")
        
        if total_descriptive == 2 and len(word_limit_desc) == 2:
            print()
            print("【原因分析】")
            print("- 20字以内の記述問題: 1問（問四）")
            print("- 80字以内の記述問題: 1問（問八）") 
            print("- 合計: 2問（文字数指定あり記述問題のみ）")
            print("- 表示の「3問」は数え間違いまたは他セクションとの混同の可能性")
            
        elif total_descriptive > expected_descriptive:
            print()
            print("【原因分析】")
            print(f"実際の記述問題が表示よりも{total_descriptive - expected_descriptive}問多い")
            print("表示の更新が必要")
    else:
        print("✅ 【不整合なし】表示と実際の記述問題数が一致")
    
    print()
    print("=== 修正案 ===")
    print("="*30)
    
    if total_descriptive == 2 and len(word_limit_desc) == 2 and len(no_word_limit_desc) == 0:
        print("【推奨修正】")
        print(f"表示を「記述問題{total_descriptive}問」に修正")
        print("詳細: 20字以内1問、80字以内1問")
    elif total_descriptive > 2:
        print("【推奨修正】")
        print(f"表示を「記述問題{total_descriptive}問」に修正")
        print(f"  - 文字数指定あり: {len(word_limit_desc)}問")
        print(f"  - 文字数指定なし: {len(no_word_limit_desc)}問")
    else:
        print("詳細確認が必要です")
    
    print()
    print("=== 全設問一覧（最終確認用） ===")
    print("="*40)
    for result in analysis_results:
        print(f"{result['number']}: {result['type']} ({result['details']})")
    
    total_questions = len(analysis_results)
    print(f"\n全設問総数: {total_questions}問")
    print(f"設問構成: 選択{len(choice_questions)}問 + 記述{total_descriptive}問 + その他{len(other_questions)}問 = {total_questions}問")

def extract_document2_questions_precise(text: str) -> Dict[str, str]:
    """
    永井佳子文章の設問を行番号ベースで正確に抽出
    """
    questions = {}
    lines = text.split('\n')
    
    # 永井佳子関連の設問開始行を特定
    doc2_start_line = None
    for i, line in enumerate(lines):
        if '線部A「様相」、B「往来」、C「注力」' in line:
            doc2_start_line = i - 2  # 「問一」の行から開始
            break
    
    if doc2_start_line is None:
        print("ERROR: 文章2の設問開始位置が見つかりません")
        return {}
    
    # 各問を行ベースで抽出
    current_question = None
    current_content = []
    
    for i in range(doc2_start_line, len(lines)):
        line = lines[i].strip()
        
        # 解答用紙セクションが始まったら終了
        if '解答用紙' in line or '氏名' in line:
            break
        
        # 問一〜問八の開始を検出
        if re.match(r'^問[一二三四五六七八]$', line):
            # 前の問題を保存
            if current_question:
                questions[current_question] = '\n'.join(current_content).strip()
            
            # 新しい問題を開始
            current_question = line
            current_content = []
        elif current_question:
            # 現在の問題の内容を追加
            current_content.append(line)
    
    # 最後の問題を保存
    if current_question:
        questions[current_question] = '\n'.join(current_content).strip()
    
    return questions

def analyze_question_precisely(text: str) -> Dict[str, str]:
    """
    設問テキストから正確なタイプを判定
    """
    text_clean = text.replace('\n', ' ').replace('\r', ' ').strip()
    
    # 記述問題（文字数指定あり）の判定
    if re.search(r'二十字以内.*説明しなさい', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '20字以内記述'}
    
    if re.search(r'八十字以内.*説明しなさい', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '80字以内記述'}
    
    if re.search(r'一行で.*説明しなさい', text_clean):
        return {'type': '記述（文字数指定あり）', 'details': '1行記述'}
    
    # 選択問題の判定
    if re.search(r'記号で答えなさい', text_clean):
        # 選択肢数を正確に数える
        katakana_choices = re.findall(r'[アイウエオカキクケコ]', text_clean)
        if katakana_choices:
            unique_choices = sorted(set(katakana_choices))
            return {'type': '選択', 'details': f'{len(unique_choices)}択選択'}
        else:
            return {'type': '選択', 'details': '選択（択数不明）'}
    
    # 記述問題（文字数指定なし）
    if re.search(r'説明しなさい', text_clean) and not re.search(r'字以内|一行で', text_clean):
        return {'type': '記述（文字数指定なし）', 'details': '自由記述'}
    
    # 抜き出し問題
    if re.search(r'抜き出[しせ]', text_clean):
        return {'type': '抜き出し', 'details': '本文抜き出し'}
    
    # その他特殊な問題タイプ
    if re.search(r'熟語の構成', text_clean):
        return {'type': '選択', 'details': '熟語構成問題'}
    
    if re.search(r'同じ言葉が入ります', text_clean):
        return {'type': '選択', 'details': '空欄補充選択'}
    
    return {'type': '不明', 'details': f'分類困難（{text_clean[:30]}...）'}

if __name__ == '__main__':
    main()