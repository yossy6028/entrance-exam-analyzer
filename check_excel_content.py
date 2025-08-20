#!/usr/bin/env python3
"""Excelファイルの内容を確認"""

import pandas as pd
from pathlib import Path

excel_file = Path("entrance_exam_database.xlsx")

if not excel_file.exists():
    print(f"❌ Excelファイルが見つかりません: {excel_file}")
    exit(1)

# Excelファイルを読み込み
with pd.ExcelFile(excel_file) as xls:
    print(f"📊 Excelファイル: {excel_file}")
    print(f"   シート数: {len(xls.sheet_names)}")
    print(f"   シート名: {', '.join(xls.sheet_names)}")
    
    # 各シートの内容を表示
    for sheet_name in xls.sheet_names:
        print(f"\n=== {sheet_name} ===")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"   行数: {len(df)}")
        print(f"   列数: {len(df.columns)}")
        
        # 列名を表示
        print("   列名:")
        for i, col in enumerate(df.columns, 1):
            print(f"     {i}. {col}")
        
        # データの概要を表示
        if len(df) > 0:
            print("\n   データ内容（最初の行）:")
            for col in df.columns[:10]:  # 最初の10列のみ表示
                value = df.iloc[0][col]
                if pd.notna(value):
                    print(f"     {col}: {value}")