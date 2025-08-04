#!/usr/bin/env python3
"""
開成中学校2025年度入試問題分析スクリプト
Google Cloud Vision APIを使用してPDFから直接分析
"""
import re
from pathlib import Path
import pandas as pd
from datetime import datetime
from modules.pdf_processor import PDFProcessor
from modules.ocr_handler import OCRHandler
from modules.text_analyzer import TextAnalyzer
from modules.pattern_extractor import PatternExtractor
from modules.excel_writer import ExcelWriter
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def analyze_kaisei_2025(pdf_path: str):
    """開成中2025年度の入試問題を分析"""
    
    print(f"\n{'='*60}")
    print(f"開成中学校2025年度 入試問題分析")
    print(f"{'='*60}")
    
    # PDFファイルの存在確認
    if not Path(pdf_path).exists():
        print(f"❌ PDFファイルが見つかりません: {pdf_path}")
        return None
    
    print(f"\n📄 PDFファイル: {Path(pdf_path).name}")
    
    # 1. PDF処理
    print(f"\n【1. PDF処理】")
    pdf_processor = PDFProcessor()
    images = pdf_processor.convert_pdf_to_images(pdf_path)
    print(f"✅ {len(images)}ページを画像に変換")
    
    # 2. OCR処理
    print(f"\n【2. OCR処理】")
    ocr_handler = OCRHandler()
    
    all_text = []
    for i, image in enumerate(images):
        print(f"  ページ{i+1}/{len(images)}を処理中...", end='', flush=True)
        result = ocr_handler.extract_text_from_image(image)
        text = result.get('full_text', '')
        all_text.append(text)
        print(f" ✅ ({len(text)}文字)")
    
    # テキスト結合
    combined_text = "\n".join(all_text)
    print(f"\n📝 抽出されたテキスト: {len(combined_text)}文字")
    
    # OCR結果が少なすぎる場合の警告
    if len(combined_text) < 1000:
        print(f"\u26a0️  警告: OCRで抽出されたテキストが非常に少ないです")
        print(f"\u62bd出されたテキストの先頭100文字:")
        print(combined_text[:100])
        print("\n※ Google Cloud Vision APIの認証が正しく設定されているか確認してください")
    
    # 3. テキスト分析
    print(f"\n【3. テキスト分析】")
    
    # 設問パターンの定義（開成中学校用）
    question_patterns = {
        '漢字・語句': [
            r'漢字.*書き.*なさい',
            r'カタカナを漢字に.*なさい',
            r'ひらがなを漢字に.*なさい',
            r'意味.*答えなさい',
            r'語句.*説明.*なさい'
        ],
        '選択': [
            r'選び.*なさい',
            r'記号で答えなさい',
            r'最も.*ものを.*選び',
            r'ア～[オカ]から.*選び',
            r'次の中から.*選び'
        ],
        '抜き出し': [
            r'抜き出.*なさい',
            r'文中から.*抜き出',
            r'本文中の.*を答えなさい',
            r'書き抜.*なさい'
        ],
        '記述': [
            r'説明.*なさい',
            r'理由.*答えなさい',
            r'どのような.*か.*答えなさい',
            r'なぜ.*か.*答えなさい',
            r'心情.*説明.*なさい'
        ]
    }
    
    analyzer = TextAnalyzer(question_patterns)
    analysis_result = analyzer.analyze_exam_structure(combined_text)
    
    print(f"✅ 大問数: {len(analysis_result['sections'])}")
    print(f"✅ 総設問数: {len(analysis_result['questions'])}")
    
    # 4. 出典情報の抽出
    print(f"\n【4. 出典情報の抽出】")
    
    # 出典パターンの定義
    source_patterns = [
        r'（([^）]+)『([^』]+)』[^）]*）',  # 日本語括弧
        r'（([^）]+)「([^」]+)」[^）]*）',  # 日本語括弧、引用符
        r'\(([^)]+)『([^』]+)』[^)]*\)',  # 半角括弧
    ]
    
    pattern_extractor = PatternExtractor(source_patterns)
    
    sources = []
    for section in analysis_result['sections']:
        source_info = pattern_extractor.extract_source_info(section['text'])
        if source_info['author'] or source_info['title']:
            sources.append({
                'section': section['number'],
                **source_info
            })
            print(f"  大問{section['number']}: {source_info['author']} - {source_info['title'] or '(作品名不明)'}")
    
    # 5. Excel出力
    print(f"\n【5. 結果の保存】")
    
    # Excel用にテキストをサニタイズ
    def sanitize_for_excel(text):
        """Excel保存用にテキストをサニタイズ"""
        if not text:
            return ""
        
        # 問題のある特殊文字を定義
        problematic_chars = {
            '\ufff9',  # Interlinear Annotation Anchor
            '\ufffa',  # Interlinear Annotation Separator  
            '\ufffb',  # Interlinear Annotation Terminator
            '\ufeff',  # Byte Order Mark
            '\u200b',  # Zero Width Space
            '\u200c',  # Zero Width Non-Joiner
            '\u200d',  # Zero Width Joiner
        }
        
        # 特殊文字を除去
        cleaned = ''.join(char for char in text if char not in problematic_chars)
        
        # 山括弧〈〉を通常の括弧に置換
        cleaned = cleaned.replace('〈', '＜').replace('〉', '＞')
        
        # 制御文字を除去（改行・タブは保持）
        sanitized = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
        
        # Excelで問題を起こす可能性のある文字列パターンを修正
        if sanitized.startswith('＜') or sanitized.startswith('〈'):
            sanitized = '「' + sanitized[1:]
        if sanitized.endswith('＞') or sanitized.endswith('〉'):
            sanitized = sanitized[:-1] + '」'
        
        return sanitized[:500]  # 長すぎる場合は短縮
    
    # データベース形式で保存
    create_database_excel(analysis_result, sources, len(combined_text))
    
    # 通常の分析結果も保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"開成中学校_2025_分析結果_{timestamp}.xlsx"
    
    excel_writer = ExcelWriter('data/output')
    excel_writer.write_analysis_results(
        output_file,
        analysis_result,
        sources,
        {
            'school_name': '開成中学校',
            'year': '2025',
            'total_chars': len(combined_text)
        }
    )
    
    print(f"✅ 分析結果を保存: {output_file}")
    
    return analysis_result


