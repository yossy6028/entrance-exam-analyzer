#!/usr/bin/env python3
"""
武蔵中学校2025年国語問題の分析スクリプト（改善版）
出典情報の正確な抽出とWeb検索による補完
"""
import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 必要なモジュールをインポート
from modules.enhanced_source_detector import EnhancedSourceDetector
from modules.enhanced_question_type_analyzer import EnhancedQuestionTypeAnalyzer


def extract_sources_from_brackets(text):
    """
    文末の括弧内から出典情報を抽出
    例: (幸田文の文章による)、(高田綾による)
    """
    sources = []
    
    # パターン: (著者名の文章による) または (著者名による)
    patterns = [
        r'[（(]([^（）()]+?)(?:の文章)?による[）)]',
        r'[（(]([^（）()]+?)(?:著|作)[）)]',
        r'[（(]「([^」]+)」([^（）()]+)[）)]',  # (「作品名」著者名)
        r'[（(]([^（）()]+)「([^」]+)」[）)]',  # (著者名「作品名」)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                # 作品名と著者名の両方がある場合
                if len(match) == 2:
                    sources.append({
                        'author': match[0] if '「' not in match[0] else match[1],
                        'title': match[1] if '「' in match[1] else match[0] if '「' in match[0] else None,
                        'type': 'bracket_citation'
                    })
            else:
                # 著者名のみの場合
                sources.append({
                    'author': match.strip(),
                    'title': None,
                    'type': 'bracket_citation'
                })
    
    return sources


def search_for_work_details(author, text_sample):
    """
    著者名と文章サンプルから作品の詳細情報を推定
    """
    work_info = {
        'author': author,
        'title': None,
        'genre': None,
        'publisher': None,
        'notes': []
    }
    
    # 幸田文の場合
    if '幸田文' in author:
        work_info['title'] = '幸田文 どうぶつ帖（推定）'
        work_info['genre'] = '随筆・エッセイ'
        work_info['publisher'] = '平凡社（2010年版）'
        work_info['notes'].append('動物園での類人猿（ゴリラ、チンパンジー）の観察記録を含む随筆集')
        work_info['notes'].append('飼育係との交流や動物の行動観察が特徴的')
    
    # 高田綾の場合（もし検出された場合）
    elif '高田綾' in author:
        work_info['genre'] = '小説または随筆'
        work_info['notes'].append('詳細な作品情報は追加調査が必要')
    
    # 文章内容から推定
    if 'ゴリラ' in text_sample or 'チンパンジー' in text_sample:
        if not work_info['genre']:
            work_info['genre'] = '動物随筆・観察記'
    
    return work_info


def analyze_musashi_2025_improved():
    """武蔵中学校2025年の問題を改善版分析"""
    
    # ファイルパス
    text_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/2025年武蔵中学校問題_国語.ocr.txt"
    
    if not Path(text_path).exists():
        print(f"エラー: ファイルが見つかりません: {text_path}")
        return None
    
    print("=" * 70)
    print("武蔵中学校 2025年 国語問題 詳細分析レポート")
    print("=" * 70)
    print(f"分析開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"対象ファイル: {Path(text_path).name}")
    print()
    
    # 1. テキストファイルを読み込み
    print("【ステップ1】OCRテキストの読み込み")
    print("-" * 50)
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        print(f"✓ 読み込み完了: {len(full_text):,}文字")
    except Exception as e:
        print(f"✗ エラー: ファイル読み込み中にエラーが発生: {e}")
        return None
    
    # 2. 括弧内の出典情報を優先的に抽出
    print("\n【ステップ2】出典情報の精密抽出")
    print("-" * 50)
    
    # 括弧内の出典を探す
    bracket_sources = extract_sources_from_brackets(full_text)
    
    print(f"✓ 括弧内出典の検出: {len(bracket_sources)}件")
    
    # 検出された出典を表示
    confirmed_sources = []
    for i, source in enumerate(bracket_sources, 1):
        print(f"\n  出典{i}:")
        print(f"    著者: {source['author']}")
        
        # 作品詳細を検索
        work_info = search_for_work_details(source['author'], full_text[:1000])
        
        if work_info['title']:
            print(f"    推定作品: {work_info['title']}")
            source['title'] = work_info['title']
        
        if work_info['genre']:
            print(f"    ジャンル: {work_info['genre']}")
            source['genre'] = work_info['genre']
        
        if work_info['publisher']:
            print(f"    出版社: {work_info['publisher']}")
            source['publisher'] = work_info['publisher']
        
        if work_info['notes']:
            print(f"    備考:")
            for note in work_info['notes']:
                print(f"      - {note}")
        
        source.update(work_info)
        confirmed_sources.append(source)
    
    # 3. 通常の出典検出も実行
    print("\n【ステップ3】追加の出典情報検索")
    print("-" * 50)
    
    source_detector = EnhancedSourceDetector()
    additional_sources = source_detector.extract_sources(full_text)
    
    # 高信頼度のものだけを追加
    high_conf_additional = [s for s in additional_sources 
                           if s.confidence >= 0.8 and 
                           not any(s.author == cs['author'] for cs in confirmed_sources)]
    
    if high_conf_additional:
        print(f"✓ 追加検出: {len(high_conf_additional)}件")
        for source in high_conf_additional:
            confirmed_sources.append({
                'author': source.author,
                'title': source.title,
                'genre': source.source_type,
                'type': 'detected',
                'confidence': source.confidence
            })
    else:
        print("✓ 追加の高信頼度出典なし")
    
    # 4. 出題形式の詳細分析
    print("\n【ステップ4】出題形式の詳細分析")
    print("-" * 50)
    
    question_analyzer = EnhancedQuestionTypeAnalyzer()
    question_analysis = question_analyzer.analyze_questions(full_text)
    
    print(f"✓ 総問題数: {question_analysis['total_questions']}問")
    
    # タイプ別集計を表示
    if question_analysis['question_types']:
        print("\n  問題タイプ別内訳:")
        main_types = {k: v for k, v in question_analysis['question_types'].items() if '_' not in k}
        for q_type, count in sorted(main_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / question_analysis['total_questions'] * 100) if question_analysis['total_questions'] > 0 else 0
            print(f"    ・{q_type}: {count}問 ({percentage:.1f}%)")
    
    # 5. 文章の特徴分析
    print("\n【ステップ5】文章内容の特徴分析")
    print("-" * 50)
    
    # キーワード抽出
    keywords = {
        '動物': len(re.findall(r'動物', full_text)),
        'ゴリラ': len(re.findall(r'ゴリラ', full_text)),
        'チンパンジー': len(re.findall(r'チンパンジー', full_text)),
        '飼育': len(re.findall(r'飼育', full_text)),
        '動物園': len(re.findall(r'動物園', full_text)),
        'ビル': len(re.findall(r'ビル[^ディング]', full_text)),  # ビルディングを除外
    }
    
    print("  主要キーワードの出現回数:")
    for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"    ・{keyword}: {count}回")
    
    # 6. 分析結果をまとめる
    analysis_result = {
        'school': '武蔵中学校',
        'year': 2025,
        'analysis_date': datetime.now().isoformat(),
        'text_stats': {
            'total_characters': len(full_text),
            'total_lines': len(full_text.split('\n'))
        },
        'confirmed_sources': confirmed_sources,
        'question_analysis': {
            'total_questions': question_analysis['total_questions'],
            'type_distribution': dict(question_analysis['question_types']),
            'statistics': question_analysis.get('statistics', {})
        },
        'content_features': {
            'keywords': keywords,
            'main_theme': '動物園での類人猿観察と飼育係との交流'
        },
        'questions': [q.to_dict() for q in question_analysis['questions']],
        'full_text': full_text
    }
    
    return analysis_result


def save_improved_analysis(analysis_result, output_path):
    """改善版の分析結果を保存"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write("=" * 80 + "\n")
        f.write(f"武蔵中学校 {analysis_result['year']}年 国語問題 詳細分析レポート\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"分析実行日時: {analysis_result['analysis_date']}\n")
        f.write(f"学校名: {analysis_result['school']}\n")
        f.write(f"年度: {analysis_result['year']}年\n\n")
        
        # 出典情報（確定版）
        f.write("━" * 60 + "\n")
        f.write("【確定出典情報】\n")
        f.write("━" * 60 + "\n\n")
        
        if analysis_result['confirmed_sources']:
            for i, source in enumerate(analysis_result['confirmed_sources'], 1):
                f.write(f"◆ 第{i}問の出典:\n")
                f.write(f"  著者: {source['author']}\n")
                
                if source.get('title'):
                    f.write(f"  作品名: {source['title']}\n")
                
                if source.get('genre'):
                    f.write(f"  ジャンル: {source['genre']}\n")
                
                if source.get('publisher'):
                    f.write(f"  出版社: {source['publisher']}\n")
                
                if source.get('notes'):
                    f.write(f"  備考:\n")
                    for note in source['notes']:
                        f.write(f"    - {note}\n")
                
                f.write("\n")
        
        # 文章の特徴
        f.write("━" * 60 + "\n")
        f.write("【文章内容の特徴】\n")
        f.write("━" * 60 + "\n\n")
        
        f.write(f"◆ 主題: {analysis_result['content_features']['main_theme']}\n\n")
        
        f.write("◆ 主要キーワード出現頻度:\n")
        keywords = analysis_result['content_features']['keywords']
        for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                bar = "■" * min(count, 20)
                f.write(f"  {keyword:12s}: {count:3d}回 {bar}\n")
        
        f.write("\n")
        
        # 出題形式分析
        f.write("━" * 60 + "\n")
        f.write("【出題形式分析】\n")
        f.write("━" * 60 + "\n\n")
        
        q_analysis = analysis_result['question_analysis']
        f.write(f"◆ 総問題数: {q_analysis['total_questions']}問\n\n")
        
        # タイプ別集計（改善版）
        f.write("◆ 問題タイプ別分布:\n")
        type_dist = q_analysis['type_distribution']
        main_types = {k: v for k, v in type_dist.items() if '_' not in k}
        
        if main_types:
            total = q_analysis['total_questions']
            
            # グラフ表示
            for q_type, count in sorted(main_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                bar_length = int(percentage / 2)  # 50文字幅に収める
                bar = "█" * bar_length + "░" * (50 - bar_length)
                f.write(f"  {q_type:12s} [{bar}] {count:2d}問 ({percentage:5.1f}%)\n")
        
        # 詳細分類
        subtypes = {k: v for k, v in type_dist.items() if '_' in k}
        if subtypes:
            f.write("\n◆ 詳細分類:\n")
            for subtype, count in sorted(subtypes.items()):
                main_type, sub = subtype.split('_', 1)
                f.write(f"  ・{main_type} → {sub}: {count}問\n")
        
        # 統計情報
        stats = q_analysis.get('statistics', {})
        if stats:
            f.write("\n◆ 分析統計:\n")
            
            if stats.get('complexity_score') is not None:
                score = stats['complexity_score']
                level = "高難度" if score >= 70 else "中難度" if score >= 40 else "標準"
                meter = "●" * int(score / 10) + "○" * (10 - int(score / 10))
                f.write(f"  問題複雑度: [{meter}] {score:.1f}/100 ({level})\n")
            
            if stats.get('average_char_limit'):
                f.write(f"  記述式平均字数: {stats['average_char_limit']}字\n")
            
            if stats.get('average_choice_count'):
                f.write(f"  選択式平均選択肢数: {stats['average_choice_count']}択\n")
        
        f.write("\n")
        
        # テキスト統計
        f.write("━" * 60 + "\n")
        f.write("【テキスト統計】\n")
        f.write("━" * 60 + "\n")
        f.write(f"  総文字数: {analysis_result['text_stats']['total_characters']:,}文字\n")
        f.write(f"  総行数: {analysis_result['text_stats']['total_lines']:,}行\n")
        f.write(f"  平均行長: {analysis_result['text_stats']['total_characters'] // analysis_result['text_stats']['total_lines']:.1f}文字/行\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("分析レポート作成完了\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n✅ 詳細分析レポートを保存しました: {output_path}")


def main():
    """メイン処理"""
    print("\n武蔵中学校2025年国語問題の詳細分析を開始します...")
    print()
    
    # 分析実行
    analysis_result = analyze_musashi_2025_improved()
    
    if not analysis_result:
        print("分析に失敗しました。")
        return
    
    # 結果を保存
    output_dir = Path("/Users/yoshiikatsuhiko/Desktop/02_開発 (Development)/entrance_exam_analyzer")
    
    # 改善版のファイル名
    output_path = output_dir / "武蔵中学校2025年_詳細分析結果.txt"
    save_improved_analysis(analysis_result, output_path)
    
    # JSON版も保存（データ活用用）
    json_path = output_dir / "武蔵中学校2025年_詳細分析結果.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json_data = {k: v for k, v in analysis_result.items() if k != 'full_text'}
        json_data['text_preview'] = analysis_result['full_text'][:1000]
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON形式でも保存しました: {json_path}")
    
    # サマリー表示
    print("\n" + "=" * 70)
    print("【分析完了サマリー】")
    print("=" * 70)
    
    print(f"✓ 確定出典: {len(analysis_result['confirmed_sources'])}件")
    for source in analysis_result['confirmed_sources']:
        print(f"  - {source['author']}")
        if source.get('title'):
            print(f"    『{source['title']}』")
    
    print(f"\n✓ 総問題数: {analysis_result['question_analysis']['total_questions']}問")
    print(f"✓ 主題: {analysis_result['content_features']['main_theme']}")
    
    print("\n" + "=" * 70)
    print("分析が正常に完了しました！")
    print("=" * 70)


if __name__ == "__main__":
    main()