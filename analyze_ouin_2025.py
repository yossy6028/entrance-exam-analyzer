#!/usr/bin/env python3
"""
2025年桜蔭中学校の国語入試問題を完全分析
"""

import sys
from pathlib import Path
import re

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor
from modules.flexible_excel_formatter import FlexibleExcelFormatter


def analyze_ouin_2025():
    """2025年桜蔭の入試問題を分析"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭/25桜蔭.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*80)
    print("【2025年 桜蔭中学校 国語入試問題 完全分析】")
    print("="*80)
    
    # コンテンツ抽出器を初期化
    extractor = FinalContentExtractor()
    
    # 内容を抽出
    result = extractor.extract_all_content(text)
    
    # テキストの最初の部分を確認
    print("\n■ テキスト冒頭確認（最初の500文字）")
    print("-"*40)
    preview = text[:500].replace('\n', ' ')
    print(preview)
    
    print("\n■ 基本情報")
    print("-"*40)
    print(f"総文字数: {result['total_characters']:,}文字")
    print(f"検出された大問数: {len(result['sections'])}問")
    
    # 出典情報の表示
    print("\n■ 検出された出典")
    print("-"*40)
    if result['sources']:
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. 著者: {source['author']}")
            print(f"   作品: {source['work']}")
            print(f"   位置: {source['position']}")
    else:
        print("出典が自動検出できませんでした。手動で確認します...")
        
        # 手動でパターンを探す
        print("\n手動検索中...")
        
        # パターン1: （著者名『作品名』）
        pattern1 = re.compile(r'[（(]([^）)]{2,20})[）)]')
        matches1 = pattern1.findall(text[-1000:])  # 最後の1000文字を検索
        if matches1:
            print("括弧内の情報:")
            for match in matches1[-5:]:  # 最後の5つ
                print(f"  - {match}")
        
        # パターン2: 『作品名』
        pattern2 = re.compile(r'[『「]([^』」]{2,30})[』」]')
        matches2 = pattern2.findall(text)
        if matches2:
            print("\n作品名候補:")
            for match in set(matches2):  # 重複を除去
                if len(match) > 5:  # 短すぎるものは除外
                    print(f"  - 『{match}』")
    
    # 設問の検出
    print("\n■ 設問分析")
    print("-"*40)
    
    # 設問パターンを手動で検索
    question_patterns = [
        (r'問[一二三四五六七八九十]', 'kanji'),
        (r'問[１-９]', 'number'),
        (r'[一二三四五六七八九十][、\s]', 'section'),
    ]
    
    all_questions = []
    for pattern_str, q_type in question_patterns:
        pattern = re.compile(pattern_str)
        for match in pattern.finditer(text):
            all_questions.append({
                'type': q_type,
                'text': match.group(),
                'position': match.start()
            })
    
    # 位置でソート
    all_questions.sort(key=lambda x: x['position'])
    
    print(f"検出された設問マーカー: {len(all_questions)}個")
    if all_questions[:10]:  # 最初の10個を表示
        print("\n最初の設問マーカー:")
        for q in all_questions[:10]:
            context = text[q['position']:q['position']+50].replace('\n', ' ')
            print(f"  {q['text']}: {context}...")
    
    # 各セクションの詳細
    print("\n■ 各大問の詳細分析")
    print("-"*40)
    
    for i, section in enumerate(result['sections'], 1):
        print(f"\n【大問{i}】")
        print(f"文字数: {section['characters']:,}文字")
        print(f"ジャンル: {section['genre']}")
        print(f"テーマ: {section['theme']}")
        
        if section.get('source'):
            print(f"著者: {section['source']['author']}")
            print(f"作品: {section['source']['work']}")
        else:
            print("出典: 検出できず")
        
        print(f"設問数: {len(section['questions'])}問")
    
    # 設問タイプの集計
    print("\n■ 設問タイプ別集計")
    print("-"*40)
    if result.get('question_types'):
        for q_type, count in result['question_types'].items():
            if count > 0:
                print(f"{q_type}: {count}問")
    
    # Excelフォーマッターで保存準備
    print("\n■ Excel保存用データ準備")
    print("-"*40)
    
    formatter = FlexibleExcelFormatter()
    
    # 追加情報
    additional_info = {
        '記述_最大字数': None,
        '記述_最小字数': None,
        '図表_使用有無': '要確認',
        '詩歌_有無': 'なし',
        '出題傾向': '要分析',
        '特記事項': '2025年度桜蔭中学校入試問題'
    }
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="桜蔭中学校",
        year=2025,
        analysis_result=result,
        ocr_filename="25桜蔭.txt",
        additional_info=additional_info
    )
    
    print("Excel保存用データを準備しました")
    print(f"  学校名: 桜蔭中学校")
    print(f"  年度: 2025")
    print(f"  総文字数: {row_data.get('総文字数', 0):,}文字")
    print(f"  大問数: {row_data.get('大問数', 0)}")
    
    # 保存するか確認
    print("\n" + "="*80)
    print("※ Excelに保存する場合は save_ouin_2025_to_excel.py を実行してください")
    
    return result, row_data


if __name__ == "__main__":
    analyze_ouin_2025()