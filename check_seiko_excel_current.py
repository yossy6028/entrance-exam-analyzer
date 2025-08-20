#!/usr/bin/env python3
"""
現在のExcelファイルで聖光学院のデータを確認する
"""

import pandas as pd
from pathlib import Path

def check_seiko_excel():
    """聖光学院のExcelデータを確認"""
    
    # 最新のバックアップファイルを使用
    backup_dir = Path("/Users/yoshiikatsuhiko/entrance_exam_analyzer/data/backups")
    excel_files = list(backup_dir.glob("*entrance_exam_database*.xlsx"))
    
    if not excel_files:
        print("Excelファイルが見つかりません")
        return
    
    # 最新のファイルを取得
    latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
    print(f"使用ファイル: {latest_file}")
    
    try:
        # シート名を確認
        with pd.ExcelFile(latest_file) as xls:
            sheet_names = xls.sheet_names
            print(f"Excelシート名: {sheet_names}")
            
            for sheet_name in sheet_names:
                print(f"\n=== {sheet_name} ===")
                df = pd.read_excel(latest_file, sheet_name=sheet_name)
                
                # 聖光学院のデータを検索
                seiko_data = df[df['学校名'].str.contains('聖光', na=False)]
                
                if not seiko_data.empty:
                    print(f"聖光学院のデータが見つかりました: {len(seiko_data)}件")
                    
                    for _, row in seiko_data.iterrows():
                        year = row.get('年度', 'N/A')
                        section_num = row.get('大問番号', 'N/A')
                        author = row.get('著者名', '')
                        work = row.get('作品名', '')
                        genre = row.get('ジャンル', '')
                        
                        if pd.notna(author) and author:
                            print(f"  {year}年 大問{section_num}: {author} 『{work}』 ({genre})")
                        else:
                            print(f"  {year}年 大問{section_num}: {genre}")
                else:
                    print("聖光学院のデータは見つかりませんでした")
                    
                # デバッグ: すべての学校名を表示
                print(f"このシートの学校名一覧:")
                unique_schools = df['学校名'].dropna().unique()[:10]  # 最初の10件だけ
                for school in unique_schools:
                    print(f"  - {school}")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_seiko_excel()