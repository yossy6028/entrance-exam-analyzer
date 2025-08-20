#!/usr/bin/env python3
"""
新形式のExcelファイルを確認する
"""

import pandas as pd

def check_new_excel():
    """新形式のExcelを確認"""
    
    excel_file = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database_new.xlsx"
    
    try:
        # シート名を確認
        with pd.ExcelFile(excel_file) as xls:
            sheet_names = xls.sheet_names
            print(f"Excelシート名: {sheet_names}")
            
            # 聖光学院シートを読み込み
            df = pd.read_excel(xls, sheet_name='聖光学院中学校')
            
            print(f"\n聖光学院中学校のデータ:")
            print(f"データ件数: {len(df)}")
            print(f"\n列名（最初の20列）:")
            for i, col in enumerate(df.columns[:20]):
                print(f"  {i+1}. {col}")
            
            # データの内容を確認
            for _, row in df.iterrows():
                year = row.get('年度', 'N/A')
                print(f"\n{year}年度の入試問題:")
                print(f"  総設問数: {row.get('総設問数', 0)}")
                print(f"  総文字数: {row.get('総文字数', 0):,}")
                
                print(f"\n文章セクション:")
                for i in range(1, 4):
                    author = row.get(f'文章{i}_著者', '')
                    work = row.get(f'文章{i}_作品', '')
                    if author or work:
                        print(f"  文章{i}: {author} 『{work}』")
                        print(f"    ジャンル: {row.get(f'文章{i}_ジャンル', '')}")
                        print(f"    テーマ: {row.get(f'文章{i}_テーマ', '')}")
                        print(f"    文字数: {row.get(f'文章{i}_文字数', 0):,}")
                        print(f"    設問数: {row.get(f'文章{i}_設問数', 0)}")
                
                print(f"\nその他セクション:")
                for i in range(1, 4):
                    type_name = row.get(f'その他{i}_種別', '')
                    if type_name:
                        print(f"  その他{i}: {type_name}")
                        author = row.get(f'その他{i}_著者', '')
                        work = row.get(f'その他{i}_作品', '')
                        if author or work:
                            print(f"    著者: {author} 『{work}』")
                        print(f"    ジャンル: {row.get(f'その他{i}_ジャンル', '')}")
                        print(f"    テーマ: {row.get(f'その他{i}_テーマ', '')}")
                        print(f"    文字数: {row.get(f'その他{i}_文字数', 0):,}")
                        print(f"    設問数: {row.get(f'その他{i}_設問数', 0)}")
                
                print(f"\n問題タイプ別統計:")
                print(f"  選択問題: {row.get('選択_問題数', 0)}問")
                print(f"  記述問題: {row.get('記述_問題数', 0)}問")
                print(f"  抜き出し問題: {row.get('抜き出し_問題数', 0)}問")
                print(f"  漢字問題: {row.get('漢字_問題数', 0)}問")
                print(f"  語句問題: {row.get('語句_問題数', 0)}問")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_new_excel()