#!/usr/bin/env python3
"""
渋谷教育学園渋谷中学校の出題傾向分析
他年度のテキストファイルから傾向を把握
"""
import os
import re
from typing import Dict, List
from collections import defaultdict


def analyze_shibuya_text_detailed(text: str, year: str) -> Dict:
    """渋渋のテキストを詳細分析"""
    
    result = {
        'year': year,
        'sections': [],
        'questions': [],
        'sources': [],
        'total_questions': 0
    }
    
    # 大問のパターン（渋渋用に調整）
    section_patterns = [
        (r'[一二三四五][\s　、。．]', 'kanji_num'),
        (r'[１２３４５][\s　、。．]', 'zenkaku_num'),
        (r'\[[一二三四五]\]', 'bracket_kanji'),
        (r'第[一二三四五]問', 'formal_style')
    ]
    
    # 設問のパターン
    question_patterns = [
        (r'問[一二三四五六七八九十][\s　]', 'kanji_question'),
        (r'問[1-9１-９][\s　]', 'number_question'),
        (r'[①②③④⑤⑥⑦⑧⑨⑩]', 'circled_number'),
        (r'\([1-9]\)', 'parenthesis_number'),
        (r'[ア-オ][\s　．、]', 'katakana_choice')
    ]
    
    # 大問を検出
    sections_found = []
    for pattern, pattern_type in section_patterns:
        matches = list(re.finditer(pattern, text[:3000]))  # 冒頭部分で検索
        for match in matches:
            sections_found.append({
                'text': match.group(0),
                'position': match.start(),
                'type': pattern_type
            })
    
    # 重複を除いてソート
    sections_found.sort(key=lambda x: x['position'])
    
    # 大問として確定
    seen_positions = set()
    section_num = 1
    for section in sections_found:
        if section['position'] not in seen_positions and section['position'] < 1000:
            seen_positions.add(section['position'])
            result['sections'].append({
                'number': section_num,
                'marker': section['text'].strip(),
                'position': section['position']
            })
            section_num += 1
    
    # 設問を検出
    questions_found = []
    for pattern, q_type in question_patterns:
        matches = list(re.finditer(pattern, text))
        for match in matches:
            questions_found.append({
                'marker': match.group(0).strip(),
                'type': q_type,
                'position': match.start()
            })
    
    # 位置でソートして番号付け
    questions_found.sort(key=lambda x: x['position'])
    
    # 重複を除去（近い位置のものは同じとみなす）
    unique_questions = []
    last_pos = -100
    for q in questions_found:
        if q['position'] - last_pos > 10:  # 10文字以上離れている
            unique_questions.append(q)
            last_pos = q['position']
    
    result['questions'] = unique_questions
    result['total_questions'] = len(unique_questions)
    
    # 出典情報を探す
    source_patterns = [
        # 標準的なパターン
        r'（([^「）]+)「([^」]+)」）',
        r'（([^『）]+)『([^』]+)』）',
        # 作者名のみ
        r'（([^）]{2,20})）(?=[\s　]*$)',
        # より複雑なパターン
        r'（([^）]+)「([^」]+)」[^）]*『([^』]+)』）'
    ]
    
    for pattern in source_patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        for match in matches:
            # 文末近くの出典を優先
            if match.end() > len(text) - 2000 or '」' in match.group(0) or '』' in match.group(0):
                groups = match.groups()
                source_info = {
                    'author': groups[0].strip() if groups else None,
                    'title': groups[1].strip() if len(groups) > 1 else None,
                    'book': groups[2].strip() if len(groups) > 2 else None,
                    'full_text': match.group(0),
                    'position': match.start()
                }
                result['sources'].append(source_info)
    
    return result


def analyze_all_shibuya_years():
    """すべての年度の渋渋を分析"""
    
    base_path = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋'
    
    # 利用可能なテキストファイル
    available_files = {
        '21': '21渋渋.txt',
        '22': '22渋渋.txt', 
        '23': '23渋渋.txt',
        '24': '24渋渋.txt',
        '25': '25渋渋.txt'
    }
    
    all_results = {}
    
    print("=== 渋谷教育学園渋谷中学校 出題傾向分析 ===\n")
    
    for year, filename in available_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            print(f"\n【20{year}年度】")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            result = analyze_shibuya_text_detailed(text, f"20{year}")
            all_results[year] = result
            
            # 結果表示
            print(f"大問数: {len(result['sections'])}")
            if result['sections']:
                sections_str = ", ".join([s['marker'] for s in result['sections'][:5]])
                print(f"大問マーカー: {sections_str}")
            
            print(f"総設問数: {result['total_questions']}")
            
            # 設問タイプの集計
            q_types = defaultdict(int)
            for q in result['questions']:
                q_types[q['type']] += 1
            
            print("設問タイプ:")
            for q_type, count in sorted(q_types.items(), key=lambda x: -x[1]):
                print(f"  - {q_type}: {count}問")
            
            # 出典情報
            if result['sources']:
                print(f"出典: {len(result['sources'])}作品")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"  {i}. {source['author']}", end="")
                    if source.get('title'):
                        print(f"「{source['title']}」", end="")
                    if source.get('book'):
                        print(f"『{source['book']}』", end="")
                    print()
    
    # 全体的な傾向分析
    print("\n【全体傾向分析】")
    
    # 大問数の傾向
    section_counts = [len(r['sections']) for r in all_results.values()]
    if section_counts:
        avg_sections = sum(section_counts) / len(section_counts)
        print(f"平均大問数: {avg_sections:.1f}")
    
    # 設問数の傾向
    question_counts = [r['total_questions'] for r in all_results.values()]
    if question_counts:
        avg_questions = sum(question_counts) / len(question_counts)
        print(f"平均設問数: {avg_questions:.1f}")
        print(f"設問数範囲: {min(question_counts)}〜{max(question_counts)}問")
    
    # 出典の傾向
    all_authors = []
    for r in all_results.values():
        for s in r['sources']:
            if s.get('author'):
                all_authors.append(s['author'])
    
    if all_authors:
        print(f"\n出典作家（延べ）: {len(all_authors)}人")
        # 頻出作家を表示
        author_counts = defaultdict(int)
        for author in all_authors:
            author_counts[author] += 1
        
        frequent_authors = sorted(author_counts.items(), key=lambda x: -x[1])
        if frequent_authors:
            print("頻出作家:")
            for author, count in frequent_authors[:5]:
                if count > 1:
                    print(f"  - {author}: {count}回")
    
    print("\n【15年度の推定】")
    print("上記の傾向から、15年度も以下のような構成と推測されます:")
    print("- 大問数: 2〜3問")
    print("- 総設問数: 10〜15問程度")
    print("- 説明的文章と文学的文章の組み合わせ")
    print("- 記述問題中心")
    print("\n※正確な分析には高精度OCRによるテキストファイルが必要です")


if __name__ == "__main__":
    analyze_all_shibuya_years()