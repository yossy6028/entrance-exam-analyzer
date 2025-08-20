#!/usr/bin/env python3
"""
歴史的パターンマッチングのデバッグ
"""

import re
import sys
import os

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_pattern_matching():
    """歴史的パターンマッチングのデバッグ"""
    print("=== 歴史的パターンマッチングのデバッグ ===\n")
    
    test_text = """令和7年度入学試験問題
本校は創立記念: 2000年設立の伝統校です。
平成15年に校舎を建設しました。
"""
    
    historical_patterns = [
        r'平成\d{1,2}年[にで]',          # 平成15年に、平成27年で
        r'昭和\d{1,2}年[にで]',          # 昭和60年に、昭和50年で
        r'西暦\d{4}年[のに]',            # 西暦2000年の、西暦1995年に  
        r'\d{4}年[のに]起[きこ]',        # 2000年に起きた、1995年に起こった
        r'\d{4}年[のに]制定',           # 2000年に制定された
        r'創立[記念]*[:\s]*\d{4}年[設立]', # 創立記念: 2000年設立、創立 1995年設立
        r'\d{4}年[のに][設建]',         # 2000年に設立、1995年に建設
        r'\d{4}年[のに].*?事[件変]',     # 2000年に起きた事件（非貪欲マッチ）
        r'\d{4}年[設建][立設]',         # 2000年設立、1995年建設
        r'平成\d{1,2}年[のに].*?[建設]',  # 平成15年に校舎を建設
    ]
    
    print(f"テストテキスト:\n{test_text}")
    print("-" * 50)
    
    for i, pattern in enumerate(historical_patterns, 1):
        print(f"パターン {i}: {pattern}")
        matches = list(re.finditer(pattern, test_text))
        
        if matches:
            for match in matches:
                print(f"  マッチ: '{match.group(0)}' (位置: {match.start()})")
                
                # 年度抽出
                year_match = re.search(r'\d{4}', match.group(0))
                if year_match:
                    year = year_match.group(0)
                    print(f"    抽出年度: {year}")
        else:
            print(f"  マッチなし")
        print()
    
    # より効果的なパターンを試す
    print("=== 改良版パターンのテスト ===")
    
    improved_patterns = [
        (r'創立.*?(\d{4})年', '創立関連年度'),
        (r'(\d{4})年設立', '設立年度'),
        (r'平成(\d{1,2})年に.*?建設', '平成建設年'),
        (r'(\d{4})年に.*?建設', '建設年度'),
    ]
    
    for pattern, description in improved_patterns:
        print(f"{description}: {pattern}")
        matches = list(re.finditer(pattern, test_text))
        
        if matches:
            for match in matches:
                print(f"  マッチ: '{match.group(0)}' (位置: {match.start()})")
                if len(match.groups()) > 0:
                    print(f"    グループ1: '{match.group(1)}'")
        else:
            print(f"  マッチなし")
        print()

def test_context_keywords():
    """文脈キーワードの効果をテスト"""
    print("=== 文脈キーワード判定のテスト ===")
    
    test_text = """令和7年度入学試験問題
本校は創立記念: 2000年設立の伝統校です。
平成15年に校舎を建設しました。
"""
    
    detected_positions = {
        '2000': 21,  # 創立記念: 2000年設立
        '2025': 0,   # 令和7年度入学試験問題
        '2003': 36,  # 平成15年に校舎を建設
    }
    
    test_keywords = ['入学試験', '年度', '試験問題', '合格', '募集']
    
    for year, pos in detected_positions.items():
        print(f"年度 {year} (位置 {pos}):")
        
        context_start = max(0, pos - 30)
        context_end = min(len(test_text), pos + 50)
        context = test_text[context_start:context_end]
        
        print(f"  文脈: '{context.replace(chr(10), ' ')}'")
        
        for keyword in test_keywords:
            if keyword in context:
                print(f"    キーワード '{keyword}' が含まれる")
        
        # この年度は試験年度か？
        has_test_keywords = any(keyword in context for keyword in test_keywords)
        print(f"    試験年度判定: {has_test_keywords}")
        
        # より詳細な文脈分析
        is_historical = any(marker in context for marker in ['設立', '建設', '創立', 'について', 'の出来事'])
        print(f"    歴史的文脈: {is_historical}")
        
        print()

if __name__ == "__main__":
    debug_pattern_matching()
    test_context_keywords()