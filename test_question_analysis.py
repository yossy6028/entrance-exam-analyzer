#!/usr/bin/env python3
"""
問題分析テストスクリプト
桜蔭2020年度の問題を詳細分析
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent))

from modules.enhanced_source_extractor import EnhancedSourceExtractor
from modules.question_analyzer import QuestionAnalyzer
from modules.ocr_postprocessor import OCRPostProcessor

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_oin_2020():
    """桜蔭2020年度の問題を分析"""
    
    # 分析済みファイルを読み込み
    result_file = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/2020年度桜蔭中学校.txt")
    
    if not result_file.exists():
        logger.error(f"結果ファイルが見つかりません: {result_file}")
        return
    
    with open(result_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 80)
    print("桜蔭中学校 2020年度 問題詳細分析")
    print("=" * 80)
    print()
    
    # 1. 出典情報の抽出
    print("【1. 出典情報の分析】")
    print("-" * 40)
    
    source_extractor = EnhancedSourceExtractor()
    source_info = source_extractor.extract_sources_from_text(content, use_postprocessing=True)
    
    if source_info['found_sources']:
        for i, source in enumerate(source_info['found_sources'], 1):
            print(f"\n出典{i}:")
            print(f"  著者: {source.get('author', '不明')}")
            print(f"  作品: {source.get('title', '不明')}")
            print(f"  信頼度: {source.get('confidence', 0):.0%}")
            print(f"  抽出方法: {source.get('extraction_method', 'unknown')}")
    else:
        print("出典情報が見つかりませんでした")
    
    print()
    
    # 2. 問題構成の分析
    print("【2. 問題構成の詳細分析】")
    print("-" * 40)
    
    analyzer = QuestionAnalyzer()
    question_analysis = analyzer.analyze_questions(content, source_info)
    
    # レポート生成
    report = analyzer.generate_report(question_analysis)
    print(report)
    
    # 3. 詳細データの表示
    print("\n【3. 詳細分析データ】")
    print("-" * 40)
    
    # 大問ごとの詳細
    for section in question_analysis['sections']:
        print(f"\n■ 大問{section['section_number']}の詳細:")
        
        # 出典
        if section.get('source'):
            source = section['source']
            print(f"  出典: {source.get('author', '不明')}『{source.get('title', '不明')}』")
        
        # 設問リスト
        print(f"  設問数: {section['question_count']}問")
        
        if section['questions']:
            print("  各設問の詳細:")
            for q in section['questions']:
                line = f"    問{q['number']}: {q['type']}"
                
                # 字数制限
                if q['char_limit']:
                    if 'limit' in q['char_limit']:
                        line += f" [{q['char_limit']['limit']}字{q['char_limit']['condition']}]"
                    elif 'max' in q['char_limit']:
                        line += f" [{q['char_limit']['min']}～{q['char_limit']['max']}字]"
                
                # 選択肢数
                if q['choice_count']:
                    line += f" [{q['choice_count']}択]"
                
                # キーワード
                if q['keywords']:
                    line += f" キーワード: {', '.join(q['keywords'][:2])}"
                
                print(line)
    
    # 4. 統計サマリー
    print("\n【4. 統計サマリー】")
    print("-" * 40)
    
    stats = question_analysis['statistics']
    
    print(f"総設問数: {question_analysis['total_questions']}問")
    print(f"大問数: {len(question_analysis['sections'])}問")
    print(f"平均設問数/大問: {stats['average_questions_per_section']:.1f}問")
    
    print("\n問題種別の分布:")
    for q_type, data in sorted(stats['question_type_distribution'].items(), 
                              key=lambda x: x[1]['count'], reverse=True):
        bar_length = int(data['percentage'] / 2)  # 50% = 25文字
        bar = '■' * bar_length
        print(f"  {q_type:12s}: {bar:25s} {data['count']:2d}問 ({data['percentage']:5.1f}%)")
    
    if stats['char_limit_range']:
        print(f"\n記述式の字数制限:")
        print(f"  範囲: {stats['char_limit_range']['min']}～{stats['char_limit_range']['max']}字")
        print(f"  平均: {stats['char_limit_range']['average']}字")
    
    print("\n特徴:")
    if stats['has_choice_questions'] and stats['has_written_questions']:
        print("  ✓ 選択式と記述式の両方を含むバランス型")
    elif stats['has_choice_questions']:
        print("  ✓ 選択式中心の出題")
    elif stats['has_written_questions']:
        print("  ✓ 記述式中心の出題")
    
    if stats['most_common_type']:
        print(f"  ✓ 最も多い問題種別: {stats['most_common_type']}")
    
    # 5. エクスポート用データ構造の生成
    print("\n【5. データベース用構造】")
    print("-" * 40)
    
    export_data = {
        '年度': 2020,
        '学校名': '桜蔭中学校',
        '総設問数': question_analysis['total_questions'],
        '大問数': len(question_analysis['sections']),
        '記述_問題数': question_analysis['question_types'].get('記述式', 0),
        '選択_問題数': question_analysis['question_types'].get('選択式', 0),
        '漢字語句_問題数': question_analysis['question_types'].get('漢字・語句', 0),
        '抜き出し_問題数': question_analysis['question_types'].get('抜き出し', 0),
    }
    
    # 大問別情報
    for i, section in enumerate(question_analysis['sections'], 1):
        prefix = f'大問{i}_'
        
        if section.get('source'):
            export_data[f'{prefix}著者'] = section['source'].get('author', '')
            export_data[f'{prefix}作品'] = section['source'].get('title', '')
        
        export_data[f'{prefix}ジャンル'] = section.get('genre', '')
        export_data[f'{prefix}設問数'] = section['question_count']
        export_data[f'{prefix}文字数'] = section.get('text_length', 0)
        
        # 大問別の問題種別
        for q_type, count in section['question_types'].items():
            export_data[f'{prefix}{q_type}'] = count
    
    print("データベース登録用データ:")
    for key, value in export_data.items():
        if value:  # 値がある項目のみ表示
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("分析完了")
    print("=" * 80)


if __name__ == "__main__":
    analyze_oin_2020()