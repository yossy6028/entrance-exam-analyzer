#!/usr/bin/env python3
"""
武蔵14-25.txtの簡易分析
"""
import re
from pathlib import Path

def simple_analysis():
    """簡易的な分析"""
    
    file_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/武蔵14-25.txt")
    
    # ファイル読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"総文字数: {len(content):,}\n")
    
    # 年度マーカーを探す（武蔵の後に改行があるパターン）
    # パターン: 武蔵\n\n何か\n\n14 のような形式
    pattern = r'武蔵\s*\n[^\n]*\n+(\d{2})\s*\n'
    matches = list(re.finditer(pattern, content))
    
    print(f"見つかった年度マーカー: {len(matches)}個\n")
    
    # 各年度の位置を表示
    year_positions = []
    for match in matches:
        year = match.group(1)
        pos = match.start()
        year_positions.append((pos, f"20{year}"))
        
        # 周辺のテキストを表示
        snippet = content[pos:pos+200].replace('\n', '\\n')
        print(f"20{year}年 (位置: {pos})")
        print(f"  テキスト: {snippet[:100]}...")
        print()
    
    # 年度ごとに分割
    print("\n=== 年度ごとの文字数 ===")
    for i, (pos, year) in enumerate(year_positions):
        if i < len(year_positions) - 1:
            next_pos = year_positions[i + 1][0]
            year_text = content[pos:next_pos]
        else:
            year_text = content[pos:]
        
        print(f"{year}年: {len(year_text):,}文字")
        
        # 大問マーカーを探す
        section_markers = re.findall(r'[一二三四五六七八九十]\s*（[^）]*枚のうち）', year_text)
        print(f"  大問マーカー: {len(section_markers)}個")
        
        # 設問を探す（簡易的に）
        questions = re.findall(r'問[一二三四五六七八九十\d]+', year_text)
        print(f"  設問マーカー: {len(questions)}個")
        
        # 出典らしきものを探す
        sources = re.findall(r'（([^）]+(?:の文による|著|作))）', year_text)
        if sources:
            print(f"  出典候補: {sources[:2]}...")
        
        print()

if __name__ == "__main__":
    simple_analysis()