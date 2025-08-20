#!/usr/bin/env python3
"""早稲田実業のExcelデータを詳細確認"""

import pandas as pd
from pathlib import Path

excel_file = Path("entrance_exam_database.xlsx")

if not excel_file.exists():
    print(f"❌ Excelファイルが見つかりません: {excel_file}")
    exit(1)

# 早稲田実業のシートを読み込み
df = pd.read_excel(excel_file, sheet_name="早稲田実業学校中等部")

print("📊 早稲田実業学校中等部 2015年データ")
print("=" * 60)

# 基本情報
print(f"年度: {df.iloc[0]['年度']}")
print(f"総設問数: {df.iloc[0]['総設問数']}")
print(f"総文字数: {df.iloc[0]['総文字数']}")
print(f"大問数: {df.iloc[0]['大問数']}")

print("\n📚 大問別情報:")
for i in range(1, 4):
    if f'大問{i}_ジャンル' in df.columns:
        print(f"\n大問{i}:")
        if pd.notna(df.iloc[0][f'大問{i}_ジャンル']):
            print(f"  ジャンル: {df.iloc[0][f'大問{i}_ジャンル']}")
        if pd.notna(df.iloc[0][f'大問{i}_テーマ']):
            print(f"  テーマ: {df.iloc[0][f'大問{i}_テーマ']}")
        if pd.notna(df.iloc[0][f'大問{i}_著者']):
            print(f"  著者: {df.iloc[0][f'大問{i}_著者']}")
        if pd.notna(df.iloc[0][f'大問{i}_作品']):
            print(f"  作品: {df.iloc[0][f'大問{i}_作品']}")
        if pd.notna(df.iloc[0][f'大問{i}_設問数']):
            print(f"  設問数: {df.iloc[0][f'大問{i}_設問数']}")

print("\n📝 設問タイプ別:")
for col in ['記述_問題数', '選択_問題数', '漢字・語句_問題数', '抜き出し_問題数']:
    if col in df.columns and pd.notna(df.iloc[0][col]):
        print(f"  {col.replace('_問題数', '')}: {df.iloc[0][col]}問")