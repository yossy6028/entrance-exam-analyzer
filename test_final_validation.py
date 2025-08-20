#!/usr/bin/env python3
"""
最終検証：修正されたシステムでの分析結果をデータベースに保存
"""

import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.universal_analyzer import UniversalAnalyzer
from pathlib import Path
from config.settings import Settings

def test_and_save_waseda_2015():
    """早稲田実業2015年度の分析結果をデータベースに保存"""
    
    # OCRテキストファイルを読み込み
    ocr_file_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.ocr.txt"
    
    if not Path(ocr_file_path).exists():
        print(f"ファイルが見つかりません: {ocr_file_path}")
        return False
        
    with open(ocr_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("分析開始...")
    
    # 分析を実行
    analyzer = UniversalAnalyzer()
    result = analyzer.analyze(text, "早稲田実業学校中等部", "2015")
    
    # 結果の詳細表示
    print(f"\n学校名: {result.school_name}")
    print(f"年度: {result.year}")
    print(f"総文字数: {result.total_characters}")
    print(f"大問数: {len(result.sections)}")
    print(f"総設問数: {result.get_question_count()}")
    
    # 出典情報
    print("\\n出典情報:")
    for i, source in enumerate(result.sources, 1):
        print(f"  出典{i}: 著者={source.author}, タイトル={source.title}")
    
    # データベースへの保存用データを準備
    db_data = {
        '年度': result.year,
        '総設問数': result.get_question_count(),
        '総文字数': result.total_characters,
        '大問数': len(result.sections),
        '更新日時': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 大問情報を追加
    for i, section in enumerate(result.sections, 1):
        db_data[f'大問{i}_設問数'] = section.question_count
        db_data[f'大問{i}_文字数'] = len(section.content)
        # 大問タイプを推定
        if '文章読解' in section.title:
            db_data[f'大問{i}_ジャンル'] = result.genre or '文章読解'
            db_data[f'大問{i}_テーマ'] = result.theme or '不明'
        elif '漢字' in section.title:
            db_data[f'大問{i}_ジャンル'] = '漢字・語句'
            db_data[f'大問{i}_テーマ'] = '漢字・語句'
    
    # 出典情報を追加
    for i, source in enumerate(result.sources, 1):
        if source.author:
            db_data[f'大問{i}_著者'] = source.author
        if source.title:
            db_data[f'大問{i}_作品'] = source.title
    
    # 設問タイプを追加
    for q_type, count in result.question_types.items():
        db_data[f'{q_type}_問題数'] = count
    
    print("\\nデータベース保存用データ:")
    for key, value in db_data.items():
        print(f"  {key}: {value}")
    
    # Excelファイルに保存
    excel_file = 'entrance_exam_database.xlsx'
    sheet_name = '早稲田実業学校中等部'
    
    try:
        # 既存データを読み込み
        with pd.ExcelFile(excel_file) as xls:
            if sheet_name in xls.sheet_names:
                existing_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # 2015年度のデータがあれば更新、なければ追加
                year_mask = existing_df['年度'] == 2015
                if year_mask.any():
                    # 既存データを更新
                    for key, value in db_data.items():
                        if key in existing_df.columns:
                            existing_df.loc[year_mask, key] = value
                    updated_df = existing_df
                else:
                    # 新しい行として追加
                    new_row = pd.DataFrame([db_data])
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            else:
                # 新しいシート
                updated_df = pd.DataFrame([db_data])
        
        # 既存のExcelファイルを読み込み、シートを更新
        with pd.ExcelFile(excel_file) as xls:
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"\\n✅ データベースを更新しました: {excel_file} - {sheet_name}")
        
        # 更新後のデータを確認
        verification_df = pd.read_excel(excel_file, sheet_name=sheet_name)
        year_data = verification_df[verification_df['年度'] == 2015]
        
        print("\\n更新後のデータ確認:")
        print(f"大問数: {year_data['大問数'].iloc[0]}")
        print(f"総設問数: {year_data['総設問数'].iloc[0]}")
        if '大問1_著者' in year_data.columns and not pd.isna(year_data['大問1_著者'].iloc[0]):
            print(f"大問1著者: {year_data['大問1_著者'].iloc[0]}")
        if '大問2_著者' in year_data.columns and not pd.isna(year_data['大問2_著者'].iloc[0]):
            print(f"大問2著者: {year_data['大問2_著者'].iloc[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ データベース更新エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_and_save_waseda_2015()
    if success:
        print("\\n🎉 最終検証完了！")
    else:
        print("\\n❌ 検証失敗")
        sys.exit(1)