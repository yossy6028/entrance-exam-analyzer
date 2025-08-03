#!/usr/bin/env python3
"""
bunkoOCRの渋渋15年度の結果を結合して保存
"""
from pathlib import Path

def combine_bunko_ocr_results():
    """最新のbunkoOCR結果を結合"""
    
    # 最新の結果フォルダ
    results_dir = Path("/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results/94F5B795-7295-4E86-89E1-838668C94095")
    
    if not results_dir.exists():
        print(f"エラー: フォルダが見つかりません: {results_dir}")
        return None
    
    # text*.txtファイルを取得
    text_files = sorted(results_dir.glob("text*.txt"))
    print(f"見つかったテキストファイル: {len(text_files)}個")
    
    # 各ファイルの内容を結合
    combined_text = []
    for txt_file in text_files:
        print(f"読み込み: {txt_file.name}")
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_text.append(f"=== {txt_file.name} ===\n{content}\n")
    
    # 結合したテキストを保存
    output_file = "15渋渋_bunko.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined_text))
    
    print(f"\n✅ 結合完了: {output_file}")
    print(f"総文字数: {sum(len(t) for t in combined_text)}文字")
    
    return output_file

if __name__ == "__main__":
    output_file = combine_bunko_ocr_results()
    
    if output_file:
        print(f"\n次のステップ:")
        print(f"python analyze_shibuya_2015.py")