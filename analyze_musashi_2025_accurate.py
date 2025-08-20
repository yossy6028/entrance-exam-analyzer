#!/usr/bin/env python3
"""
武蔵中学校2025年国語問題の正確な形式分析
選択式・抜き出し・記述の正確な判定基準による再分析
"""
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json


class AccurateQuestionAnalyzer:
    """正確な問題形式判定クラス"""
    
    def __init__(self):
        # 選択式の判定パターン
        self.selection_patterns = [
            r'[ア-オ]\s*[から選び|から一つ選|を選び]',
            r'[(（][ア-オ][)）]\s*から',
            r'記号で答え',
            r'最も.*ものを.*選び',
            r'一つ選び'
        ]
        
        # 抜き出しの判定パターン  
        self.extraction_patterns = [
            r'抜き出し',
            r'書き抜き',
            r'本文中から.*探し',
            r'文中から.*見つけ'
        ]
        
        # 記述タイプの判定パターン
        self.description_types = {
            '言い換え': [r'どういうこと', r'どのようなこと'],
            '理由': [r'なぜ', r'理由', r'原因'],
            '心情説明': [r'どのような気持ち', r'心情', r'感情'],
            '指示語': [r'それ.*何', r'これ.*何', r'指すもの'],
            '違いの記述': [r'どのように違', r'違い'],
            '変化の記述': [r'どのように変化', r'変化']
        }
        
        # 字数指定パターン
        self.char_limit_pattern = r'([0-9０-９]+)\s*字'
        
    def analyze_question(self, question_text: str) -> Dict:
        """個別の問題を分析"""
        result = {
            'type': None,
            'subtype': None,
            'char_limit': None,
            'has_choices': False
        }
        
        # 1. 選択式かチェック
        for pattern in self.selection_patterns:
            if re.search(pattern, question_text):
                result['type'] = '選択式'
                # 選択肢をチェック
                if re.search(r'[ア-オ]', question_text):
                    result['has_choices'] = True
                return result
        
        # 2. 抜き出しかチェック
        for pattern in self.extraction_patterns:
            if re.search(pattern, question_text):
                result['type'] = '抜き出し'
                # 字数指定をチェック
                char_match = re.search(self.char_limit_pattern, question_text)
                if char_match:
                    result['char_limit'] = int(char_match.group(1))
                return result
        
        # 3. 記述式と判定し、サブタイプを特定
        result['type'] = '記述式'
        
        # サブタイプを判定
        for subtype, patterns in self.description_types.items():
            for pattern in patterns:
                if re.search(pattern, question_text):
                    result['subtype'] = subtype
                    break
            if result['subtype']:
                break
        
        # 字数指定をチェック
        char_match = re.search(self.char_limit_pattern, question_text)
        if char_match:
            result['char_limit'] = int(char_match.group(1))
        
        return result


