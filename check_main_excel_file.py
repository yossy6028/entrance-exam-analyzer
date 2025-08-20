#!/usr/bin/env python3
"""
メインExcelファイルで聖光学院のデータを確認する
"""

import pandas as pd

def check_main_excel():
    """メインExcelファイルで聖光学院のデータを確認"""
    
    excel_file = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database.xlsx"
    
    try:
        # シート名を確認
        with pd.ExcelFile(excel_file) as xls:
            sheet_names = xls.sheet_names
            print(f"Excelシート名: {sheet_names}")
            
            for sheet_name in sheet_names:
                print(f"\n=== {sheet_name} ===")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                print(f"データ件数: {len(df)}")
                print(f"列名: {list(df.columns)}")
                
                # 聖光学院のデータを検索
                seiko_data = df[df['学校名'].str.contains('聖光', na=False)]
                
                if not seiko_data.empty:
                    print(f"\n聖光学院のデータが見つかりました: {len(seiko_data)}件")
                    
                    for _, row in seiko_data.iterrows():
                        year = row.get('年度', 'N/A')
                        section_num = row.get('大問番号', 'N/A')
                        author = row.get('著者名', '')
                        work = row.get('作品名', '')
                        genre = row.get('ジャンル', '')
                        theme = row.get('テーマ', '')
                        char_count = row.get('文字数', 'N/A')
                        
                        if pd.notna(author) and author:
                            print(f"  {year}年 大問{section_num}: {author} 『{work}』")
                        else:
                            print(f"  {year}年 大問{section_num}: {genre}")
                        print(f"    ジャンル: {genre}, テーマ: {theme}, 文字数: {char_count}")
                else:
                    print("聖光学院のデータは見つかりませんでした")
                    
                # デバッグ: 全データの最初の3行を表示
                print(f"\n全データの例（最初の3行）:")
                for i, (_, row) in enumerate(df.head(3).iterrows()):
                    school = row.get('学校名', 'N/A')
                    year = row.get('年度', 'N/A')
                    section = row.get('大問番号', 'N/A')
                    print(f"  {i+1}. {school} {year}年 大問{section}")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_main_excel()