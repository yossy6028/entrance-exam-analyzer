#!/usr/bin/env python3
"""
新しいセクション分割ロジックのテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.section_splitter_v2 import ImprovedSectionSplitter

def test_improved_splitter():
    """改良版セクション分割のテスト"""
    
    # 実際の入試問題に近いテストケース
    test_text = """二〇二五年度 聖光学院中学校 入学試験問題
    
国語

一、次の文章を読んで、後の問いに答えなさい。

（ここから本文が始まる。通常は3000～5000文字の長文が続く。
たとえば、現代の小説や評論文が掲載される。
内容は様々で、人間関係、社会問題、科学技術などが扱われる。
...省略...
文章の途中に「一つの例として」「二つ目の理由は」などの表現があっても、
これらは大問マーカーではない。）

森沢明夫『本が紡いだ五つの奇跡』による

問一　傍線部①「それ」とは何を指しますか。次の中から選びなさい。
問二　傍線部②について、筆者の考えを説明しなさい。
問三　この文章の主題を60字以内で書きなさい。
問四　空欄アに入る語句を答えなさい。
問五　この文章から読み取れることを100字以内でまとめなさい。

二、次の文章を読んで、後の問いに答えなさい。

（第二の長文がここに入る。こちらも通常3000～5000文字。
別の著者による別のテーマの文章。
説明文、随筆、詩などの場合もある。
...省略...）

永井佳子「見えないキノコの勤勉な日々」（『図書』第九〇四号所収）による

問一　漢字の読みを答えなさい。
　　　① 蓄積　② 潤沢　③ 融和
問二　空欄に入る語句を選びなさい。
問三　筆者の主張をまとめなさい。

三、次の漢字・語句の問題に答えなさい。

問一　次の漢字の読みをひらがなで書きなさい。
　１　執筆
　２　簡潔
　３　融通
　４　謙虚
　５　寛容

問二　次のカタカナを漢字に直しなさい。
　１　キョウリョク（協力）
　２　シンチョウ（慎重）
　３　カンサツ（観察）

問三　次の慣用句の意味を説明しなさい。
　１　足が地に着かない
　２　耳を貸す

四、次の詩を読んで、後の問いに答えなさい。

春の朝
風が吹いて
桜が舞い散る
（詩の本文）

問一　この詩の形式を答えなさい。
問二　作者の心情を説明しなさい。
"""
    
    print("=== 改良版セクション分割テスト ===\n")
    
    splitter = ImprovedSectionSplitter(min_section_length=500)
    
    # マーカー候補を検出
    candidates = splitter._find_marker_candidates(test_text)
    print(f"検出されたマーカー候補: {len(candidates)}個")
    for c in candidates[:10]:  # 最初の10個を表示
        print(f"  位置{c['start']:4d}: {c['text']:20s} (優先度:{c['priority']}, 番号:{c['number']})")
    
    print("\n--- フィルタリング後 ---")
    
    # フィルタリング（デバッグ情報付き）
    print("フィルタリング処理詳細:")
    
    # 重複除去
    position_map = {}
    for c in candidates:
        pos_key = c['start']
        if pos_key not in position_map or c['priority'] > position_map[pos_key]['priority']:
            position_map[pos_key] = c
    unique_candidates = sorted(position_map.values(), key=lambda x: x['start'])
    print(f"  重複除去後: {len(unique_candidates)}個")
    
    for i, c in enumerate(unique_candidates):
        if i > 0:
            prev = unique_candidates[i-1]
            distance = c['start'] - prev['start']
            print(f"    {prev['text']} → {c['text']}: 距離={distance}文字")
    
    true_markers = splitter._filter_true_markers(candidates, test_text)
    print(f"\n確定した大問マーカー: {len(true_markers)}個")
    for m in true_markers:
        print(f"  大問{m['number']}: 位置{m['start']:4d} '{m['text']}'")
    
    print("\n--- セクション分割結果 ---")
    
    # セクション分割
    sections = splitter.split_sections(test_text)
    print(f"生成されたセクション: {len(sections)}個\n")
    
    for section in sections:
        print(f"【{section.title}】")
        print(f"  文字数: {len(section.text)}文字")
        print(f"  設問数: {section.question_count}問")
        print(f"  内容プレビュー: {section.text[:80]}...")
        print()
    
    # 文字数の分布を確認
    char_counts = [len(s.text) for s in sections]
    if char_counts:
        print("=== 文字数分析 ===")
        print(f"平均: {sum(char_counts) / len(char_counts):.0f}文字")
        print(f"最小: {min(char_counts)}文字")
        print(f"最大: {max(char_counts)}文字")
        
        # 異常検出
        if min(char_counts) < 100:
            print("⚠️ 警告: 100文字未満のセクションがあります")
        elif all(c >= 500 for c in char_counts):
            print("✅ すべてのセクションが適切な長さです")

if __name__ == "__main__":
    test_improved_splitter()