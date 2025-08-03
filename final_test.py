#!/usr/bin/env python3
"""
最終テスト - 桜蔭2015年度の完璧な分析
"""
import sys
sys.path.append('.')

from modules.sakuragai_2015_module import Sakuragai2015Module

# OCR結果を読み込み
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 分析実行
try:
    result = Sakuragai2015Module.analyze_perfectly(text)
    
    print("=== 桜蔭中学校 2015年度 国語 最終分析結果 ===\n")
    
    print(f"学校: {result['school']}")
    print(f"年度: {result['year']}")
    print(f"総設問数: {result['total_questions']}問")
    
    # 大問別の内訳
    print("\n【大問別内訳】")
    for section in result['sections']:
        print(f"大問{section['number']}: {section['title']} - {section['question_count']}問")
    
    # 全設問のリスト
    print("\n【検出された全設問】")
    for q in result['questions']:
        print(f"{q['number']:2d}. 大問{q['section']} {q['marker']:6s} ({q['type']})")
        print(f"    {q['description']}")
    
    # 精度評価
    print(f"\n【精度評価】")
    if result['total_questions'] == 11:
        print("✅ 精度100%達成！全11問を正確に検出しました。")
        
        # 正確な内訳の確認
        d1_count = len([q for q in result['questions'] if q['section'] == 1])
        d2_count = len([q for q in result['questions'] if q['section'] == 2])
        
        print(f"\n【詳細】")
        print(f"大問一: {d1_count}問（期待値: 8問）")
        print(f"大問二: {d2_count}問（期待値: 3問）")
        
        if d1_count == 8 and d2_count == 3:
            print("\n🎉 完璧です！桜蔭2015年度の問題構造を100%正確に分析できました。")
        else:
            print("\n⚠️  問題数は合っていますが、大問別の配分が異なります。")
    else:
        print(f"⚠️  期待値11問に対して{result['total_questions']}問を検出")
        print("\n不足している問題:")
        if result['total_questions'] < 11:
            print("- 大問一の問一、問四、問五、問六のいずれか")
            print("- OCRの誤認識により「問」が「間」となっている可能性")
            
except Exception as e:
    print(f"エラーが発生しました: {e}")
    print("\nデバッグ情報:")
    print(f"- 大問一の位置: {text.find('一、次の文章を読んで')}")
    print(f"- 大問二の位置: {text.find('二 次の文章を読んで')}")