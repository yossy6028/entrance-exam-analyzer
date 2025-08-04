#!/usr/bin/env python3
"""
武蔵14-25.txtの正確な分析
年度の開始位置を正しく特定
"""
import re
from pathlib import Path
from collections import defaultdict

def correct_analysis():
    """正確な分析"""
    
    file_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/武蔵14-25.txt")
    
    # ファイル読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"総文字数: {len(content):,}\n")
    
    # 年度の開始位置を特定（最初の出現のみ）
    # パターン: 武蔵の後に14, 15などの年度が初めて出現する位置
    year_starts = {}
    
    # まず、可能性のある年度を探す
    for year in range(14, 26):  # 2014-2025
        year_str = str(year)
        
        # 武蔵XX形式を探す
        pattern1 = f'武蔵{year_str}'
        match1 = re.search(pattern1, content)
        
        # 武蔵\n...\nXX形式を探す（最初の出現）
        pattern2 = f'武蔵\\s*\\n[^\\n]*\\n+{year_str}\\s*\\n'
        match2 = re.search(pattern2, content)
        
        if match1 or match2:
            # 最も早い位置を採用
            positions = []
            if match1:
                positions.append(match1.start())
            if match2:
                positions.append(match2.start())
            
            if positions:
                year_starts[f"20{year_str}"] = min(positions)
    
    # 年度順にソート
    sorted_years = sorted(year_starts.items(), key=lambda x: x[1])
    
    print("=== 検出された年度と開始位置 ===")
    for year, pos in sorted_years:
        print(f"{year}年: 位置 {pos}")
    
    print("\n=== 年度ごとの分析 ===\n")
    
    results = []
    for i, (year, start_pos) in enumerate(sorted_years):
        # 次の年度の開始位置まで、またはファイル末尾まで
        if i < len(sorted_years) - 1:
            end_pos = sorted_years[i + 1][1]
        else:
            end_pos = len(content)
        
        year_text = content[start_pos:end_pos]
        
        print(f"--- {year}年 ---")
        print(f"文字数: {len(year_text):,}")
        
        # 大問を検出（「その一」「その二」など）
        section_patterns = [
            r'その[一二三四五六七八九十]+（[^）]*枚のうち）',
            r'国\s*語\s*その[一二三四五六七八九十]+',
            r'[一二三四五六七八九十]\s*（[^）]*枚のうち）'
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, year_text)
            sections.extend(matches)
        
        # 重複を除去して大問数を推定
        unique_sections = []
        for s in sections:
            if '一' in s and '一' not in [us for us in unique_sections]:
                unique_sections.append('一')
            elif '二' in s and '二' not in [us for us in unique_sections]:
                unique_sections.append('二')
            elif '三' in s and '三' not in [us for us in unique_sections]:
                unique_sections.append('三')
        
        estimated_sections = max(len(unique_sections), 1)
        print(f"大問数: {estimated_sections} (推定)")
        
        # 設問を検出
        question_patterns = [
            r'問[一二三四五六七八九十]+',
            r'問\d+',
            r'〔[一二三四五六七八九十]+〕',
            r'〔\d+〕'
        ]
        
        questions = []
        for pattern in question_patterns:
            matches = re.findall(pattern, year_text)
            questions.extend(matches)
        
        # 重複を除去
        unique_questions = list(set(questions))
        print(f"設問数: {len(unique_questions)}")
        
        # 設問タイプを推定
        question_types = {
            '記述': len(re.findall(r'(?:説明|述べ|書き|答え)なさい', year_text)),
            '選択': len(re.findall(r'(?:選び|選べ|選択)なさい', year_text)),
            '漢字・語句': len(re.findall(r'(?:漢字|読み|語句)', year_text)),
            '抜き出し': len(re.findall(r'(?:抜き出|書き抜|探し)', year_text))
        }
        
        print("設問タイプ:")
        for q_type, count in question_types.items():
            if count > 0:
                print(f"  {q_type}: {count}問（推定）")
        
        # 出典を探す
        source_patterns = [
            r'（([^）]+の文による)）',
            r'（([^）]+著)）',
            r'（([^）]+作)）',
            r'『([^』]+)』'
        ]
        
        sources = []
        for pattern in source_patterns:
            matches = re.findall(pattern, year_text)
            sources.extend(matches)
        
        if sources:
            print("出典候補:")
            for source in sources[:3]:  # 最初の3つ
                print(f"  {source}")
        
        print()
        
        results.append({
            'year': year,
            'characters': len(year_text),
            'sections': estimated_sections,
            'questions': len(unique_questions),
            'question_types': question_types,
            'sources': sources[:3] if sources else []
        })
    
    # サマリー
    print("\n=== サマリー ===")
    print("年度\t文字数\t大問数\t設問数")
    print("-" * 40)
    for r in results:
        print(f"{r['year']}\t{r['characters']:,}\t{r['sections']}\t{r['questions']}")
    
    return results

if __name__ == "__main__":
    correct_analysis()