#!/usr/bin/env python3
"""
聖光学院の国語問題を新しいセクション分割ロジックv3でテスト（簡易版）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.section_splitter_v3 import ImprovedSectionSplitterV3

def test_seiko_problem():
    """聖光学院の実際の問題でテスト"""
    
    # テストデータ（実際のOCR結果のサンプル）
    test_text = """一、次の漢字の読みがなを書きなさい。

    1、放送で指示があるまで、この冊子を開いてはいけません。
    2、この冊子は27ページまであります。
    3、問題について質問は受け付けません。
    
    ① 地方経済
    ② 生徒会長
    ③ 上級生
    ④ 彼女の豊富
    ⑤ 全校生徒

    二、次の語句について答えなさい。

    1、次の①～⑤の文の線部の方カタカナを、それぞれ漢字に直しなさい。
    
    ① 地方経済の活性化
    ② 生徒会長に選ばれた
    ③ 上級生たちは
    ④ 彼女の豊富な
    ⑤ 生徒会長選挙では

    三、次の文章を読んで、後の問いに答えなさい。

    津山は、俺の小刻みに音を振って古定した。
    「ほぼ」
    「じゃあ、書きません」なととと音を縦に振って否定したわけではない。「ほぼ」という危険なことをしている。
    これまでいろんな文献に目を通してきて、「ほぼ」という言葉は実に危険だということを知った。
    （長い本文が続く...）
    
    森谷美「本が新しい五五の希望」による

    問一　傍線部①「それ」とは何を指しますか。
    問二　傍線部②について、筆者の考えを説明しなさい。
    問三　この文章の主題を60字以内で書きなさい。

    四、次の文章を読んで、後の問いに答えなさい。

    津山は生き方が不器用で、人付き合いが苦手だった。
    （長い本文が続く...）
    
    津山さん『私たちが見ていること』（『図書』第九〇四号所収）による

    問一　漢字の読みを答えなさい。
    問二　空欄に入る語句を選びなさい。
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
        print(f"  - 内容プレビュー: {section.content[:80]}...")
    
    # 総文字数の計算（文章問題のみ）
    total_char_count = sum(s.char_count for s in sections if s.char_count is not None)
    print(f"\n総文字数（文章問題のみ）: {total_char_count}")
    
    # 正しい判定結果の確認
    print("\n" + "=" * 60)
    print("判定結果の検証")
    print("=" * 60)
    
    expected = {
        1: ("語句", False),  # 一：漢字の読み → 語句問題
        2: ("語句", False),  # 二：カタカナを漢字に → 語句問題  
        3: ("文章", True),   # 三：文章を読んで → 文章問題
        4: ("文章", True),   # 四：文章を読んで → 文章問題
    }
    
    for section in sections:
        if section.number in expected:
            exp_type, exp_is_text = expected[section.number]
            actual_type = "文章" if section.is_text_problem else "語句"
            
            if actual_type == exp_type:
                print(f"✅ 大問{section.number}: 正しく{exp_type}問題と判定")
            else:
                print(f"❌ 大問{section.number}: 誤判定（期待:{exp_type}, 実際:{actual_type}）")
    
    return sections

if __name__ == "__main__":
    test_seiko_problem()