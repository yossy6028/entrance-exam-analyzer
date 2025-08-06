#!/usr/bin/env python3
"""
2025年開成中学校の分析結果を柔軟なフォーマットでExcelに保存
"""

import sys
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor
from modules.flexible_excel_formatter import FlexibleExcelFormatter


def save_kaisei_2025_final():
    """2025年開成の分析結果を最終版フォーマットでExcelに保存"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*70)
    print("2025年開成中学校のデータを柔軟なフォーマットでExcelに保存")
    print("="*70)
    
    # コンテンツ抽出
    extractor = FinalContentExtractor()
    analysis_result = extractor.extract_all_content(text)
    
    # 手動で補正・追加情報を設定
    # 大問1（古内一絵『百年の子』）
    if len(analysis_result['sections']) >= 1:
        analysis_result['sections'][0]['questions'] = [
            {'number': '一', 'type': '記述'},
            {'number': '二', 'type': '記述'},
            {'number': '三', 'type': '記述'}
        ]
        analysis_result['sections'][0]['summary'] = (
            "出版社で学年誌を担当する野山彬が、児童文学作家の佐野三津彦から"
            "児童文学の本質について話を聞く場面。戦災孤児だった三津彦の体験を通じて、"
            "子どもの人権の歴史と児童文学の役割について論じる。"
        )
        analysis_result['sections'][0]['format'] = '小説（会話文中心）'
        analysis_result['sections'][0]['special_elements'] = 'なし'
    
    # 大問2（永井玲衣『世界の適切な保存』）
    if len(analysis_result['sections']) >= 2:
        analysis_result['sections'][1]['questions'] = [
            {'number': '一', 'type': '漢字'},
            {'number': '二', 'type': '記述'},
            {'number': '三', 'type': '記述'},
            {'number': '四', 'type': '記述'}
        ]
        analysis_result['sections'][1]['summary'] = (
            "「伝わらない」ということの本質について、大学でのシンポジウムや"
            "日常的な場面を例に考察。言語の限界と、それでも伝えようとする"
            "人間の営みについて哲学的に論じる。"
        )
        analysis_result['sections'][1]['format'] = '随筆'
        analysis_result['sections'][1]['special_elements'] = 'なし'
    
    # 総設問数を再計算
    total_questions = sum(len(s.get('questions', [])) for s in analysis_result['sections'])
    analysis_result['total_questions'] = total_questions
    
    # 設問タイプを再集計（より詳細に）
    question_types = {
        '記述': 5,      # 問題文から実際にカウント
        '漢字': 1,      # 漢字書き取り問題
        '選択': 0,
        '抜き出し': 0,
        '語句': 0
    }
    analysis_result['question_types'] = question_types
    
    # 追加情報
    additional_info = {
        '記述_最大字数': None,  # 字数制限なし
        '記述_最小字数': None,
        '選択肢_最大数': None,
        '図表_使用有無': 'なし',
        '詩歌_有無': 'なし',
        '古文_有無': 'なし',
        '漢文_有無': 'なし',
        '出題傾向': (
            "1.文学的文章（小説）と論理的文章（随筆）のバランス型 "
            "2.現代文学作品を中心に出題 "
            "3.社会的・哲学的テーマを扱った作品 "
            "4.記述問題が中心（全6問中5問） "
            "5.傍線部の意味や理由を問う問題が主体"
        ),
        '特記事項': (
            "児童文学論と言語哲学という高度で抽象的なテーマを扱った出題。"
            "戦後文学やコミュニケーション論など、社会性の高い内容。"
            "記述問題に字数制限がなく、深い理解と表現力が求められる。"
        )
    }
    
    # Excelフォーマッターを初期化
    formatter = FlexibleExcelFormatter()
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="開成中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25開成.txt",
        additional_info=additional_info
    )
    
    # 整形されたデータを表示
    print("\n【保存するデータ（主要項目）】")
    print("-"*50)
    
    # 主要項目のみ表示
    display_keys = [
        '年度', '総文字数', '大問数', '総設問数',
        '大問1_著者', '大問1_作品', '大問1_ジャンル',
        '大問2_著者', '大問2_作品', '大問2_ジャンル',
        '記述_問題数', '漢字_問題数', '出題傾向'
    ]
    
    for key in display_keys:
        if key in row_data and row_data[key] is not None:
            value = row_data[key]
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"{key}: {value}")
    
    # Excelに保存
    print("\n" + "-"*50)
    success = formatter.save_to_excel(
        school_name="開成中学校",
        row_data=row_data,
        backup=True
    )
    
    if success:
        print("\n✅ データの保存が完了しました")
        
        # サマリー情報を表示
        summary = formatter.get_school_summary("開成中学校")
        print("\n" + summary)
    else:
        print("\n❌ データの保存に失敗しました")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    save_kaisei_2025_final()