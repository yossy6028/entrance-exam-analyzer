#!/usr/bin/env python3
"""
複数年度誤検出問題のデバッグスクリプト
聖光学院のPDFで2000, 2015, 2025が検出される問題を調査
"""

import re
import sys
import os
from pathlib import Path

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector
from config.settings import Settings

def analyze_problematic_patterns():
    """問題のある年度検出パターンを分析"""
    print("=== 複数年度誤検出問題の分析 ===\n")
    
    detector = YearDetector()
    
    # 聖光学院のPDFに含まれそうなテキストパターンを模擬
    test_texts = [
        # 実際の年度
        "二〇二五年度入学試験問題",
        "2025年度入学試験問題", 
        "令和7年度入学試験問題",
        
        # 誤検出の原因になりそうなパターン
        "第15回模擬試験",
        "問題15番",
        "平成15年創立",
        "開校記念日(2000年)",
        "創立記念 2000年設立",
        "設問番号: 15",
        "ページ番号: 25",
        "受験番号: 2000",
        "生徒番号: 15班",
        "クラス番号: 25組",
        "試験時間: 25分",
        "(15)",  # 括弧内の数字
        "[2000]",  # 角括弧内の数字
        "15章",
        "25問",
        
        # 複合パターン
        "二〇二五年度入学試験問題\n第15回模擬試験\n平成15年創立記念\n受験番号2000番",
        
        # 歴史関連での年号
        "西暦2000年の出来事",
        "平成15年に起きた事件",
        "2015年の歴史問題",
        
        # 数学問題での数字
        "2000mの距離を歩く",
        "15個のリンゴ",
        "25人の生徒",
        
        # OCRエラーによる誤検出の可能性
        "二○二五年度",  # 〇の代わりに○
        "ニ〇二五年度",  # 二の代わりにニ
        "2O25年度",      # 0の代わりにO
        "２０２５年度",    # 全角数字
    ]
    
    print("各テストケースでの年度検出結果:\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"【テストケース {i}】")
        print(f"入力テキスト: {repr(text)}")
        
        try:
            result = detector.detect_years(text)
            print(f"検出年度: {result.years}")
            print(f"信頼度: {result.confidence:.2f}")
            print(f"検出パターン: {result.detection_patterns}")
            
            # 複数年度が検出された場合は詳細分析
            if len(result.years) > 1:
                print("⚠️  複数年度が検出されました！")
                analyze_pattern_details(detector, text, result)
                
        except Exception as e:
            print(f"エラー: {e}")
        
        print("-" * 60)

def analyze_pattern_details(detector, text, result):
    """複数年度検出の詳細分析"""
    print("\n【詳細分析】")
    
    # 各パターンでのマッチを詳細確認
    for pattern_obj in detector.patterns:
        matches = list(pattern_obj.compiled.finditer(text))
        if matches:
            print(f"\n{pattern_obj.name} (優先度: {pattern_obj.priority}):")
            for match in matches:
                try:
                    converted_year = pattern_obj.converter(match.group(1))
                    is_valid = detector._is_valid_year(converted_year)
                    match_context = get_match_context(text, match)
                    
                    print(f"  - マッチ: '{match.group(0)}' -> '{converted_year}' (有効: {is_valid})")
                    print(f"    位置: {match.start()}-{match.end()}")
                    print(f"    前後文脈: ...{match_context}...")
                    
                except Exception as e:
                    print(f"  - マッチエラー: '{match.group(0)}' -> {e}")

def get_match_context(text, match, context_length=20):
    """マッチ部分の前後文脈を取得"""
    start = max(0, match.start() - context_length)
    end = min(len(text), match.end() + context_length)
    return text[start:end].replace('\n', '\\n')

def test_specific_problematic_patterns():
    """特定の問題パターンをテスト"""
    print("\n=== 特定問題パターンの分析 ===\n")
    
    detector = YearDetector()
    
    # 2桁年度パターンの問題を調査
    pattern_2digit = detector.patterns[6]  # year_2digit パターン
    print(f"2桁年度パターン: {pattern_2digit.pattern}")
    print(f"優先度: {pattern_2digit.priority}")
    
    problematic_texts = [
        "問題番号15",
        "設問(15)",
        "第15問",
        "15年度",  # これは検出されるべき
        "平成15年度", # これも検出されるべき
        "設立2000年", # 微妙なケース
        "2000年度", # これは検出されるべき
        "西暦2000年の出来事について", # 文脈的に年度ではない
        "受験番号: 2000", # これは年度ではない
        "(25)", # 括弧内
        "25年度", # これは検出されるべき
        "試験時間25分", # これは年度ではない
    ]
    
    print("2桁パターンでの検出テスト:")
    for text in problematic_texts:
        matches = list(pattern_2digit.compiled.finditer(text))
        print(f"'{text}' -> {len(matches)}件マッチ: ", end="")
        for match in matches:
            converted = detector._two_digit_to_year(match.group(1))
            is_valid = detector._is_valid_year(converted)
            print(f"[{match.group(0)} -> {converted} ({'有効' if is_valid else '無効'})]", end=" ")
        print()

def analyze_regex_patterns():
    """正規表現パターンの詳細分析"""
    print("\n=== 正規表現パターン分析 ===\n")
    
    # 問題のある2桁年度パターンを分析
    pattern = r'(?<![(\d\n平成令和])(\d{2})年度?(?![)\d])'
    print(f"2桁年度パターン: {pattern}")
    
    test_cases = [
        "15年度",        # 検出されるべき (OK)
        "(15)年度",      # 検出されるべきでない (括弧内)
        "平成15年度",    # 検出されるべきでない (平成の後)
        "令和15年度",    # 検出されるべきでない (令和の後)  
        "問題15年度",    # 検出される？(微妙)
        "設立2000年",    # 検出される？(微妙)
        "115年度",       # 検出されるべきでない (3桁数字の一部)
        "15年度生",      # 検出される？
        "第15年度",      # 検出される？
        "15",           # 検出されるべきでない (年度の文字がない)
        "15年",         # 検出される
        "15度",         # 検出されるべきでない
    ]
    
    compiled_pattern = re.compile(pattern)
    
    print("各テストケースでのマッチング結果:")
    for test_case in test_cases:
        matches = list(compiled_pattern.finditer(test_case))
        match_count = len(matches)
        match_results = [match.group(1) for match in matches]
        print(f"'{test_case}' -> {match_count}件: {match_results}")

def suggest_improvements():
    """改善案の提案"""
    print("\n=== 改善案 ===\n")
    
    print("1. 2桁年度パターンの改良案:")
    print("   現在: r'(?<![(\d\n平成令和])(\d{2})年度?(?![)\d])'")
    print("   改良案1: r'(?<![(\d\n平成令和問題設問第])(\d{2})年度(?![)\d分問])'")
    print("   - '問題', '設問', '第'の後の数字を除外")
    print("   - '年度'を必須にし、'分'や '問'の前の数字を除外")
    
    print("\n2. 文脈を考慮した除外パターンの追加:")
    print("   - '問題\\d{1,2}' : 問題番号")
    print("   - '設問\\d{1,2}' : 設問番号") 
    print("   - '第\\d{1,2}回' : 回数")
    print("   - '受験番号\\d+' : 受験番号")
    print("   - '\\d+分' : 時間")
    print("   - '\\d+問' : 問題数")
    print("   - '\\d+人' : 人数")
    print("   - '\\d+個' : 個数")
    print("   - '\\d+[mMメートル]' : 距離")
    
    print("\n3. 優先度の調整:")
    print("   - 明確な年度表記（令和、平成、4桁西暦）の優先度を上げる")
    print("   - 2桁年度の優先度を下げ、他パターンとの重複時は除外")
    
    print("\n4. 信頼度計算の改良:")
    print("   - 複数パターンで同じ年度が検出された場合の信頼度向上")
    print("   - 文脈に基づく信頼度調整（問題番号vs年度）")

if __name__ == "__main__":
    analyze_problematic_patterns()
    test_specific_problematic_patterns()
    analyze_regex_patterns()
    suggest_improvements()