#!/usr/bin/env python3
"""
桜蔭中15年度国語問題の出典情報を抽出
"""
import re
from typing import Dict, List, Optional, Tuple


def extract_source_info(text: str) -> Dict:
    """テキストから出典情報を抽出"""
    
    result = {
        'school': '桜蔭中学校',
        'year': '2015年度（平成27年度）',
        'sources': []
    }
    
    # 出典パターン（括弧内の著者名「作品名」形式）
    # 複数のパターンに対応
    patterns = [
        # 標準パターン：（著者名「作品名」）
        r'（([^「）]+)「([^」]+)」）',
        # 作品名に『』が含まれるパターン：（著者名「作品名」『書籍名』）
        r'（([^「）]+)「([^」]+)」『([^』]+)』）',
        # 書籍名のみのパターン：（著者名『書籍名』）
        r'（([^『）]+)『([^』]+)』）'
    ]
    
    # 大問の境界を検出
    section1_match = re.search(r'一、次の文章を読んで、後の問いに答えなさい。', text)
    section2_match = re.search(r'二\s+次の文章を読んで、後の問いに答えなさい。', text)
    
    # 各大問の範囲を特定
    section1_start = section1_match.start() if section1_match else 0
    section2_start = section2_match.start() if section2_match else len(text) // 2
    
    # 大問一の出典を探す（大問一の開始から大問二の開始まで）
    section1_text = text[section1_start:section2_start]
    section1_source = None
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, section1_text))
        if matches:
            # 最初の出典を採用（通常は文章の最後にある）
            match = matches[0]
            if len(match.groups()) == 3:  # 作品名と書籍名がある場合
                section1_source = {
                    'section': 1,
                    'author': match.group(1).strip(),
                    'title': match.group(2).strip(),
                    'book': match.group(3).strip(),
                    'full_text': match.group(0)
                }
            elif len(match.groups()) == 2:
                if '「' in match.group(0):  # 作品名がある場合
                    section1_source = {
                        'section': 1,
                        'author': match.group(1).strip(),
                        'title': match.group(2).strip(),
                        'book': None,
                        'full_text': match.group(0)
                    }
                else:  # 書籍名のみの場合
                    section1_source = {
                        'section': 1,
                        'author': match.group(1).strip(),
                        'title': None,
                        'book': match.group(2).strip(),
                        'full_text': match.group(0)
                    }
            break
    
    # 大問二の出典を探す
    section2_text = text[section2_start:]
    section2_source = None
    
    # 大問二の文章の終わりを探す（問一の前まで）
    section2_end_match = re.search(r'問一[^\n]*①〜⑤のカタカナを正しい漢字に直しなさい', section2_text)
    if section2_end_match:
        section2_text_part = section2_text[:section2_end_match.start()]
    else:
        section2_text_part = section2_text
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, section2_text_part))
        if matches:
            # 最後の出典を採用（文章の最後にあるはず）
            match = matches[-1]
            if len(match.groups()) == 3:  # 作品名と書籍名がある場合
                section2_source = {
                    'section': 2,
                    'author': match.group(1).strip(),
                    'title': match.group(2).strip(),
                    'book': match.group(3).strip(),
                    'full_text': match.group(0)
                }
            elif len(match.groups()) == 2:
                if '「' in match.group(0):  # 作品名がある場合
                    section2_source = {
                        'section': 2,
                        'author': match.group(1).strip(),
                        'title': match.group(2).strip(),
                        'book': None,
                        'full_text': match.group(0)
                    }
                else:  # 書籍名のみの場合
                    section2_source = {
                        'section': 2,
                        'author': match.group(1).strip(),
                        'title': None,
                        'book': match.group(2).strip(),
                        'full_text': match.group(0)
                    }
            break
    
    # 結果に追加
    if section1_source:
        result['sources'].append(section1_source)
    if section2_source:
        result['sources'].append(section2_source)
    
    return result


def main():
    """メイン実行関数"""
    
    # 高精度テキストファイルを読み込み
    text_file = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭/15桜蔭.txt'
    
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 出典情報を抽出
        result = extract_source_info(text)
        
        # 結果表示
        print("\n=== 桜蔭中学校 2015年度 国語 出典情報 ===\n")
        
        for source in result['sources']:
            print(f"【大問{source['section']}】")
            print(f"著者: {source['author']}")
            if source['title']:
                print(f"作品名: 「{source['title']}」")
            if source['book']:
                print(f"書籍名: 『{source['book']}』")
            print(f"原文表記: {source['full_text']}")
            print()
        
        # 出典が見つからなかった場合の確認
        if len(result['sources']) < 2:
            print("\n⚠️ 一部の出典が見つかりませんでした。")
            print("デバッグ情報:")
            
            # すべての出典候補を表示
            all_patterns = [
                r'（[^）]+「[^」]+」[^）]*）',
                r'（[^）]+『[^』]+』[^）]*）'
            ]
            
            print("\nテキスト内のすべての出典候補:")
            for pattern in all_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    print(f"  - {match}")
                    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()