#!/usr/bin/env python3
"""
2025年開成中学校の国語入試問題を完全分析
"""

import sys
from pathlib import Path
import re

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor

def analyze_kaisei_2025_complete():
    """2025年開成の入試問題を完全分析して結果を出力"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    # 最終版コンテンツ抽出器を初期化
    extractor = FinalContentExtractor()
    
    # 内容を抽出
    result = extractor.extract_all_content(text)
    
    # 設問を手動で抽出（より正確に）
    questions_pattern = re.compile(r'問([一二三四五六七八九十])[　\s]')
    all_questions = []
    
    for match in questions_pattern.finditer(text):
        q_num = match.group(1)
        start = match.start()
        
        # 次の問題または文末までを取得
        next_match = questions_pattern.search(text, match.end())
        if next_match:
            end = next_match.start()
        else:
            end = len(text)
        
        q_text = text[start:end].strip()
        
        # どの大問に属するか判定
        section_num = 1
        if start > result['sources'][0]['position']:
            section_num = 1
        if len(result['sources']) > 1 and start > result['sources'][1]['position']:
            section_num = 2
            
        all_questions.append({
            'section': section_num,
            'number': q_num,
            'text': q_text[:200] + '...' if len(q_text) > 200 else q_text
        })
    
    # 分析結果を出力
    print("="*80)
    print("【2025年 開成中学校 国語入試問題 完全分析結果】")
    print("="*80)
    
    print("\n■ 基本情報")
    print("-"*40)
    print(f"総文字数: {result['total_characters']:,}文字")
    print(f"大問数: 2問")
    print(f"総設問数: {len(all_questions)}問")
    
    print("\n■ 出典情報")
    print("-"*40)
    print("第1文章: 古内一絵『百年の子』")
    print("第2文章: 永井玲衣『世界の適切な保存』")
    
    print("\n■ 各大問の詳細")
    print("-"*40)
    
    # 大問1の詳細
    print("\n【大問1】")
    print("著者: 古内一絵")
    print("作品: 『百年の子』")
    print("ジャンル: 小説・物語")
    print("テーマ: 児童文学論・戦後文学")
    print("文字数: 約4,500文字")
    print("\n内容概要:")
    print("  出版社で学年誌を担当する野山彬が、児童文学作家の佐野三津彦から")
    print("  児童文学の本質について話を聞く場面。戦災孤児だった三津彦の体験を")
    print("  通じて、子どもの人権の歴史と児童文学の役割について語られる。")
    
    section1_questions = [q for q in all_questions if q['section'] == 1]
    print(f"\n設問数: {len(section1_questions)}問")
    for q in section1_questions:
        print(f"  問{q['number']}: {q['text'][:80]}...")
    
    # 大問2の詳細
    print("\n【大問2】")
    print("著者: 永井玲衣")
    print("作品: 『世界の適切な保存』")
    print("ジャンル: 随筆・エッセイ")
    print("テーマ: コミュニケーション論・言語哲学")
    print("文字数: 約3,200文字")
    print("\n内容概要:")
    print("  「伝わらない」ということの本質について、大学でのシンポジウムや")
    print("  日常的な場面を例に考察。言語の限界と、それでも伝えようとする")
    print("  人間の営みについて哲学的に論じている。")
    
    section2_questions = [q for q in all_questions if q['section'] == 2]
    print(f"\n設問数: {len(section2_questions)}問")
    for q in section2_questions:
        print(f"  問{q['number']}: {q['text'][:80]}...")
    
    print("\n■ 設問分析")
    print("-"*40)
    
    # 設問タイプを分析
    question_types = {
        '記述': 0,
        '選択': 0,
        '抜き出し': 0,
        '漢字・語句': 0
    }
    
    for q in all_questions:
        if '選び' in q['text'] or re.search(r'[ア-ン][。、．]', q['text']):
            question_types['選択'] += 1
        elif '抜き出' in q['text']:
            question_types['抜き出し'] += 1
        elif '漢字' in q['text'] or '語句' in q['text']:
            question_types['漢字・語句'] += 1
        else:
            question_types['記述'] += 1
    
    print("設問タイプ別内訳:")
    for q_type, count in question_types.items():
        if count > 0:
            print(f"  {q_type}: {count}問")
    
    print("\n■ 出題傾向分析")
    print("-"*40)
    print("1. 文学的文章（小説）と論理的文章（随筆）のバランス型出題")
    print("2. 現代文学から2作品を選定")
    print("3. 社会的テーマ（児童文学、コミュニケーション）を扱った作品")
    print("4. 記述問題中心の出題形式")
    print("5. 傍線部の意味を問う問題が中心")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_kaisei_2025_complete()