def analyze_musashi_2025_accurate():
    """武蔵中2025年の正確な分析"""
    
    # ファイルパス
    text_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/2025年武蔵中学校問題_国語.ocr.txt"
    
    print("=" * 70)
    print("武蔵中学校 2025年 国語問題 正確な形式分析")
    print("=" * 70)
    print(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # テキスト読み込み
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 問題を手動で抽出（OCRから確認できる問題）
    questions = [
        {
            'number': '問一',
            'text': '二重傍線部A~Cの語句の本文中での意味として最もふさわしいものを、それぞれ(ア)~(エ)から一つ選び、記号で答えなさい',
            'sub_questions': 3  # A, B, C
        },
        {
            'number': '問二(1)',
            'text': '「それ」とは何ですか。'
        },
        {
            'number': '問二(2)', 
            'text': '「私」が「そこのところが大切なところだと思う」のはなぜですか。'
        },
        {
            'number': '問三',
            'text': '「飼育係の『と思う』は学問する人の態度をもって語られている」とあるが、どういうことですか。'
        },
        {
            'number': '問四',
            'text': '「私はチンパにつばきされたのだが、それは同胞から頂戴したつばき同然で、はなはだ心たいらかでない」とあるが、それはどういうことですか。'
        },
        {
            'number': '問五',
            'text': '「そのまっ黒な長い手はかなしい」とあるが、ゴリラの手を「私」が「かなしい」と感じる理由として最も適当でないものを一つ選び、記号で答えなさい。'
        },
        {
            'number': '問六',
            'text': '「攻撃というより防禦だと思う」とあるが、どういうことですか。'
        },
        {
            'number': '問七',
            'text': '「そのゆえに、ビルの淋しさはずばりとわかってもらえたのである」とあるが、どういうことですか。'
        },
        {
            'number': '問八',
            'text': '次の各文のカタカナを漢字に直しなさい。'
        }
    ]
    
    # 分析実行
    analyzer = AccurateQuestionAnalyzer()
    results = []
    
    for q in questions:
        analysis = analyzer.analyze_question(q['text'])
        analysis['number'] = q['number']
        
        # 問一は3つの小問があるため特別処理
        if q['number'] == '問一':
            for i in range(q['sub_questions']):
                sub_analysis = analysis.copy()
                sub_analysis['number'] = f"問一({chr(65+i)})"  # A, B, C
                results.append(sub_analysis)
        else:
            results.append(analysis)
    
    # 集計
    type_counts = {}
    subtype_counts = {}
    char_limits = []
    
    for r in results:
        # メインタイプ集計
        if r['type']:
            type_counts[r['type']] = type_counts.get(r['type'], 0) + 1
        
        # サブタイプ集計
        if r['subtype']:
            subtype_counts[r['subtype']] = subtype_counts.get(r['subtype'], 0) + 1
        
        # 字数制限集計
        if r['char_limit']:
            char_limits.append(r['char_limit'])
    
    # 結果表示
    print("【問題形式分析結果】\n")
    print("=" * 50)
    print("問題タイプ別集計:")
    print("=" * 50)
    
    total = len(results)
    for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100)
        bar = "■" * int(percentage / 5)
        print(f"{type_name:10s}: {count:2d}問 ({percentage:5.1f}%) {bar}")
    
    print(f"\n総問題数: {total}問")
    
    print("\n" + "=" * 50)
    print("記述式の詳細分類:")
    print("=" * 50)
    
    for subtype, count in sorted(subtype_counts.items()):
        print(f"  {subtype}: {count}問")
    
    if char_limits:
        print(f"\n字数指定のある問題: {len(char_limits)}問")
        print(f"  指定字数: {char_limits}")
    
    print("\n" + "=" * 50)
    print("個別問題の詳細:")
    print("=" * 50)
    
    for r in results:
        print(f"\n{r['number']}:")
        print(f"  タイプ: {r['type']}")
        if r['subtype']:
            print(f"  サブタイプ: {r['subtype']}")
        if r['char_limit']:
            print(f"  字数指定: {r['char_limit']}字")
    
    # 正確な結果のサマリー
    print("\n" + "=" * 70)
    print("【分析サマリー】")
    print("=" * 70)
    print(f"✅ 選択式: {type_counts.get('選択式', 0)}問のみ")
    print(f"✅ 記述式: {type_counts.get('記述式', 0)}問（大部分）")
    print(f"✅ 抜き出し: {type_counts.get('抜き出し', 0)}問")
    print(f"✅ 漢字: 1問（問八）")
    
    print("\n【重要な発見】")
    print("・武蔵中2025年は記述中心の出題")
    print("・選択式は非常に少ない（問一と問五のみ）")
    print("・記述式は「言い換え」「理由」タイプが中心")
    
    # JSON保存
    output_data = {
        'school': '武蔵中学校',
        'year': 2025,
        'analysis_date': datetime.now().isoformat(),
        'total_questions': total,
        'type_distribution': type_counts,
        'subtype_distribution': subtype_counts,
        'char_limits': char_limits,
        'detailed_results': results
    }
    
    output_path = Path("/Users/yoshiikatsuhiko/Desktop/02_開発 (Development)/entrance_exam_analyzer")
    json_path = output_path / "武蔵中2025_正確な形式分析.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析結果を保存: {json_path}")
    
    return output_data


if __name__ == "__main__":
    analyze_musashi_2025_accurate()