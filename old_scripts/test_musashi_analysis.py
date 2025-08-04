#!/usr/bin/env python3
"""
武蔵14-25.txtの分析テスト
"""
from pathlib import Path
import json
from modules.year_detector import YearDetector
from modules.school_detector import SchoolDetector
from modules.text_analyzer import TextAnalyzer
from plugins.musashi_plugin import MusashiPlugin
from utils.text_utils import detect_encoding

def analyze_musashi_file():
    """武蔵14-25.txtを分析"""
    
    file_path = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/武蔵中学校/武蔵14-25.txt")
    
    # エンコーディング検出
    encoding = detect_encoding(file_path)
    print(f"エンコーディング: {encoding}\n")
    
    # ファイル読み込み
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    
    print(f"総文字数: {len(content):,}\n")
    
    # 年度検出
    year_detector = YearDetector()
    year_result = year_detector.detect_years(content, file_path)
    
    print("=== 検出された年度 ===")
    print(f"年度リスト: {year_result.years}")
    print(f"信頼度: {year_result.confidence:.1%}")
    print()
    
    # 学校名検出
    school_detector = SchoolDetector()
    school_name, confidence = school_detector.detect_school(content, file_path)
    print(f"検出された学校: {school_name} (信頼度: {confidence:.1%})\n")
    
    # 年度ごとにテキストを分割
    year_texts = year_detector.split_text_by_years(content, year_result.years)
    
    print("=== 年度ごとの分析結果 ===\n")
    
    # プラグインを使用して分析
    plugin = MusashiPlugin()
    
    results = []
    for year in sorted(year_texts.keys()):
        text = year_texts[year]
        print(f"--- {year}年 ---")
        print(f"テキスト長: {len(text):,}文字")
        
        # プラグインで分析
        result = plugin.analyze(text, school_name, year)
        
        print(f"大問数: {result.get_section_count()}")
        print(f"総設問数: {result.get_question_count()}")
        
        # 設問タイプ
        print("設問タイプ:")
        for q_type, count in result.question_types.items():
            if count > 0:
                print(f"  {q_type}: {count}問")
        
        # 出典情報
        if result.sources:
            print("出典:")
            for i, source in enumerate(result.sources, 1):
                if source.author or source.title:
                    info = f"  大問{i}: "
                    if source.author:
                        info += f"著者={source.author}"
                    if source.title:
                        if source.author:
                            info += f", "
                        info += f"作品=『{source.title}』"
                    print(info)
                elif source.raw_source:
                    print(f"  大問{i}: {source.raw_source[:50]}...")
        
        # テーマとジャンル
        if result.theme:
            print(f"テーマ: {result.theme}")
        if result.genre:
            print(f"ジャンル: {result.genre}")
        
        print()
        
        # 結果を保存
        results.append({
            'year': year,
            'total_characters': len(text),
            'sections': result.get_section_count(),
            'questions': result.get_question_count(),
            'question_types': result.question_types,
            'sources': [
                {
                    'author': s.author,
                    'title': s.title,
                    'raw': s.raw_source[:100] if s.raw_source else None
                }
                for s in result.sources
            ],
            'theme': result.theme,
            'genre': result.genre
        })
    
    # 結果をJSONファイルに保存
    with open('musashi_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n結果をmusashi_analysis_results.jsonに保存しました")
    
    return results

if __name__ == "__main__":
    analyze_musashi_file()