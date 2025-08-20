#!/usr/bin/env python3
"""早稲田実業2015年の改善された分析をテスト"""

import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.universal_analyzer import UniversalAnalyzer
from models import ExamDocument

# OCRテキストファイル
ocr_file = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.ocr.txt")

if not ocr_file.exists():
    print(f"❌ ファイルが見つかりません: {ocr_file}")
    exit(1)

with open(ocr_file, 'r', encoding='utf-8') as f:
    text = f.read()

# ドキュメントを作成
document = ExamDocument(
    file_path=ocr_file,
    school_name="早稲田実業学校中等部",
    years=["2015"],
    content=text,
    encoding="utf-8"
)

# アナライザーを初期化
analyzer = UniversalAnalyzer()

# 分析実行
print("📊 早稲田実業2015年度の分析")
print("=" * 60)

result = analyzer.analyze(text, "早稲田実業学校中等部", "2015")

print(f"\n✅ 分析結果:")
print(f"  - 大問数: {result.get_section_count()}個")
print(f"  - 総設問数: {result.get_question_count()}問")
print(f"  - 総文字数: {result.total_characters:,}文字")

print(f"\n📚 大問の詳細:")
for i, section in enumerate(result.sections, 1):
    print(f"  大問{i}: {section.title}")
    print(f"    設問数: {section.question_count}問")
    if hasattr(section, 'text'):
        print(f"    文字数: {len(section.text) if section.text else 0}文字")

print(f"\n📖 出典情報:")
if result.sources:
    for i, source in enumerate(result.sources, 1):
        if source.author or source.title:
            print(f"  大問{i}:")
            if source.author:
                print(f"    著者: {source.author}")
            if source.title:
                print(f"    作品: {source.title}")
else:
    print("  出典が検出されませんでした")

print(f"\n📝 設問タイプ別:")
for q_type, count in result.question_types.items():
    if count > 0:
        print(f"  {q_type}: {count}問")

print(f"\n🎯 ジャンル: {result.genre}")
print(f"🎯 テーマ: {result.theme}")

# 期待される結果と比較
print("\n" + "=" * 60)
print("📋 期待される結果との比較:")
print(f"  大問数: {result.get_section_count()}個 / 期待値: 3個 {'✅' if result.get_section_count() == 3 else '❌'}")
print(f"  出典検出: {len([s for s in result.sources if s.author or s.title])}個 / 期待値: 2個 {'✅' if len([s for s in result.sources if s.author or s.title]) == 2 else '❌'}")