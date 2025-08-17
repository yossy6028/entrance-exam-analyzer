#!/usr/bin/env python3
"""
出典情報抽出精度テスト
聖光学院のOCR結果を使って改善された出典抽出をテスト
"""
from pathlib import Path
from modules.enhanced_source_extractor import EnhancedSourceExtractor

def test_source_extraction():
    """聖光学院のOCR結果で出典抽出をテスト"""
    
    print("=" * 70)
    print("出典情報抽出精度テスト")
    print("=" * 70)
    
    # OCR結果テキストを読み込み
    text_file = Path("seiko_output/combined_seiko_text.txt")
    
    if not text_file.exists():
        print(f"エラー: {text_file} が見つかりません")
        return
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"テキスト文字数: {len(text):,}")
    print()
    
    # 出典抽出器を初期化
    extractor = EnhancedSourceExtractor()
    
    # 出典情報を抽出
    print("出典情報を抽出中...")
    sources = extractor.extract_sources_from_text(text)
    
    # 結果を表示
    print("\n" + "=" * 50)
    print("抽出結果")
    print("=" * 50)
    
    print(f"発見された出典: {len(sources['found_sources'])}件")
    
    for i, source in enumerate(sources['found_sources'], 1):
        print(f"\n【出典 {i}】")
        print(f"  著者: {source.get('author', 'なし')}")
        print(f"  作品: {source.get('title', 'なし')}")
        print(f"  信頼度: {source.get('confidence', 0):.2f}")
        print(f"  抽出元: {source.get('full_match', '')[:100]}...")
        if source.get('pattern_used'):
            print(f"  使用パターン: {source.get('pattern_used')}")
    
    if sources['author_candidates']:
        print(f"\n著者名候補: {sources['author_candidates'][:10]}")  # 最初の10件
    
    if sources['title_candidates']:
        print(f"\n作品タイトル候補:")
        for title in sources['title_candidates'][:5]:  # 最初の5件
            print(f"  - {title}")
    
    if sources['corrections_applied']:
        print(f"\n適用された修正: {sources['corrections_applied']}")
    
    # 改善された抽出の詳細分析
    print("\n" + "=" * 50)
    print("詳細分析")
    print("=" * 50)
    
    # 既知の出典と比較
    known_sources = [
        {'author': '森沢晴夫', 'title': '本が紡いだ五つの命題'},
        {'author': '???', 'title': '見えないキノコの動勉な日々'}  # OCR誤認識
    ]
    
    print("既知の出典情報:")
    for known in known_sources:
        print(f"  - {known['author']}: {known['title']}")
    
    print("\n抽出精度の評価:")
    
    # 第三問の出典をチェック
    novel_found = False
    for source in sources['found_sources']:
        if '森沢' in source.get('author', '') or '本が紡いだ' in source.get('title', ''):
            novel_found = True
            print(f"  ✅ 小説の出典検出: {source.get('author')} / {source.get('title')}")
            break
    
    if not novel_found:
        print("  ❌ 小説の出典が検出されませんでした")
    
    # 第四問の出典をチェック  
    essay_found = False
    for source in sources['found_sources']:
        title = source.get('title') or ''
        if 'キノコ' in title or '動勉' in title:
            essay_found = True
            print(f"  ⚠️ エッセイの出典検出（要修正）: {source.get('author')} / {title}")
            break
    
    if not essay_found:
        print("  ❌ エッセイの出典が検出されませんでした")

def test_individual_patterns():
    """個別パターンのテスト"""
    print("\n" + "=" * 50)
    print("個別パターンテスト")
    print("=" * 50)
    
    extractor = EnhancedSourceExtractor()
    
    # テストケース
    test_cases = [
        "森沢晴夫『本が紡いだ五つの命題』による",
        "選手担子「見えないキノコの動勉な日々」(同書』第九〇四号所収)による",
        "山田太郎の文章より",
        "次の文章は、田中花子『春の物語』の一節である。",
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n【テスト {i}】: {test_text}")
        
        sources = extractor.extract_sources_from_text(test_text)
        
        if sources['found_sources']:
            source = sources['found_sources'][0]
            print(f"  著者: {source.get('author')}")
            print(f"  作品: {source.get('title')}")
            print(f"  信頼度: {source.get('confidence')}")
        else:
            print("  出典なし")

if __name__ == "__main__":
    test_source_extraction()
    test_individual_patterns()
    
    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)