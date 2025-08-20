#!/usr/bin/env python3
"""
拡張版コンテンツ抽出機能のテスト
"""

import json
from pathlib import Path
from modules.enhanced_content_extractor import EnhancedContentExtractor
from modules.content_type_formatter import ContentTypeFormatter


def test_with_seiko():
    """聖光学院のデータで拡張機能をテスト"""
    
    print("="*60)
    print("拡張版コンテンツ抽出機能のテスト")
    print("="*60)
    
    # 拡張版抽出器を作成
    extractor = EnhancedContentExtractor()
    
    # テスト1: OCRテキストでの検証
    print("\n【テスト1: OCRテキストでの設問連続性チェック】")
    
    ocr_file = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/2025過去問/聖光25.txt"
    
    with open(ocr_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 検証付きで分析
    result = extractor.analyze_with_validation(text, school_name="聖光学院中学校")
    
    # レポートを表示
    print(result['report'])
    
    # テスト2: PDFレイアウト解析（PDFが存在する場合）
    print("\n【テスト2: PDFレイアウト解析】")
    
    pdf_paths = [
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/kokugo-mondai (1).pdf",
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/聖光学院/聖光25.pdf"
    ]
    
    pdf_file = None
    for path in pdf_paths:
        if Path(path).exists():
            pdf_file = path
            break
    
    if pdf_file:
        print(f"PDFファイル: {pdf_file}")
        
        try:
            # PDFから直接抽出
            pdf_result = extractor.extract_from_pdf(pdf_file)
            
            # PDFレイアウト情報を表示
            if 'layout_info' in pdf_result:
                print(f"\nPDFレイアウト解析結果:")
                print(f"  総ページ数: {pdf_result['layout_info']['total_pages']}")
                for page in pdf_result['layout_info']['page_layouts']:
                    print(f"  ページ{page['page']+1}: {page['layout']}レイアウト")
            
            # 結果を保存
            with open('enhanced_result.json', 'w', encoding='utf-8') as f:
                json.dump(pdf_result, f, ensure_ascii=False, indent=2)
            
            print("\n✅ PDFレイアウト解析成功")
            
        except Exception as e:
            print(f"⚠️  PDFレイアウト解析エラー: {e}")
    else:
        print("PDFファイルが見つかりません")
    
    # テスト3: 新形式でのExcel出力
    print("\n【テスト3: 改良後のExcel出力】")
    
    formatter = ContentTypeFormatter()
    formatted_data = formatter.format_data(
        result,
        school_name='聖光学院中学校',
        year=2025
    )
    
    # 表示
    formatter.display_formatted_data(formatted_data)
    
    # 保存
    formatter.save_to_excel(formatted_data, sheet_name='聖光学院中学校')
    
    print("\n✅ すべてのテスト完了")


def test_question_continuity():
    """設問番号の連続性チェック機能を単体テスト"""
    
    print("\n【設問連続性チェックの単体テスト】")
    
    from modules.question_validator import QuestionValidator
    
    validator = QuestionValidator()
    
    # テストケース1: 連続している場合
    test_questions_1 = [
        {'number': '一', 'text': '問一の内容'},
        {'number': '二', 'text': '問二の内容'},
        {'number': '三', 'text': '問三の内容'}
    ]
    
    is_continuous, warnings = validator.check_continuity(test_questions_1)
    print(f"\nテスト1（連続）: {'✅ OK' if is_continuous else '❌ NG'}")
    if warnings:
        for w in warnings:
            print(f"  - {w}")
    
    # テストケース2: 飛びがある場合
    test_questions_2 = [
        {'number': '一', 'text': '問一の内容'},
        {'number': '二', 'text': '問二の内容'},
        {'number': '六', 'text': '問六の内容'},
        {'number': '七', 'text': '問七の内容'}
    ]
    
    is_continuous, warnings = validator.check_continuity(test_questions_2)
    print(f"\nテスト2（飛びあり）: {'✅ OK' if is_continuous else '❌ NG'}")
    if warnings:
        for w in warnings:
            print(f"  - {w}")
    
    # テストケース3: セクション統合のテスト
    test_sections = [
        {
            'number': 1,
            'questions': [
                {'number': '一', 'text': '問一'},
                {'number': '二', 'text': '問二'}
            ],
            'source': {'author': '著者A', 'work': '作品A'},
            'characters': 1000
        },
        {
            'number': 2,
            'questions': [
                {'number': '三', 'text': '問三'},
                {'number': '四', 'text': '問四'}
            ],
            'source': None,
            'characters': 500
        },
        {
            'number': 3,
            'questions': [
                {'number': '一', 'text': '問一'},
                {'number': '二', 'text': '問二'}
            ],
            'source': {'author': '著者B', 'work': '作品B'},
            'characters': 800
        }
    ]
    
    print("\n【セクション統合テスト】")
    print(f"統合前: {len(test_sections)}セクション")
    
    merged = validator.merge_sections_by_continuity(test_sections)
    print(f"統合後: {len(merged)}セクション")
    
    for i, section in enumerate(merged):
        print(f"\nセクション{i+1}:")
        if 'merged_from' in section:
            print(f"  統合元: セクション{section['merged_from']}")
        questions = section.get('questions', [])
        if questions:
            q_nums = [q['number'] for q in questions]
            print(f"  設問: {', '.join(q_nums)}")


if __name__ == "__main__":
    # 設問連続性チェックの単体テスト
    test_question_continuity()
    
    # 聖光学院データでの統合テスト
    test_with_seiko()