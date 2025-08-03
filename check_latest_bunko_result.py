#!/usr/bin/env python3
"""
最新のbunkoOCR結果を確認して開成中2025年を分析
"""
from pathlib import Path
import subprocess
from datetime import datetime


def check_and_analyze_latest():
    """最新のbunkoOCR結果を確認して分析"""
    
    print("\n📁 最新のbunkoOCR結果を確認中...")
    
    # bunkoOCR結果フォルダ
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    
    if not results_dir.exists():
        print("❌ bunkoOCR結果フォルダが見つかりません")
        return
    
    # 最新のフォルダを取得
    folders = [d for d in results_dir.iterdir() if d.is_dir()]
    if not folders:
        print("❌ 結果フォルダが見つかりません")
        return
    
    # 最新のフォルダ
    latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
    
    # 作成時刻を確認
    mtime = datetime.fromtimestamp(latest_folder.stat().st_mtime)
    print(f"✅ 最新フォルダ: {latest_folder.name}")
    print(f"   作成時刻: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テキストファイルを確認
    text_files = sorted(latest_folder.glob("text*.txt"))
    if not text_files:
        print("❌ テキストファイルが見つかりません")
        return
    
    print(f"✅ テキストファイル数: {len(text_files)}")
    
    # 最初のページを確認
    with open(text_files[0], 'r', encoding='utf-8') as f:
        first_page = f.read()[:200]
        print(f"\n📄 最初のページの内容:")
        print(first_page)
    
    # 開成中学校かどうか確認
    is_kaisei = False
    for txt_file in text_files[:3]:  # 最初の3ページをチェック
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "開成" in content or "令和七年度" in content:
                is_kaisei = True
                break
    
    if not is_kaisei:
        print("\n⚠️  開成中学校のPDFではない可能性があります")
        print("それでも続行しますか？ (y/n): ", end='')
        # 自動で続行
        print("y (自動続行)")
    
    # テキストを結合
    print("\n📝 テキストファイルを結合中...")
    combined_text = []
    for txt_file in text_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_text.append(f"=== {txt_file.name} ===\n{content}")
    
    # 結合したテキストを保存
    output_file = "開成2025_bunko.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(combined_text))
    
    print(f"✅ 結合テキストを保存: {output_file}")
    print(f"   総文字数: {len(''.join(combined_text))}文字")
    
    # 分析スクリプトを実行
    print("\n🔍 分析を開始します...")
    if Path("analyze_kaisei_2025_bunko.py").exists():
        subprocess.run(['python', 'analyze_kaisei_2025_bunko.py'])
    else:
        print("❌ 分析スクリプトが見つかりません")
        print("手動で analyze_kaisei_2025_bunko.py を実行してください")


if __name__ == "__main__":
    check_and_analyze_latest()