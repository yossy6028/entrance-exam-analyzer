#!/usr/bin/env python3
"""
強化された分析機能のテストスクリプト
出典情報と出題形式の判定精度を検証
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.enhanced_source_detector import EnhancedSourceDetector, SourceInfo
from modules.enhanced_question_type_analyzer import EnhancedQuestionTypeAnalyzer, QuestionInfo
import json


def test_source_detection():
    """出典情報検出のテスト"""
    print("=" * 60)
    print("出典情報検出テスト")
    print("=" * 60)
    
    detector = EnhancedSourceDetector()
    
    # テストケース
    test_cases = [
        # ケース1: 標準的な出典表記
        """
        太郎は窓の外を見つめていた。雨が静かに降り続いている。
        彼の心には、昨日の出来事が重くのしかかっていた。
        
        （山田太郎『雨の日の記憶』新潮社、より）
        """,
        
        # ケース2: 作品名が先のパターン
        """
        問題文の内容がここに入ります。
        様々な設問が続きます。
        
        （『星の王子さま』サン＝テグジュペリ）
        """,
        
        # ケース3: 出典：形式
        """
        本文の内容
        
        出典：夏目漱石『こころ』
        """,
        
        # ケース4: 複数の情報を含む
        """
        文章の内容
        
        （村上春樹『ノルウェイの森』講談社文庫、1991年）
        """
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nテストケース {i}:")
        print("-" * 40)
        
        sources = detector.extract_sources(text)
        
        for source in sources:
            print(f"著者: {source.author}")
            print(f"タイトル: {source.title}")
            print(f"出版社: {source.publisher}")
            print(f"年: {source.year}")
            print(f"ジャンル: {source.source_type}")
            print(f"信頼度: {source.confidence:.2f}")
            print()


def test_question_type_analysis():
    """出題形式判定のテスト"""
    print("\n" + "=" * 60)
    print("出題形式判定テスト")
    print("=" * 60)
    
    analyzer = EnhancedQuestionTypeAnalyzer()
    
    # テストケース
    test_cases = [
        # 選択式問題
        """
        問1 傍線部①「それは違う」について、太郎がこのように言った理由として最も適切なものを次のア～エから一つ選びなさい。
        
        ア. 自分の考えが正しいと信じていたから
        イ. 相手の意見に納得できなかったから
        ウ. 議論を続けたくなかったから
        エ. 別の案を持っていたから
        """,
        
        # 記述式問題（字数制限あり）
        """
        問2 傍線部②「彼女の表情が変わった」とありますが、なぜ彼女の表情が変わったのか、本文の内容をふまえて80字以内で説明しなさい。
        """,
        
        # 抜き出し問題
        """
        問3 太郎が最も驚いたことを表す一文を本文中から15字で抜き出しなさい。
        """,
        
        # 漢字問題
        """
        問4 次の傍線部の漢字の読みをひらがなで書きなさい。
        ① 彼は静寂を破った。
        ② 困難な状況に直面した。
        """,
        
        # 複合的な問題
        """
        問5 次の文章を読んで、後の問いに答えなさい。
        
        (1) この場面での主人公の心情を30字程度で説明しなさい。
        
        (2) 主人公がとった行動について、あなたはどう思いますか。自分の考えを100字以上120字以内で書きなさい。
        """
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nテストケース {i}:")
        print("-" * 40)
        
        result = analyzer.analyze_questions(text)
        
        print(f"総問題数: {result['total_questions']}")
        print("\n問題タイプ別集計:")
        for q_type, count in result['question_types'].items():
            print(f"  {q_type}: {count}問")
        
        print("\n個別問題の詳細:")
        for q in result['questions']:
            print(f"  問題番号: {q.number}")
            print(f"  タイプ: {q.type}")
            if q.subtype:
                print(f"  サブタイプ: {q.subtype}")
            if q.char_limit:
                print(f"  字数制限: {q.char_limit}")
            if q.choice_count:
                print(f"  選択肢数: {q.choice_count}")
            print(f"  信頼度: {q.confidence:.2f}")
            print()
        
        if result['statistics']:
            print("\n統計情報:")
            stats = result['statistics']
            print(f"  複雑度スコア: {stats.get('complexity_score', 0)}")
            if stats.get('average_char_limit'):
                print(f"  平均字数制限: {stats['average_char_limit']}字")
            if stats.get('average_choice_count'):
                print(f"  平均選択肢数: {stats['average_choice_count']}")


def test_with_real_file():
    """実際のファイルでテスト"""
    print("\n" + "=" * 60)
    print("実ファイルでのテスト")
    print("=" * 60)
    
    # テスト用のサンプルファイルを探す
    test_dir = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問")
    
    if not test_dir.exists():
        print("テストディレクトリが見つかりません")
        return
    
    # PDFファイルを探す（最初の1つ）
    pdf_files = list(test_dir.glob("**/*.pdf"))[:1]
    
    if not pdf_files:
        print("PDFファイルが見つかりません")
        return
    
    pdf_file = pdf_files[0]
    print(f"テストファイル: {pdf_file.name}")
    
    # OCR処理が必要な場合はここで実行
    # （既存のOCRモジュールを使用）
    
    # ここでは仮のテキストを使用
    sample_text = """
    【一】次の文章を読んで、後の問いに答えなさい。
    
    春の陽射しが窓から差し込む教室で、私は一人、本を読んでいた。
    クラスメイトたちは皆、校庭でサッカーをしているらしい。
    窓の外から聞こえる歓声が、静かな教室に響いてくる。
    
    問1 傍線部①について、主人公はなぜ一人で教室にいたのか、次のア～エから最も適切なものを一つ選びなさい。
    
    ア. 体調が悪かったから
    イ. 本を読みたかったから
    ウ. 友達がいなかったから
    エ. 先生に言われたから
    
    問2 この場面での主人公の心情を60字以内で説明しなさい。
    
    （芥川龍之介『或る日の午後』より）
    """
    
    # 出典情報を検出
    detector = EnhancedSourceDetector()
    sources = detector.extract_sources(sample_text)
    
    print("\n検出された出典情報:")
    for source in sources:
        print(f"  著者: {source.author}")
        print(f"  作品: {source.title}")
        print(f"  信頼度: {source.confidence:.2f}")
    
    # 出題形式を分析
    analyzer = EnhancedQuestionTypeAnalyzer()
    result = analyzer.analyze_questions(sample_text)
    
    print("\n出題形式分析結果:")
    print(f"  総問題数: {result['total_questions']}")
    for q_type, count in result['question_types'].items():
        if not '_' in q_type:  # サブタイプは除外
            print(f"  {q_type}: {count}問")


def main():
    """メイン処理"""
    print("強化された入試問題分析機能のテスト")
    print("=" * 60)
    
    # 各機能をテスト
    test_source_detection()
    test_question_type_analysis()
    test_with_real_file()
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()