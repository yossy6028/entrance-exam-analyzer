#!/usr/bin/env python3
"""
2025年開成中学校の分析結果をExcelデータベースに保存
"""

import sys
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.final_content_extractor import FinalContentExtractor
from modules.excel_formatter import ExcelFormatter


def save_kaisei_2025():
    """2025年開成の分析結果をExcelに保存"""
    
    # テキストファイルを読み込み
    file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成/25開成.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    print("="*70)
    print("2025年開成中学校のデータをExcelに保存")
    print("="*70)
    
    # コンテンツ抽出
    extractor = FinalContentExtractor()
    analysis_result = extractor.extract_all_content(text)
    
    # 手動で補正・追加情報を設定
    # 大問1（古内一絵『百年の子』）の設問を追加
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
    
    # 大問2（永井玲衣『世界の適切な保存』）の情報を補正
    if len(analysis_result['sections']) >= 2:
        analysis_result['sections'][1]['questions'] = [
            {'number': '一', 'type': '漢字・語句'},
            {'number': '二', 'type': '記述'},
            {'number': '三', 'type': '記述'},
            {'number': '四', 'type': '記述'}
        ]
        analysis_result['sections'][1]['summary'] = (
            "「伝わらない」ということの本質について、大学でのシンポジウムや"
            "日常的な場面を例に考察。言語の限界と、それでも伝えようとする"
            "人間の営みについて哲学的に論じる。"
        )
    
    # 総設問数を再計算
    total_questions = sum(len(s.get('questions', [])) for s in analysis_result['sections'])
    analysis_result['total_questions'] = total_questions
    
    # 設問タイプを再集計
    question_types = {'記述': 0, '選択': 0, '漢字・語句': 0, '抜き出し': 0}
    for section in analysis_result['sections']:
        for q in section.get('questions', []):
            q_type = q.get('type', '記述')
            if q_type in question_types:
                question_types[q_type] += 1
    analysis_result['question_types'] = question_types
    
    # Excelフォーマッターを初期化
    formatter = ExcelFormatter()
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="開成中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25開成.txt"
    )
    
    # 出題傾向を追加
    row_data['出題傾向'] = (
        "1.文学的文章と論理的文章のバランス型 "
        "2.現代文学中心 "
        "3.社会的テーマ（児童文学、コミュニケーション論） "
        "4.記述問題中心"
    )
    
    # 特記事項を追加
    row_data['特記事項'] = (
        "児童文学論と言語哲学という高度なテーマを扱った出題。"
        "傍線部の意味を問う記述問題が中心。"
    )
    
    # 表示用に整形されたデータを出力
    print("\n【保存するデータ】")
    print("-"*50)
    for key, value in row_data.items():
        if value is not None and value != 0:
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
        
        # 保存後の統計情報を表示
        stats = formatter.get_summary_statistics("開成中学校")
        if stats:
            print("\n【開成中学校の統計情報】")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.1f}")
                else:
                    print(f"  {key}: {value}")
    else:
        print("\n❌ データの保存に失敗しました")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    save_kaisei_2025()