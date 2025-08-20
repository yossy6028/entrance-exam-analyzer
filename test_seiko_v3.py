#!/usr/bin/env python3
"""
聖光学院の国語問題を新しいセクション分割ロジックv3でテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.section_splitter_v3 import ImprovedSectionSplitterV3
from processors.source_processor import SourceProcessor

def test_seiko_problem():
    """聖光学院の実際の問題でテスト"""
    
    # テストデータ（実際のOCR結果のサンプル）
    # 実際には完全なOCR結果を使用しますが、ここでは構造を確認するための簡略版
    test_text = """一、次の漢字の読みがなを書きなさい。

    1、放送で指示があるまで、この冊子を開いてはいけません。
    2、この冊子は27ページまであります。
    3、問題について質問は受け付けません。
    4、下書きには下書き欄や余白を使いなさい。
    5、字数指定のある問題では、句読点や力ッコなども字数に含みます。

    聖光学院中学校

    二、次の語句について答えなさい。

    1、次の①～⑤の文の線部の方カタカナを、それぞれ漢字に直しなさい。
    
    ① 地方経済の活性化と自精して、新技術の開発事業に取りシコウンする。
    ② 生徒会長に選ばれた僕は、全校生徒に就任にあたってのショカンを述べた。
    ③ 上級生たちはイベント運営のトウジ者として、 悩みながらも臨機応変な動きを見せていた。
    ④ 彼女の豊富なアイデイアのケンセンは、日々の読書の中にある。
    ⑤ 生徒会長選挙では、彼が全校生徒にミトめられた。

    三、次の文章を読んで、後の問いに答えなさい。

    津山は、俺の小刻みに音を振って古定した。
    「ほぼ」
    「じゃあ、書きません」なととと音を縦に振って否定したわけではない。「ほぼ」という危険なことをしている。これまでいろんな文献に目を通してきて、「ほぼ」という言葉は実に危険だということを知った。
    
    （中略 - 実際には3000～4000文字程度の本文が続く）
    
    森谷美「本が新しい五五の希望」による

    問一　傍線部①「それ」とは何を指しますか。
    問二　傍線部②について、筆者の考えを説明しなさい。
    問三　この文章の主題を60字以内で書きなさい。

    四、次の文章を読んで、後の問いに答えなさい。

    津山は生き方が不器用で、人付き合いが苦手だった。
    
    （中略 - 実際には3000～4000文字程度の本文が続く）
    
    津山さん『私たちが見ていること』（『図書』第九〇四号所収）による

    問一　漢字の読みを答えなさい。
    問二　空欄に入る語句を選びなさい。
    問三　筆者の主張をまとめなさい。
    
    五、次の問題に答えなさい。
    
    問一　次の慣用句の意味として最も適切なものを選びなさい。
    問二　次の四字熟語を完成させなさい。
    """
    
    # セクション分割のテスト
    print("=" * 60)
    print("セクション分割テスト（v3）")
    print("=" * 60)
    
    splitter = ImprovedSectionSplitterV3()
    sections = splitter.split_sections(test_text)
    
    print(f"\n検出された大問数: {len(sections)}")
    print("-" * 60)
    
    for section in sections:
        print(f"\n大問{section.number}: {section.title}")
        print(f"  - セクションタイプ: {section.section_type}")
        print(f"  - 文章問題: {'はい' if section.is_text_problem else 'いいえ'}")
        if section.char_count is not None:
            print(f"  - 文字数: {section.char_count}")
        else:
            print(f"  - 文字数: カウント対象外（語句問題）")
        print(f"  - 設問数: {section.question_count}")
        print(f"  - 内容プレビュー: {section.content[:100]}...")
    
    # 出典抽出のテスト
    print("\n" + "=" * 60)
    print("出典抽出テスト")
    print("=" * 60)
    
    extractor = SourceProcessor()
    
    # 文章問題のセクションからのみ出典を抽出
    text_sections = [s for s in sections if s.is_text_problem]
    
    for section in text_sections:
        sources = extractor.extract_sources_from_text(section.text)
        if sources:
            print(f"\n大問{section.number}の出典:")
            for source in sources:
                print(f"  - 著者: {source.author}")
                print(f"  - 作品: {source.title}")
                print(f"  - 原文: {source.raw_source}")
    
    # 総文字数の計算（文章問題のみ）
    total_char_count = sum(s.char_count for s in sections if s.char_count is not None)
    print(f"\n総文字数（文章問題のみ）: {total_char_count}")
    
    return sections

if __name__ == "__main__":
    test_seiko_problem()