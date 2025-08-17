#!/usr/bin/env python3
"""
PDFから完全な問題分析を実行
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent))

from modules.ocr_handler import OCRHandler
from modules.enhanced_source_extractor import EnhancedSourceExtractor
from modules.question_analyzer import QuestionAnalyzer
from modules.source_validator import SourceValidator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_pdf_complete(pdf_path: str) -> Dict[str, Any]:
    """PDFを完全に分析"""
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        logger.error(f"PDFファイルが見つかりません: {pdf_path}")
        return {}
    
    print("=" * 80)
    print(f"入試問題PDF完全分析")
    print(f"ファイル: {pdf_path.name}")
    print("=" * 80)
    print()
    
    # 1. OCR処理
    print("【1. OCR処理】")
    print("-" * 40)
    print("Google Cloud Vision APIでOCR処理を実行中...")
    
    ocr = OCRHandler()
    ocr_result = ocr.process_pdf(str(pdf_path))
    
    if not ocr_result or not ocr_result.get('full_text'):
        print("❌ OCR処理に失敗しました")
        return {}
    
    print(f"✓ OCR完了: {len(ocr_result['full_text'])}文字を抽出")
    print()
    
    # 2. 出典情報の抽出
    print("【2. 出典情報の抽出】")
    print("-" * 40)
    
    source_extractor = EnhancedSourceExtractor()
    # OCRハンドラーからの結果を処理
    enhanced_result = {
        'full_text': ocr_result.get('full_text', ''),
        'pages': ocr_result.get('pages', []),
        'exam_structure': {}
    }
    # 出典情報を抽出
    source_analysis = source_extractor.extract_sources_from_text(
        enhanced_result['full_text'],
        enhanced_result.get('pages'),
        use_postprocessing=True
    )
    enhanced_result['exam_structure']['source_analysis'] = source_analysis
    source_info = enhanced_result['exam_structure'].get('source_analysis', {})
    
    if source_info.get('found_sources'):
        print(f"✓ {len(source_info['found_sources'])}件の出典を検出:")
        for i, source in enumerate(source_info['found_sources'], 1):
            print(f"\n  出典{i}:")
            print(f"    著者: {source.get('author', '不明')}")
            print(f"    作品: {source.get('title', '不明')}")
            print(f"    信頼度: {source.get('confidence', 0):.0%}")
            
            # Web検証（必要に応じて）
            if source.get('author') and source.get('title'):
                validator = SourceValidator()
                validation = validator.validate_source(
                    source.get('author'),
                    source.get('title')
                )
                if validation['exists']:
                    print(f"    ✓ Web検証: 実在を確認")
                    if validation.get('metadata'):
                        meta = validation['metadata']
                        if meta.get('year'):
                            print(f"      出版年: {meta['year']}年")
                        if meta.get('publisher'):
                            print(f"      出版社: {meta['publisher']}")
    else:
        print("出典情報が見つかりませんでした")
    
    print()
    
    # 3. 問題構成の分析
    print("【3. 問題構成の詳細分析】")
    print("-" * 40)
    
    analyzer = QuestionAnalyzer()
    question_analysis = analyzer.analyze_questions(
        enhanced_result.get('full_text', ''),
        source_info
    )
    
    # 統計表示
    stats = question_analysis.get('statistics', {})
    print(f"総設問数: {question_analysis['total_questions']}問")
    print(f"大問数: {len(question_analysis['sections'])}問")
    
    if stats.get('average_questions_per_section'):
        print(f"平均設問数/大問: {stats['average_questions_per_section']:.1f}問")
    
    print("\n問題種別の内訳:")
    for q_type, data in sorted(stats.get('question_type_distribution', {}).items(), 
                              key=lambda x: x[1]['count'], reverse=True):
        print(f"  {q_type}: {data['count']}問 ({data['percentage']}%)")
    
    print()
    
    # 4. 大問別詳細
    print("【4. 大問別詳細分析】")
    print("-" * 40)
    
    for section in question_analysis['sections']:
        print(f"\n■ 大問{section['section_number']}")
        
        # 出典情報
        if section.get('source'):
            source = section['source']
            if source.get('author') and source.get('title'):
                print(f"  出典: {source['author']}『{source['title']}』")
            elif source.get('title'):
                print(f"  出典: 『{source['title']}』")
        
        # ジャンル
        if section.get('genre'):
            print(f"  ジャンル: {section['genre']}")
        
        # 設問情報
        print(f"  設問数: {section['question_count']}問")
        print(f"  文字数: 約{section.get('text_length', 0):,}文字")
        
        # 設問種別の内訳
        if section['question_types']:
            print("  設問種別:")
            for q_type, count in sorted(section['question_types'].items()):
                print(f"    - {q_type}: {count}問")
        
        # 個別設問（最初の5問）
        if section['questions']:
            print("  各設問:")
            for j, q in enumerate(section['questions'][:5], 1):
                detail = f"    問{q['number']}: {q['type']}"
                
                # 詳細情報
                details = []
                if q.get('char_limit'):
                    if 'limit' in q['char_limit']:
                        details.append(f"{q['char_limit']['limit']}字{q['char_limit']['condition']}")
                    elif 'max' in q['char_limit']:
                        details.append(f"{q['char_limit']['min']}～{q['char_limit']['max']}字")
                
                if q.get('choice_count'):
                    details.append(f"{q['choice_count']}択")
                
                if details:
                    detail += f" [{', '.join(details)}]"
                
                print(detail)
            
            if len(section['questions']) > 5:
                print(f"    ... 他{len(section['questions'])-5}問")
    
    print()
    
    # 5. 特徴分析
    print("【5. 出題の特徴】")
    print("-" * 40)
    
    # 記述式の分析
    if stats.get('char_limit_range'):
        print(f"\n記述式問題の字数制限:")
        print(f"  最小: {stats['char_limit_range']['min']}字")
        print(f"  最大: {stats['char_limit_range']['max']}字")
        print(f"  平均: {stats['char_limit_range']['average']}字")
    
    # 出題バランス
    print("\n出題バランス:")
    if stats.get('has_choice_questions') and stats.get('has_written_questions'):
        print("  ✓ 選択式と記述式のバランス型出題")
    elif stats.get('has_choice_questions'):
        print("  ✓ 選択式中心の出題")
    elif stats.get('has_written_questions'):
        print("  ✓ 記述式中心の出題")
    
    if stats.get('most_common_type'):
        print(f"  ✓ 最頻出題形式: {stats['most_common_type']}")
    
    # 文章ジャンル
    genres = []
    for section in question_analysis['sections']:
        if section.get('genre'):
            genres.append(section['genre'])
    
    if genres:
        print(f"\n文章ジャンル:")
        for genre in set(genres):
            count = genres.count(genre)
            print(f"  - {genre}: {count}題")
    
    print()
    
    # 6. 分析結果を返す
    return {
        'ocr_result': enhanced_result,
        'source_info': source_info,
        'question_analysis': question_analysis,
        'statistics': stats
    }


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用法: python analyze_full_pdf.py <PDFファイルパス>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = analyze_pdf_complete(pdf_path)
    
    # 結果をJSONファイルに保存（オプション）
    if result:
        output_path = Path(pdf_path).stem + "_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            # 関数やオブジェクトを除外してシリアライズ可能なデータのみ保存
            clean_result = {
                'source_info': result.get('source_info', {}),
                'statistics': result.get('statistics', {}),
                'total_questions': result.get('question_analysis', {}).get('total_questions', 0),
                'sections_count': len(result.get('question_analysis', {}).get('sections', []))
            }
            json.dump(clean_result, f, ensure_ascii=False, indent=2)
        print(f"\n分析結果を保存: {output_path}")
    
    print("\n" + "=" * 80)
    print("分析完了")
    print("=" * 80)


if __name__ == "__main__":
    main()