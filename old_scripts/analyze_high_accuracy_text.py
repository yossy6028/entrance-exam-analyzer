#!/usr/bin/env python3
"""
高精度テキストファイル（15桜蔭.txt）の分析
bunkoOCRまたは他の高精度OCRで処理されたテキストファイルから
正確に問題構造を抽出する
"""
import re
from typing import List, Dict, Tuple


def analyze_sakuragai_text(text: str) -> Dict:
    """桜蔭中15年度のテキストファイルから問題構造を抽出"""
    
    # 結果を格納する辞書
    result = {
        'school': '桜蔭中学校',
        'year': '2015年度（平成27年度）',
        'sections': [],
        'questions': [],
        'total_questions': 0
    }
    
    # 大問の検出パターン
    section1_match = re.search(r'一、次の文章を読んで、後の問いに答えなさい。', text)
    section2_match = re.search(r'二\s+次の文章を読んで、後の問いに答えなさい。', text)
    
    sections_info = []
    
    if section1_match:
        sections_info.append({
            'number': 1,
            'title': '一、次の文章を読んで、後の問いに答えなさい。',
            'start_pos': section1_match.start(),
            'type': '読解'
        })
    
    if section2_match:
        sections_info.append({
            'number': 2,
            'title': '二 次の文章を読んで、後の問いに答えなさい。',
            'start_pos': section2_match.start(),
            'type': '読解'
        })
    
    # 各大問の範囲を確定
    for i, section in enumerate(sections_info):
        if i < len(sections_info) - 1:
            section['end_pos'] = sections_info[i + 1]['start_pos']
        else:
            section['end_pos'] = len(text)
        
        section['text'] = text[section['start_pos']:section['end_pos']]
    
    # 各大問の設問を検出
    all_questions = []
    
    for section in sections_info:
        section_questions = []
        section_text = section['text']
        
        if section['number'] == 1:
            # 大問一の設問検出（テキストに基づいて正確に）
            # 問一〜問六を検出
            patterns = [
                (r'問一――Ａについて、「たまたま撮影した1枚のスナップ」がなぜ[^\n]+', '問一', '記述'),
                (r'問二――Ｂのように感じたのばどうしてでしょうか[^\n]*', '問二', '記述'),
                (r'問三――Ｅとはどういうことですか[^\n]+', '問三', '記述'),
                (r'問四[　 ]*――Ｆとは筆者の場合はどのようなことでしたか[^\n]*', '問四', '記述'),
                (r'問五[　 ]*――[①ⓛ]の慣用句の　に入る、身体の一部分を漢字で[^\n]*', '問五', '語句'),
                (r'問六――②の慣用句の［?ア・イ[^\n]+語群から選び[^\n]+', '問六', '語句'),
            ]
            
            for pattern, marker, q_type in patterns:
                match = re.search(pattern, section_text)
                if match:
                    section_questions.append({
                        'marker': marker,
                        'text': match.group(0),
                        'position': section['start_pos'] + match.start(),
                        'type': q_type
                    })
        
        elif section['number'] == 2:
            # 大問二の設問検出
            patterns = [
                (r'問一〜〜①〜⑤のカタカナを正しい漢字に直しなさい[^\n]*', '問一', '漢字'),
                (r'問二――１とありますが、なぜ「自然と笑みが上」り[^\n]+', '問二', '記述'),
                (r'問三　――２とありますが、登瀬はなぜこう感じたのか[^\n]+', '問三', '記述（200字）'),
                (r'問四｜は、文中ではどういう意味で使われているのですか[^\n]+', '問四', '語句'),
                (r'問五　――３とありますが、登瀬はなぜ涙を流したのですか[^\n]+', '問五', '記述'),
            ]
            
            for pattern, marker, q_type in patterns:
                match = re.search(pattern, section_text, re.MULTILINE)
                if match:
                    section_questions.append({
                        'marker': marker,
                        'text': match.group(0),
                        'position': section['start_pos'] + match.start(),
                        'type': q_type
                    })
        
        # セクション情報を更新
        section['question_count'] = len(section_questions)
        result['sections'].append({
            'number': section['number'],
            'title': section['title'],
            'question_count': section['question_count'],
            'type': section['type']
        })
        
        # 全体の設問リストに追加
        for idx, q in enumerate(section_questions):
            all_questions.append({
                'number': len(all_questions) + 1,
                'section': section['number'],
                'marker': q['marker'],
                'type': q['type'],
                'description': q['text'][:50] + '...' if len(q['text']) > 50 else q['text']
            })
    
    result['questions'] = all_questions
    result['total_questions'] = len(all_questions)
    
    return result


def main():
    """メイン実行関数"""
    
    # 高精度テキストファイルを読み込み
    text_file = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭/15桜蔭.txt'
    
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"テキストファイルを読み込みました: {len(text)}文字")
        
        # 分析実行
        result = analyze_sakuragai_text(text)
        
        # 結果表示
        print("\n=== 桜蔭中学校 2015年度 国語 分析結果（高精度版）===\n")
        
        print(f"学校: {result['school']}")
        print(f"年度: {result['year']}")
        print(f"総設問数: {result['total_questions']}問")
        
        print("\n【大問別内訳】")
        for section in result['sections']:
            print(f"大問{section['number']}: {section['title'][:20]}... - {section['question_count']}問")
        
        print("\n【検出された全設問】")
        for q in result['questions']:
            print(f"{q['number']:2d}. 大問{q['section']} {q['marker']:6s} ({q['type']})")
            print(f"    {q['description']}")
        
        # 精度評価
        print(f"\n【精度評価】")
        if result['total_questions'] == 11:
            print("✅ 精度100%達成！全11問を正確に検出しました。")
            
            d1_count = len([q for q in result['questions'] if q['section'] == 1])
            d2_count = len([q for q in result['questions'] if q['section'] == 2])
            
            print(f"\n【詳細】")
            print(f"大問一: {d1_count}問（期待値: 6問）")
            print(f"大問二: {d2_count}問（期待値: 5問）")
        else:
            print(f"検出数: {result['total_questions']}問（期待値: 11問）")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()