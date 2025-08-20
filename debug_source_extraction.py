#!/usr/bin/env python3
"""
出典抽出のデバッグ
"""
import re

def debug_source_patterns():
    """出典パターンのデバッグ"""
    
    # テストテキスト
    test_texts = [
        "(北杜夫の文章による)",
        "(岩田規久男『経済学を学ぶ』による)"
    ]
    
    # パターン
    patterns = [
        r'\(([^)]+)の文による\)',  # 半角括弧版
        r'（([^）]+)の文による）',   # 全角括弧版
        r'\(([^)]+)の文章による\)', # 半角括弧「文章」版
        r'（([^）]+)の文章による）',  # 全角括弧「文章」版
        r'\(([^)]+)『([^』]+)』による\)',  # 半角「(著者『作品』による)」
        r'（([^）]+)『([^』]+)』による）',  # 全角「(著者『作品』による)」
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"テスト{i}: {text}")
        for j, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, text)
            if matches:
                print(f"  パターン{j}: {pattern}")
                print(f"  マッチ: {matches}")
        print()

if __name__ == "__main__":
    debug_source_patterns()