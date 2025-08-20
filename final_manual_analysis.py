#!/usr/bin/env python3
"""
聖光学院2025年国語 文章2（永井佳子）手動分析
OCRテキストから直接内容を確認して不整合を検証
"""

def main():
    with open('/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).ocr.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=== 聖光学院2025年国語 文章2（永井佳子）手動分析 ===")
    print()
    
    # OCRテキストから直接各設問を確認
    print("=== 各設問の直接確認 ===")
    
    # 永井佳子文章の設問部分を特定
    nagaii_questions = analyze_nagaii_questions(text)
    
    print("\n=== 分析結果サマリー ===")
    
    choice_count = 0
    descriptive_count = 0
    word_limit_descriptive = 0
    no_word_limit_descriptive = 0
    
    descriptive_details = []
    
    for q_num, q_info in nagaii_questions.items():
        print(f"{q_num}: {q_info['type']} - {q_info['details']}")
        
        if q_info['type'] == '選択':
            choice_count += 1
        elif q_info['type'] == '記述（文字数指定あり）':
            descriptive_count += 1
            word_limit_descriptive += 1
            descriptive_details.append(f"{q_num}: {q_info['details']}")
        elif q_info['type'] == '記述（文字数指定なし）':
            descriptive_count += 1
            no_word_limit_descriptive += 1
            descriptive_details.append(f"{q_num}: {q_info['details']}")
    
    print(f"\n=== 統計 ===")
    print(f"選択問題: {choice_count}問")
    print(f"記述問題: {descriptive_count}問")
    print(f"  - 文字数指定あり: {word_limit_descriptive}問")
    print(f"  - 文字数指定なし: {no_word_limit_descriptive}問")
    
    print(f"\n=== 記述問題詳細 ===")
    for detail in descriptive_details:
        print(f"  {detail}")
    
    print(f"\n=== 不整合検証 ===")
    print(f"{'='*50}")
    
    # 表示では「記述問題3問」とされているかの確認
    expected_descriptive = 3
    actual_descriptive = descriptive_count
    
    print(f"表示上の記述問題数（推定）: {expected_descriptive}問")
    print(f"実際の記述問題数: {actual_descriptive}問")
    
    if actual_descriptive != expected_descriptive:
        print(f"\n🚨 【不整合発見】")
        print(f"表示と実際の記述問題数が一致しません")
        
        if actual_descriptive == 2 and word_limit_descriptive == 2:
            print(f"\n【詳細分析】")
            print(f"実際には文字数指定ありの記述問題が{word_limit_descriptive}問のみ存在")
            print(f"・20字以内記述: 1問")
            print(f"・80字以内記述: 1問")
            print(f"・合計: {word_limit_descriptive}問")
        
        print(f"\n【修正案】")
        print(f"表示を「記述問題{actual_descriptive}問（20字以内1問、80字以内1問）」に修正")
    else:
        print(f"\n✅ 【不整合なし】")
    
    print(f"\n=== 最終結論 ===")
    print(f"文章2（永井佳子）の設問構成:")
    print(f"  選択問題: {choice_count}問")
    print(f"  記述問題: {actual_descriptive}問")
    
    # 記述問題の詳細
    if word_limit_descriptive >= 1:
        print(f"  　├ 20字以内: 1問")
    if word_limit_descriptive >= 2:
        print(f"  　├ 1行記述: 1問")  
    if word_limit_descriptive >= 3:
        print(f"  　└ 80字以内: 1問")
    elif word_limit_descriptive >= 1:
        print(f"  　└ 80字以内: 1問")
        
    print(f"  合計: {choice_count + actual_descriptive}問")
    
    # 記述問題の内訳が正しく3問であることの確認
    if actual_descriptive == 3:
        print(f"\n✅ 【結論】表示されている「記述問題3問」は正確")
        print(f"内訳: 20字以内1問 + 1行記述1問 + 80字以内1問 = 3問")

def analyze_nagaii_questions(text: str) -> dict:
    """永井佳子文章の設問を手動で確認"""
    
    questions = {}
    
    # 問一: 熟語構成問題（様相・往来・注力）
    if '線部A「様相」、B「往来」、C「注力」について、熟語の構成' in text:
        questions['問一'] = {
            'type': '選択',
            'details': '熟語構成問題（6択程度）'
        }
    
    # 問二: 空欄補充問題（☑に同じ言葉が入る）
    if '本文中の二か所の ☑' in text and '同じ言葉が入ります' in text:
        questions['問二'] = {
            'type': '選択',
            'details': '空欄補充選択（5択程度）'
        }
    
    # 問三: 菌類仕事中の説明（選択）
    if '《菌類仕事中》の目印のようなもの' in text and 'その説明として最もふさわしいものを、次のア~オの中から' in text:
        questions['問三'] = {
            'type': '選択',
            'details': '内容理解選択（5択）'
        }
    
    # 問四: 20字以内記述問題
    if '線部②に「人が作るものにたった一つの価値なんて存在するのだろうかと疑問に思ってい' in text and '二十字以内で説明しなさい' in text:
        questions['問四'] = {
            'type': '記述（文字数指定あり）',
            'details': '20字以内記述'
        }
    
    # 問五: 抽象の力（選択）
    if '「抽象の力を借り、形の魅力をできるだけ発揮させる」' in text and 'その説明として最もふさわしいものを、次のア~オの中から' in text:
        questions['問五'] = {
            'type': '選択',
            'details': '内容理解選択（5択）'
        }
    
    # 問六: 菌類についても（1行記述）
    if '菌類についてもそうである' in text and '一行' in text:
        questions['問六'] = {
            'type': '記述（文字数指定あり）',
            'details': '1行記述（約40字程度）'
        }
    
    # 問七: 自立し次の課題へ（選択）
    if 'それが自立し、さらに次の課題におのずから向かっている' in text and 'その説明として最もふさわしいものを、次のア~オの中から' in text:
        questions['問七'] = {
            'type': '選択',
            'details': '内容理解選択（5択）'
        }
    
    # 問八: 80字以内記述
    if '「成果だけに止まらない目に見えない創造の蠢きのなかに身を投じる」' in text and '八十字以内で説明しなさい' in text:
        questions['問八'] = {
            'type': '記述（文字数指定あり）',
            'details': '80字以内記述'
        }
    
    return questions

if __name__ == '__main__':
    main()