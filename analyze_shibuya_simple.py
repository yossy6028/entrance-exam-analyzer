#!/usr/bin/env python3
"""
渋谷教育学園渋谷中学校 15年度 国語問題分析（簡易版）
"""
import os
import re
from google.cloud import vision
from typing import List, Dict


def extract_text_from_pdf_direct(pdf_path: str) -> str:
    """PDFから直接Google Vision APIでテキスト抽出"""
    
    # Google Cloud Vision クライアントを初期化
    client = vision.ImageAnnotatorClient()
    
    # PDFファイルを読み込み
    with open(pdf_path, 'rb') as pdf_file:
        content = pdf_file.read()
    
    # Vision APIに送信するためのリクエストを作成
    # PDFの場合は各ページが個別の画像として処理される
    image = vision.Image(content=content)
    
    # テキスト検出を実行
    try:
        response = client.document_text_detection(
            image=image,
            image_context={'language_hints': ['ja']}
        )
        
        # 抽出されたテキストを取得
        text = response.full_text_annotation.text
        
        return text
        
    except Exception as e:
        print(f"Google Vision APIエラー: {e}")
        print("PDFが複数ページの場合、ページごとに処理が必要です")
        return ""


def analyze_shibuya_text(text: str) -> Dict:
    """渋渋のテキストを分析"""
    
    result = {
        'school': '渋谷教育学園渋谷中学校',
        'year': '15年度',
        'sections': [],
        'questions': [],
        'sources': []
    }
    
    # 大問のパターン
    section_patterns = [
        (r'[一二三四五六七八九十][\s　]*[、。．]', 'main_section'),
        (r'第[一二三四五六七八九十]問', 'main_section_alt'),
        (r'問題[一二三四五六七八九十]', 'main_section_alt2')
    ]
    
    # 設問のパターン
    question_patterns = [
        (r'問[一二三四五六七八九十0-9１-９]', 'question'),
        (r'[①②③④⑤⑥⑦⑧⑨⑩]', 'sub_question'),
        (r'\([1-9]\)', 'sub_question_alt'),
        (r'[ア-オ][\s　]*[、。．]', 'choice')
    ]
    
    # 大問を検出
    sections = []
    for pattern, pattern_type in section_patterns:
        matches = list(re.finditer(pattern, text))
        for match in matches:
            sections.append({
                'text': match.group(0),
                'position': match.start(),
                'type': pattern_type
            })
    
    # 位置でソート
    sections.sort(key=lambda x: x['position'])
    
    # 大問番号を割り当て
    section_num = 1
    for i, section in enumerate(sections):
        # 次の大問の位置を取得
        next_pos = sections[i + 1]['position'] if i + 1 < len(sections) else len(text)
        
        result['sections'].append({
            'number': section_num,
            'text': section['text'],
            'start_pos': section['position'],
            'end_pos': next_pos
        })
        section_num += 1
    
    # 各大問内の設問を検出
    question_num = 1
    for section in result['sections']:
        section_text = text[section['start_pos']:section['end_pos']]
        section_questions = []
        
        for pattern, q_type in question_patterns:
            matches = list(re.finditer(pattern, section_text))
            for match in matches:
                section_questions.append({
                    'number': question_num,
                    'section': section['number'],
                    'marker': match.group(0),
                    'type': q_type,
                    'position': section['start_pos'] + match.start()
                })
                question_num += 1
        
        # この大問の設問数を記録
        section['question_count'] = len(section_questions)
        result['questions'].extend(section_questions)
    
    result['total_questions'] = len(result['questions'])
    
    # 出典情報を探す
    source_patterns = [
        r'（([^「）]+)「([^」]+)」）',
        r'（([^『）]+)『([^』]+)』）',
        r'（([^）]+)）[\s　]*$'  # 文末の括弧
    ]
    
    for pattern in source_patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        for match in matches:
            if len(match.groups()) >= 2:
                result['sources'].append({
                    'author': match.group(1).strip(),
                    'title': match.group(2).strip() if len(match.groups()) > 1 else None,
                    'full_text': match.group(0)
                })
    
    return result


def main():
    """メイン実行関数"""
    
    pdf_path = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf'
    
    print("=== 渋谷教育学園渋谷中学校 15年度 国語問題分析 ===\n")
    
    # まずPDFの最初のページだけ処理を試みる
    print("PDFの分析を開始します...")
    print("注意: Google Vision APIはPDF全体を一度に処理できない場合があります")
    
    # 簡易的な分析
    print("\n【分析方法】")
    print("1. 高精度テキストファイルがないため、概要分析のみ実施")
    print("2. 詳細な分析には以下が必要です:")
    print("   - bunkoOCR等でテキストファイルを作成")
    print("   - またはPDFを画像に変換してから処理")
    
    # 過去の渋渋の傾向を表示
    print("\n【渋谷教育学園渋谷中学校の一般的な出題傾向】")
    print("- 大問数: 通常2〜3問")
    print("- 総設問数: 10〜15問程度")
    print("- 出題内容:")
    print("  - 説明的文章（論説文・随筆）")
    print("  - 文学的文章（小説・物語）")
    print("  - 漢字・語句問題")
    print("  - 記述問題が多い")
    
    # 他の年度のテキストファイルから傾向を分析
    print("\n【参考: 他年度の構成】")
    other_years = ['21', '22', '23', '24', '25']
    
    for year in other_years:
        txt_path = f'/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/{year}渋渋.txt'
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
                result = analyze_shibuya_text(text)
                
                print(f"\n{year}年度: 大問{len(result['sections'])}個, 設問{result['total_questions']}問")
                if result['sources']:
                    print(f"  出典: {len(result['sources'])}作品")
                    for source in result['sources'][:2]:  # 最初の2つ
                        if source.get('author'):
                            print(f"    - {source['author']}")


if __name__ == "__main__":
    main()