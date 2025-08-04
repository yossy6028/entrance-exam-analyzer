#!/usr/bin/env python3
"""タイトル設定問題のデバッグ用スクリプト"""

import re
from pathlib import Path

def debug_shibuya_2015_title_setting(text_file="15渋渋_bunko.txt"):
    """渋渋2015年のタイトル設定処理をデバッグ"""
    
    print("🔍 タイトル設定デバッグ開始")
    
    # テキスト読み込み
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 テキスト読み込み完了: {len(text)}文字")
    
    # 大問検出（analyze_shibuya_2015.pyから抜粋）
    problem_patterns = [
        (r'次の文章を読んで.*?問いに答えなさい', '文章読解'),
        (r'文章を読んで.*?問いに答えなさい', '文章読解'),
        (r'以下の文章を読んで.*?問いに答えなさい', '文章読解'),
        (r'【.*?】.*?問いに答えなさい', '文章読解'),
    ]
    
    sections = []
    text_lines = text.split('\n')
    
    for i, line in enumerate(text_lines):
        for pattern, genre in problem_patterns:
            if re.search(pattern, line):
                sections.append({
                    'section_num': len(sections) + 1,
                    'genre': genre,
                    'start_pos': text.find(line),
                    'line_num': i + 1,
                    'line_content': line.strip()
                })
                print(f"✅ 大問{len(sections)}を検出: {genre}")
                print(f"   位置: {text.find(line)} (行{i+1})")
                print(f"   内容: {line.strip()[:100]}...")
                break
    
    print(f"\n検出された大問数: {len(sections)}")
    
    # 出典抽出（analyze_shibuya_2015.pyから抜粋）
    print(f"\n📚 出典情報の抽出")
    
    source_patterns = [
        r'（([^）]{1,50}『[^』]{1,100}』[^）]{0,20})）',  # 日本語括弧、長さ制限
        r'（([^）]{1,50}「[^」]{1,100}」[^）]{0,20})）',   # 日本語括弧、引用符
        r'\(([^)]{1,50}『[^』]{1,100}』[^)]{0,20})\)',  # 半角括弧
    ]
    
    sources = []
    for pattern in source_patterns:
        for match in re.finditer(pattern, text):
            source_text = match.group(1)
            if len(source_text) > 150:
                continue
            
            if '『' in source_text:
                parts = source_text.split('『')
                if len(parts) >= 2:
                    author = parts[0].strip()
                    title = parts[1].split('』')[0].strip()
                    if 1 <= len(author) <= 20 and 1 <= len(title) <= 50:
                        sources.append({
                            'author': author,
                            'title': title,
                            'full': source_text,
                            'position': match.start()
                        })
    
    print(f"抽出された出典数: {len(sources)}")
    for i, source in enumerate(sources, 1):
        print(f"  {i}. 位置{source['position']}: {source['author']} 『{source['title']}』")
    
    # 大問と出典のマッピング（analyze_shibuya_2015.pyから抜粋）
    print(f"\n🔗 大問と出典のマッピング")
    
    for section in sections:
        print(f"\n大問{section['section_num']} (位置: {section['start_pos']}):")
        
        # この大問より後にある出典を検索
        section_sources = [s for s in sources if s['position'] > section['start_pos']]
        
        print(f"  候補出典数: {len(section_sources)}")
        for i, s in enumerate(section_sources):
            distance = s['position'] - section['start_pos']
            print(f"    {i+1}. 距離{distance}: {s['author']} 『{s['title']}』")
        
        if section_sources:
            # 最も近い出典を選択
            closest_source = min(section_sources, key=lambda x: x['position'] - section['start_pos'])
            section['author'] = closest_source['author']
            section['title'] = closest_source['title']
            
            distance = closest_source['position'] - section['start_pos']
            print(f"  → 選択: {closest_source['author']} 『{closest_source['title']}』 (距離: {distance})")
        else:
            section['author'] = '不明'
            section['title'] = '不明'
            print(f"  → 該当する出典が見つかりません")
    
    # 最終結果
    print(f"\n📊 最終結果")
    for section in sections:
        print(f"大問{section['section_num']}:")
        print(f"  著者: {section.get('author', '未設定')}")
        print(f"  作品: {section.get('title', '未設定')}")
    
    # Excel形式で出力する場合のデータ構造
    print(f"\n📋 Excel出力データ構造")
    section_stats = []
    for section in sections:
        stat = {
            '大問': f"大問{section['section_num']}",
            '文章ジャンル': section['genre'],
            'テーマ': '現代文',  # 簡略化
            '出典_著者': section.get('author', '不明'),
            '出典_作品': section.get('title', '不明'),
            '設問数': 0,  # 簡略化
            '推定文字数': 1000,  # 簡略化
            '問題タイプ構成': '記述・選択'  # 簡略化
        }
        section_stats.append(stat)
        print(f"  {stat}")
    
    # 特に大問1のタイトルが正しく設定されているかチェック
    print(f"\n🎯 大問1タイトル設定チェック")
    if len(sections) > 0:
        section1 = sections[0]
        title = section1.get('title', '未設定')
        author = section1.get('author', '未設定')
        
        if 'フェアネス' in title or '朱喜哲' in author:
            print(f"✅ 大問1のタイトル設定は正常です")
            print(f"   著者: {author}")
            print(f"   作品: {title}")
        else:
            print(f"❌ 大問1のタイトル設定に問題があります")
            print(f"   著者: {author}")
            print(f"   作品: {title}")
            print(f"   期待: 朱喜哲 / フェアネスを含む作品名")
    
    return sections, sources

if __name__ == "__main__":
    sections, sources = debug_shibuya_2015_title_setting()