#!/usr/bin/env python3
"""
武蔵中学校2025年国語問題の分析スクリプト
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 必要なモジュールをインポート
from modules.pdf_ocr_processor import PDFOCRProcessor
from modules.enhanced_source_detector import EnhancedSourceDetector
from modules.enhanced_question_type_analyzer import EnhancedQuestionTypeAnalyzer
from modules.school_detector import SchoolDetector
from modules.year_detector import YearDetector


def analyze_musashi_2025():
    """武蔵中学校2025年の問題を分析"""
    
    # ファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/2025年武蔵中学校問題_国語.pdf"
    
    if not Path(pdf_path).exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        return None
    
    print("=" * 60)
    print("武蔵中学校 2025年 国語問題分析")
    print("=" * 60)
    print(f"分析開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"対象ファイル: {Path(pdf_path).name}")
    print()
    
    # 1. PDFをOCR処理
    print("ステップ1: PDFのOCR処理中...")
    ocr_processor = PDFOCRProcessor()
    
    try:
        # Pathオブジェクトに変換
        ocr_result = ocr_processor.process_pdf(Path(pdf_path))
        
        if not ocr_result or 'text' not in ocr_result:
            print("エラー: OCR処理に失敗しました")
            return None
        
        full_text = ocr_result['text']
        print(f"  → OCR完了: {len(full_text)}文字を抽出")
        
    except Exception as e:
        print(f"エラー: OCR処理中にエラーが発生: {e}")
        return None
    
    # 2. 学校名と年度の検出
    print("\nステップ2: 学校名と年度の検出...")
    school_detector = SchoolDetector()
    year_detector = YearDetector()
    
    detected_school = school_detector.detect(full_text)
    detected_year = year_detector.detect(full_text)
    
    # ファイル名からも確認
    if not detected_school or detected_school == "不明":
        detected_school = "武蔵中学校"
    if not detected_year:
        detected_year = 2025
    
    print(f"  → 学校名: {detected_school}")
    print(f"  → 年度: {detected_year}")
    
    # 3. 出典情報の抽出
    print("\nステップ3: 出典情報の抽出...")
    source_detector = EnhancedSourceDetector()
    sources = source_detector.extract_sources(full_text)
    
    print(f"  → {len(sources)}件の出典情報を検出")
    
    # 4. 出題形式の分析
    print("\nステップ4: 出題形式の分析...")
    question_analyzer = EnhancedQuestionTypeAnalyzer()
    question_analysis = question_analyzer.analyze_questions(full_text)
    
    print(f"  → 総問題数: {question_analysis['total_questions']}問")
    
    # 5. 分析結果をまとめる
    analysis_result = {
        'school': detected_school,
        'year': detected_year,
        'analysis_date': datetime.now().isoformat(),
        'ocr_stats': {
            'total_characters': len(full_text),
            'total_lines': len(full_text.split('\n'))
        },
        'sources': [],
        'question_analysis': {
            'total_questions': question_analysis['total_questions'],
            'type_distribution': dict(question_analysis['question_types']),
            'statistics': question_analysis.get('statistics', {})
        },
        'questions': [],
        'full_text': full_text
    }
    
    # 出典情報を整形
    for i, source in enumerate(sources, 1):
        source_dict = {
            'number': i,
            'author': source.author,
            'title': source.title,
            'publisher': source.publisher,
            'year': source.year,
            'genre': source.source_type,
            'confidence': source.confidence
        }
        analysis_result['sources'].append(source_dict)
    
    # 問題情報を整形
    for q in question_analysis['questions']:
        question_dict = {
            'number': q.number,
            'type': q.type,
            'subtype': q.subtype,
            'char_limit': q.char_limit,
            'choice_count': q.choice_count,
            'confidence': q.confidence
        }
        analysis_result['questions'].append(question_dict)
    
    return analysis_result


def save_analysis_to_text(analysis_result, output_path):
    """分析結果をテキストファイルに保存"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write("=" * 80 + "\n")
        f.write(f"武蔵中学校 {analysis_result['year']}年 国語問題 分析レポート\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"分析実行日時: {analysis_result['analysis_date']}\n")
        f.write(f"学校名: {analysis_result['school']}\n")
        f.write(f"年度: {analysis_result['year']}年\n\n")
        
        # OCR統計
        f.write("-" * 60 + "\n")
        f.write("【OCR処理結果】\n")
        f.write("-" * 60 + "\n")
        f.write(f"総文字数: {analysis_result['ocr_stats']['total_characters']:,}文字\n")
        f.write(f"総行数: {analysis_result['ocr_stats']['total_lines']:,}行\n\n")
        
        # 出典情報
        f.write("-" * 60 + "\n")
        f.write("【出典情報】\n")
        f.write("-" * 60 + "\n")
        
        if analysis_result['sources']:
            for source in analysis_result['sources']:
                f.write(f"\n出典{source['number']}:\n")
                if source['author']:
                    f.write(f"  著者: {source['author']}\n")
                if source['title']:
                    f.write(f"  作品名: {source['title']}\n")
                if source['publisher']:
                    f.write(f"  出版社: {source['publisher']}\n")
                if source['year']:
                    f.write(f"  出版年: {source['year']}\n")
                f.write(f"  ジャンル: {source['genre']}\n")
                f.write(f"  信頼度: {source['confidence']:.2%}\n")
        else:
            f.write("出典情報が検出されませんでした。\n")
        
        f.write("\n")
        
        # 出題形式分析
        f.write("-" * 60 + "\n")
        f.write("【出題形式分析】\n")
        f.write("-" * 60 + "\n")
        f.write(f"総問題数: {analysis_result['question_analysis']['total_questions']}問\n\n")
        
        f.write("問題タイプ別集計:\n")
        type_dist = analysis_result['question_analysis']['type_distribution']
        for q_type, count in sorted(type_dist.items()):
            if '_' not in q_type:  # サブタイプは除外
                percentage = (count / analysis_result['question_analysis']['total_questions'] * 100) if analysis_result['question_analysis']['total_questions'] > 0 else 0
                f.write(f"  {q_type}: {count}問 ({percentage:.1f}%)\n")
        
        f.write("\n")
        
        # 統計情報
        stats = analysis_result['question_analysis'].get('statistics', {})
        if stats:
            f.write("統計情報:\n")
            if stats.get('average_char_limit'):
                f.write(f"  記述式平均字数: {stats['average_char_limit']}字\n")
            if stats.get('average_choice_count'):
                f.write(f"  選択式平均選択肢数: {stats['average_choice_count']}\n")
            if stats.get('complexity_score'):
                f.write(f"  複雑度スコア: {stats['complexity_score']}/100\n")
            if stats.get('has_opinion_questions'):
                f.write(f"  意見記述問題: あり\n")
        
        f.write("\n")
        
        # 個別問題の詳細
        f.write("-" * 60 + "\n")
        f.write("【個別問題の詳細】\n")
        f.write("-" * 60 + "\n")
        
        if analysis_result['questions']:
            for q in analysis_result['questions']:
                f.write(f"\n問題{q['number']}:\n")
                f.write(f"  タイプ: {q['type']}\n")
                if q['subtype']:
                    f.write(f"  サブタイプ: {q['subtype']}\n")
                if q['char_limit']:
                    f.write(f"  字数制限: {q['char_limit']}\n")
                if q['choice_count']:
                    f.write(f"  選択肢数: {q['choice_count']}\n")
                f.write(f"  判定信頼度: {q['confidence']:.2%}\n")
        else:
            f.write("個別問題の詳細情報がありません。\n")
        
        f.write("\n")
        
        # OCRで抽出されたテキスト（最初の3000文字）
        f.write("-" * 60 + "\n")
        f.write("【OCR抽出テキスト（最初の3000文字）】\n")
        f.write("-" * 60 + "\n")
        f.write(analysis_result['full_text'][:3000])
        if len(analysis_result['full_text']) > 3000:
            f.write("\n\n... (以下省略) ...\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("分析レポート終了\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n分析結果を保存しました: {output_path}")


def main():
    """メイン処理"""
    print("武蔵中学校2025年国語問題の分析を開始します...")
    
    # 分析実行
    analysis_result = analyze_musashi_2025()
    
    if not analysis_result:
        print("分析に失敗しました。")
        return
    
    # 結果をテキストファイルに保存
    output_dir = Path("/Users/yoshiikatsuhiko/Desktop/02_開発 (Development)/entrance_exam_analyzer")
    output_path = output_dir / "武蔵中学校2025年_分析結果.txt"
    
    save_analysis_to_text(analysis_result, output_path)
    
    # JSONでも保存（詳細データ用）
    json_path = output_dir / "武蔵中学校2025年_分析結果.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        # full_textは大きいので除外
        json_data = {k: v for k, v in analysis_result.items() if k != 'full_text'}
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON形式でも保存しました: {json_path}")
    
    print("\n分析が完了しました！")


if __name__ == "__main__":
    main()