def create_database_excel(analysis_result, sources, total_chars):
    """データベース形式のExcelファイルを作成・更新"""
    
    # データベースファイル名
    db_filename = "entrance_exam_database.xlsx"
    school_name = "開成中学校"
    year = 2025
    
    # 既存ファイルがあるかチェック
    try:
        existing_sheets = pd.ExcelFile(db_filename, engine='openpyxl').sheet_names
    except FileNotFoundError:
        existing_sheets = []
    
    # Excel用にテキストをサニタイズ（関数定義済み）
    def sanitize_for_excel(text):
        if not text:
            return ""
        problematic_chars = {'\ufff9', '\ufffa', '\ufffb', '\ufeff', '\u200b', '\u200c', '\u200d'}
        cleaned = ''.join(char for char in text if char not in problematic_chars)
        cleaned = cleaned.replace('〈', '＜').replace('〉', '＞')
        sanitized = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
        if sanitized.startswith('＜') or sanitized.startswith('〈'):
            sanitized = '「' + sanitized[1:]
        if sanitized.endswith('＞') or sanitized.endswith('〉'):
            sanitized = sanitized[:-1] + '」'
        return sanitized[:500]
    
    # 新しいデータを準備
    data_row = {
        '年度': year,
        '総設問数': len(analysis_result['questions']),
        '総文字数': total_chars,
        '大問数': len(analysis_result['sections'])
    }
    
    # 各大問のデータを追加
    for i, section in enumerate(analysis_result['sections'], 1):
        # 該当する出典情報を探す
        section_source = next((s for s in sources if s['section'] == section['number']), {})
        
        # 文章ジャンルとテーマを判定
        section_text = section['text'][:1000]  # 最初の1000文字で判定
        
        # ジャンル判定
        if any(word in section_text for word in ['小説', '物語', '「', '」', 'と言った', 'と思った']):
            genre = '小説・物語'
        elif any(word in section_text for word in ['評論', '論説', 'について', 'という', 'ことは']):
            genre = '評論・論説'
        elif any(word in section_text for word in ['随筆', 'エッセイ', '私は', '経験']):
            genre = '随筆・エッセイ'
        else:
            genre = '評論・論説'  # デフォルト
        
        # テーマ判定（簡易版）
        if any(word in section_text for word in ['自然', '環境', '生物', '動物']):
            theme = '自然・環境'
        elif any(word in section_text for word in ['社会', '人間', '文化', '歴史']):
            theme = '社会・文化'
        elif any(word in section_text for word in ['科学', '技術', 'AI', 'コンピュータ']):
            theme = '科学・技術'
        elif any(word in section_text for word in ['友情', '家族', '成長']):
            theme = '人間関係・成長'
        else:
            theme = '一般'
        
        data_row[f'大問{i}_ジャンル'] = genre
        data_row[f'大問{i}_テーマ'] = theme
        data_row[f'大問{i}_著者'] = sanitize_for_excel(section_source.get('author', '不明'))
        data_row[f'大問{i}_作品'] = sanitize_for_excel(section_source.get('title', '不明'))
        data_row[f'大問{i}_設問数'] = len([q for q in analysis_result['questions'] if q['section'] == section['number']])
        data_row[f'大問{i}_文字数'] = len(section['text'])
    
    # 設問タイプ別集計
    for q_type, count in analysis_result['question_types'].items():
        data_row[f'{q_type}_問題数'] = count
    
    # 新しいデータフレームを作成
    new_df = pd.DataFrame([data_row])
    
    # Excelファイルに書き込み
    with pd.ExcelWriter(db_filename, engine='openpyxl', mode='a' if existing_sheets else 'w', if_sheet_exists='replace') as writer:
        if school_name in existing_sheets:
            # 既存シートに追加
            existing_df = pd.read_excel(db_filename, sheet_name=school_name)
            existing_df['年度'] = pd.to_numeric(existing_df['年度'], errors='coerce')
            if year in existing_df['年度'].values:
                existing_df = existing_df[existing_df['年度'] != year]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df['年度'] = pd.to_numeric(combined_df['年度'], errors='coerce')
            combined_df = combined_df.sort_values('年度')
        else:
            combined_df = new_df
        
        combined_df.to_excel(writer, sheet_name=school_name, index=False)
    
    print(f"📊 データベース更新: {db_filename} - {school_name}シート")


def main():
    """メイン処理"""
    # 開成中2025年のPDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # 分析実行
    result = analyze_kaisei_2025(pdf_path)
    
    if result:
        print(f"\n✅ 分析が完了しました！")
        print(f"\n【分析サマリー】")
        print(f"- 大問数: {len(result['sections'])}")
        print(f"- 総設問数: {len(result['questions'])}")
        print(f"- 設問タイプ:")
        for q_type, count in result['question_types'].items():
            percentage = (count / len(result['questions'])) * 100
            print(f"  - {q_type}: {count}問 ({percentage:.1f}%)")


if __name__ == "__main__":
    main()