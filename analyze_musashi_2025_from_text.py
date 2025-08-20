#!/usr/bin/env python3
"""
武蔵中学校2025年国語問題の分析スクリプト（テキストファイル版）
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 必要なモジュールをインポート
from modules.enhanced_source_detector import EnhancedSourceDetector
from modules.enhanced_question_type_analyzer import EnhancedQuestionTypeAnalyzer


def analyze_musashi_2025_from_text():
    """武蔵中学校2025年の問題を既存のOCRテキストから分析"""
    
    # ファイルパス
    text_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/2025年武蔵中学校問題_国語.ocr.txt"
    
    if not Path(text_path).exists():
        print(f"エラー: ファイルが見つかりません: {text_path}")
        return None
    
    print("=" * 60)
    print("武蔵中学校 2025年 国語問題分析")
    print("=" * 60)
    print(f"分析開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"対象ファイル: {Path(text_path).name}")
    print()
    
    # 1. テキストファイルを読み込み
    print("ステップ1: OCRテキストの読み込み...")
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        print(f"  → 読み込み完了: {len(full_text)}文字")
    except Exception as e:
        print(f"エラー: ファイル読み込み中にエラーが発生: {e}")
        return None
    
    # 2. 学校名と年度の設定
    print("\nステップ2: 学校名と年度の設定...")
    detected_school = "武蔵中学校"
    detected_year = 2025
    
    print(f"  → 学校名: {detected_school}")
    print(f"  → 年度: {detected_year}")
    
    # 3. 出典情報の抽出
    print("\nステップ3: 出典情報の抽出...")
    source_detector = EnhancedSourceDetector()
    sources = source_detector.extract_sources(full_text)
    
    print(f"  → {len(sources)}件の出典情報を検出")
    
    # 信頼度の高い出典を優先表示
    high_confidence_sources = [s for s in sources if s.confidence >= 0.8]
    if high_confidence_sources:
        print("\n  高信頼度の出典:")
        for i, source in enumerate(high_confidence_sources[:3], 1):
            if source.author or source.title:
                print(f"    {i}. ", end="")
                if source.author:
                    print(f"著者: {source.author}", end="")
                if source.title:
                    if source.author:
                        print(f" / ", end="")
                    print(f"作品: {source.title}", end="")
                print(f" (信頼度: {source.confidence:.0%})")
    
    # 4. 出題形式の分析
    print("\nステップ4: 出題形式の分析...")
    question_analyzer = EnhancedQuestionTypeAnalyzer()
    question_analysis = question_analyzer.analyze_questions(full_text)
    
    print(f"  → 総問題数: {question_analysis['total_questions']}問")
    
    # タイプ別集計を表示
    if question_analysis['question_types']:
        print("\n  タイプ別集計:")
        for q_type, count in sorted(question_analysis['question_types'].items()):
            if '_' not in q_type:  # サブタイプは除外
                print(f"    {q_type}: {count}問")
    
    # 5. 分析結果をまとめる
    analysis_result = {
        'school': detected_school,
        'year': detected_year,
        'analysis_date': datetime.now().isoformat(),
        'text_stats': {
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
        
        # テキスト統計
        f.write("-" * 60 + "\n")
        f.write("【テキスト統計】\n")
        f.write("-" * 60 + "\n")
        f.write(f"総文字数: {analysis_result['text_stats']['total_characters']:,}文字\n")
        f.write(f"総行数: {analysis_result['text_stats']['total_lines']:,}行\n\n")
        
        # 出典情報（信頼度順に表示）
        f.write("-" * 60 + "\n")
        f.write("【出典情報】\n")
        f.write("-" * 60 + "\n")
        
        if analysis_result['sources']:
            # 信頼度でソート
            sorted_sources = sorted(analysis_result['sources'], 
                                  key=lambda x: x['confidence'], 
                                  reverse=True)
            
            # 高信頼度（0.8以上）の出典
            high_conf_sources = [s for s in sorted_sources if s['confidence'] >= 0.8]
            if high_conf_sources:
                f.write("\n◆ 高信頼度の出典（信頼度80%以上）:\n")
                for i, source in enumerate(high_conf_sources, 1):
                    f.write(f"\n  出典{i}:\n")
                    if source['author']:
                        f.write(f"    著者: {source['author']}\n")
                    if source['title']:
                        f.write(f"    作品名: {source['title']}\n")
                    if source['publisher']:
                        f.write(f"    出版社: {source['publisher']}\n")
                    if source['year']:
                        f.write(f"    出版年: {source['year']}\n")
                    f.write(f"    ジャンル: {source['genre']}\n")
                    f.write(f"    信頼度: {source['confidence']:.1%}\n")
            
            # 中信頼度（0.5-0.8）の出典
            mid_conf_sources = [s for s in sorted_sources if 0.5 <= s['confidence'] < 0.8]
            if mid_conf_sources:
                f.write("\n◆ 中信頼度の出典（信頼度50-80%）:\n")
                for source in mid_conf_sources[:3]:  # 最大3件まで
                    if source['author'] or source['title']:
                        f.write(f"  ・")
                        if source['author']:
                            f.write(f"著者: {source['author']} ")
                        if source['title']:
                            f.write(f"作品: {source['title']}")
                        f.write(f" (信頼度: {source['confidence']:.0%})\n")
        else:
            f.write("出典情報が検出されませんでした。\n")
        
        f.write("\n")
        
        # 出題形式分析
        f.write("-" * 60 + "\n")
        f.write("【出題形式分析】\n")
        f.write("-" * 60 + "\n")
        f.write(f"\n総問題数: {analysis_result['question_analysis']['total_questions']}問\n\n")
        
        # 問題タイプ別集計
        f.write("◆ 問題タイプ別集計:\n")
        type_dist = analysis_result['question_analysis']['type_distribution']
        main_types = {k: v for k, v in type_dist.items() if '_' not in k}
        
        if main_types:
            total = analysis_result['question_analysis']['total_questions']
            for q_type, count in sorted(main_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                bar = "■" * int(percentage / 5)  # 5%ごとに■を表示
                f.write(f"  {q_type:12s}: {count:2d}問 ({percentage:5.1f}%) {bar}\n")
        
        # サブタイプの詳細
        subtypes = {k: v for k, v in type_dist.items() if '_' in k}
        if subtypes:
            f.write("\n◆ 詳細分類:\n")
            for subtype, count in sorted(subtypes.items()):
                main_type, sub = subtype.split('_', 1)
                f.write(f"  {main_type} - {sub}: {count}問\n")
        
        f.write("\n")
        
        # 統計情報
        stats = analysis_result['question_analysis'].get('statistics', {})
        if stats:
            f.write("◆ 統計情報:\n")
            if stats.get('average_char_limit'):
                f.write(f"  記述式の平均字数制限: {stats['average_char_limit']}字\n")
            if stats.get('average_choice_count'):
                f.write(f"  選択式の平均選択肢数: {stats['average_choice_count']}\n")
            if stats.get('complexity_score'):
                level = "高" if stats['complexity_score'] >= 70 else "中" if stats['complexity_score'] >= 40 else "低"
                f.write(f"  問題複雑度スコア: {stats['complexity_score']:.1f}/100 ({level})\n")
            if stats.get('has_opinion_questions'):
                f.write(f"  意見記述問題: あり\n")
            else:
                f.write(f"  意見記述問題: なし\n")
        
        f.write("\n")
        
        # 個別問題の詳細（最初の10問）
        f.write("-" * 60 + "\n")
        f.write("【個別問題の詳細（最初の10問）】\n")
        f.write("-" * 60 + "\n")
        
        if analysis_result['questions']:
            displayed_questions = analysis_result['questions'][:10]
            for q in displayed_questions:
                f.write(f"\n問題{q['number']}:\n")
                f.write(f"  タイプ: {q['type']}")
                if q['subtype']:
                    f.write(f" ({q['subtype']})")
                f.write("\n")
                
                if q['char_limit']:
                    if isinstance(q['char_limit'], dict):
                        if q['char_limit'].get('type') == 'single':
                            f.write(f"  字数制限: {q['char_limit']['limit']}字{q['char_limit'].get('condition', '')}\n")
                        elif q['char_limit'].get('type') == 'range':
                            f.write(f"  字数制限: {q['char_limit']['min']}～{q['char_limit']['max']}字\n")
                    else:
                        f.write(f"  字数制限: {q['char_limit']}\n")
                
                if q['choice_count']:
                    f.write(f"  選択肢数: {q['choice_count']}択\n")
                
                conf_level = "高" if q['confidence'] >= 0.8 else "中" if q['confidence'] >= 0.5 else "低"
                f.write(f"  判定信頼度: {q['confidence']:.0%} ({conf_level})\n")
            
            if len(analysis_result['questions']) > 10:
                f.write(f"\n... 他{len(analysis_result['questions']) - 10}問省略 ...\n")
        else:
            f.write("個別問題の詳細情報がありません。\n")
        
        f.write("\n")
        
        # OCRテキストのサンプル（最初の2000文字）
        f.write("-" * 60 + "\n")
        f.write("【OCRテキストサンプル（最初の2000文字）】\n")
        f.write("-" * 60 + "\n")
        sample_text = analysis_result['full_text'][:2000]
        # 読みやすくするため、長い行は折り返す
        lines = sample_text.split('\n')
        for line in lines:
            if len(line) > 70:
                # 70文字ごとに改行
                for i in range(0, len(line), 70):
                    f.write(line[i:i+70] + "\n")
            else:
                f.write(line + "\n")
        
        if len(analysis_result['full_text']) > 2000:
            f.write("\n... (以下省略) ...\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("分析レポート終了\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n✅ 分析結果を保存しました: {output_path}")


def main():
    """メイン処理"""
    print("武蔵中学校2025年国語問題の分析を開始します...")
    print()
    
    # 分析実行
    analysis_result = analyze_musashi_2025_from_text()
    
    if not analysis_result:
        print("分析に失敗しました。")
        return
    
    # 結果をテキストファイルに保存
    output_dir = Path("/Users/yoshiikatsuhiko/Desktop/02_開発 (Development)/entrance_exam_analyzer")
    output_path = output_dir / "武蔵中学校2025年_分析結果.txt"
    
    save_analysis_to_text(analysis_result, output_path)
    
    # JSONでも保存（詳細データ用、full_textは除外）
    json_path = output_dir / "武蔵中学校2025年_分析結果.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json_data = {k: v for k, v in analysis_result.items() if k != 'full_text'}
        json_data['text_sample'] = analysis_result['full_text'][:500]  # サンプルのみ
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON形式でも保存しました: {json_path}")
    
    print("\n" + "=" * 60)
    print("分析が完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()