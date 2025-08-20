#!/usr/bin/env python3
"""
聖光学院のExcelデータを詳細確認する
"""

import pandas as pd

def check_seiko_detail():
    """聖光学院のExcelデータを詳細確認"""
    
    excel_file = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/entrance_exam_database.xlsx"
    
    try:
        # 聖光学院シートを読み込み
        df = pd.read_excel(excel_file, sheet_name='聖光学院中学校')
        
        print("聖光学院中学校のデータ:")
        print(f"データ件数: {len(df)}")
        
        for _, row in df.iterrows():
            year = row.get('年度', 'N/A')
            total_questions = row.get('総設問数', 'N/A')
            total_chars = row.get('総文字数', 'N/A')
            total_sections = row.get('大問数', 'N/A')
            
            print(f"\n{year}年度の入試問題:")
            print(f"  総設問数: {total_questions}")
            print(f"  総文字数: {total_chars:,}" if isinstance(total_chars, int) else f"  総文字数: {total_chars}")
            print(f"  大問数: {total_sections}")
            
            print(f"\n各大問の詳細:")
            for i in range(1, int(total_sections) + 1):
                genre = row.get(f'大問{i}_ジャンル', 'N/A')
                theme = row.get(f'大問{i}_テーマ', 'N/A')
                author = row.get(f'大問{i}_著者', '')
                work = row.get(f'大問{i}_作品', '')
                questions = row.get(f'大問{i}_設問数', 'N/A')
                chars = row.get(f'大問{i}_文字数', 'N/A')
                
                if pd.notna(author) and author:
                    print(f"  大問{i}: {author} 『{work}』")
                else:
                    print(f"  大問{i}: {genre}")
                
                print(f"    ジャンル: {genre}")
                print(f"    テーマ: {theme}")
                print(f"    設問数: {questions}")
                print(f"    文字数: {chars:,}" if isinstance(chars, int) else f"    文字数: {chars}")
            
            # 問題タイプ別統計
            print(f"\n問題タイプ別統計:")
            print(f"  選択問題: {row.get('選択_問題数', 'N/A')}問")
            print(f"  記述問題: {row.get('記述_問題数', 'N/A')}問")
            print(f"  抜き出し問題: {row.get('抜き出し_問題数', 'N/A')}問")
            print(f"  漢字問題: {row.get('漢字_問題数', 'N/A')}問")
            print(f"  語句問題: {row.get('語句_問題数', 'N/A')}問")
            
            # 更新日時
            update_time = row.get('更新日時', 'N/A')
            print(f"  更新日時: {update_time}")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_seiko_detail()