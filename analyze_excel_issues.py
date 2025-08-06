#!/usr/bin/env python3
"""
Excelデータベースの問題点を詳細に分析するスクリプト
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_excel_issues():
    """Excelデータベースの問題点を分析"""
    
    # Excelファイルを読み込み
    excel_file = pd.ExcelFile('entrance_exam_database.xlsx')
    
    print("="*70)
    print("Excel入試データベース 問題分析レポート")
    print("="*70)
    print(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 各シートを分析
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name)
        
        print(f"\n【{sheet_name}】")
        print("-"*50)
        print(f"データ件数: {len(df)}件")
        print(f"列数: {len(df.columns)}列")
        
        # 問題点のチェック
        issues = []
        
        # 1. 大問データの欠損チェック
        for col in df.columns:
            if '大問' in col:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    issues.append(f"  ⚠️ {col}: {null_count}/{len(df)}件が欠損")
        
        # 2. 設問数の整合性チェック
        if all(col in df.columns for col in ['記述_問題数', '選択_問題数', '漢字・語句_問題数', '抜き出し_問題数', '総設問数']):
            for idx, row in df.iterrows():
                total = 0
                for col in ['記述_問題数', '選択_問題数', '漢字・語句_問題数', '抜き出し_問題数']:
                    if pd.notna(row[col]):
                        total += row[col]
                
                if pd.notna(row['総設問数']) and total != row['総設問数']:
                    issues.append(f"  ⚠️ {row['年度']}年: 設問数合計({total}) ≠ 総設問数({row['総設問数']})")
        
        # 3. 列構造の不一致チェック
        expected_cols = ['年度', '総設問数', '総文字数', '大問数']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"  ⚠️ 必須列が欠落: {', '.join(missing_cols)}")
        
        # 問題点の表示
        if issues:
            print("\n発見された問題:")
            for issue in issues:
                print(issue)
        else:
            print("  ✅ 問題なし")
        
        # データサンプルの表示
        print(f"\nデータサンプル（最初の3件）:")
        if len(df) > 0:
            for idx, row in df.head(3).iterrows():
                print(f"  {row['年度']}年: ", end="")
                if '大問1_著者' in df.columns and pd.notna(row.get('大問1_著者')):
                    print(f"{row.get('大問1_著者', 'N/A')} - {row.get('大問1_作品', 'N/A')}")
                else:
                    print("著者・作品情報なし")
    
    print("\n" + "="*70)
    print("推奨される修正方針:")
    print("-"*50)
    print("1. 大問別のデータ（ジャンル、テーマ、著者、作品等）が全て欠損")
    print("   → OCR結果から再分析が必要")
    print("2. 列構造が学校ごとに異なる")
    print("   → 統一されたスキーマに修正が必要")
    print("3. データの整合性が取れていない")
    print("   → バリデーションロジックの実装が必要")
    print("="*70)

if __name__ == "__main__":
    analyze_excel_issues()