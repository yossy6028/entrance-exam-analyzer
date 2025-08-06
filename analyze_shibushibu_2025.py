#!/usr/bin/env python3
"""
2025年渋谷教育学園渋谷中学校の国語入試問題を完全分析
"""

import sys
from pathlib import Path
from datetime import datetime

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.flexible_excel_formatter import FlexibleExcelFormatter


def analyze_shibushibu_2025():
    """渋渋2025年の詳細分析結果"""
    
    print("="*80)
    print("【2025年 渋谷教育学園渋谷中学校 国語入試問題 完全分析結果】")
    print("="*80)
    
    # 基本情報
    print("\n### 基本情報\n")
    print("- 総文字数: 約15,000文字")
    print("- 大問数: 2問")
    print("- 総設問数: 15問")
    
    # 出典情報
    print("\n### 出典情報\n")
    print("- 第1文章: 高瀬隼子『お小遣いの成果』")
    print("- 第2文章: 朱喜哲『〈公正〉を乗りこなす　正義の反対は別の正義か』")
    
    # 大問1の詳細
    print("\n### 【大問1】高瀬隼子『お小遣いの成果』\n")
    print("- ジャンル: 小説・物語")
    print("- テーマ: 人間関係・成長／友情と価値観")
    print("- 文字数: 約8,000文字")
    print("- 内容概要: 小学6年生のあゆみが、限られたお小遣いの中で好きなライトノベルを買うか")
    print("  友人関係のためファッション誌を買うか葛藤する。近所の田所さん（友人園葉の祖母）から")
    print("  園葉の善行を伝えたお礼にお小遣いをもらい、それで念願の本を買う。")
    print("  その後、私立中学に進学する園葉との友情を再確認する物語。")
    
    print("\n設問（7問）:")
    print("1. 問一：カタカナを漢字に直す（漢字・語句）【選択肢なし】")
    print("2. 問二：あゆみの心情説明（選択）【5択（ア〜オ）】")
    print("3. 問三：田所さんの人物像（選択）【5択（ア〜オ）】")
    print("4. 問四：あゆみの心情説明（選択）【5択（ア〜オ）】")
    print("5. 問五：心情の変化を説明（記述・61〜70字）【選択肢なし】")
    print("6. 問六：あゆみの心情（選択）【5択（ア〜オ）】")
    print("7. 問七：作品解釈の誤り（選択・2つ）【6択から2つ選択（ア〜カ）】")
    
    # 大問2の詳細
    print("\n### 【大問2】朱喜哲『〈公正〉を乗りこなす　正義の反対は別の正義か』\n")
    print("- ジャンル: 論説文")
    print("- テーマ: 社会・文化／多様性と公正")
    print("- 文字数: 約7,000文字")
    print("- 内容概要: 「インターセクショナリティ（交差性）」という概念を用いて、")
    print("  社会における様々な属性（人種、性別、階級等）の軸が交差する中での")
    print("  多様性と公正について論じる。マイノリティとマジョリティの関係性、")
    print("  複合差別の問題、コミュニケーションにおける配慮の必要性を説明。")
    
    print("\n設問（8問）:")
    print("1. 問一：カタカナを漢字に直す（漢字・語句）【選択肢なし】")
    print("2. 問二：用語説明（記述）【選択肢なし】")
    print("3. 問三：「おとなであることの条件」の説明（選択）【5択（ア〜オ）】")
    print("4. 問四：インターセクショナリティの効果（記述・51〜60字）【選択肢なし】")
    print("5. 問五：「どっちもどっち」ではない理由（選択）【5択（ア〜オ）】")
    print("6. 問六：アイデンティティーズの説明（選択）【5択（ア〜オ）】")
    print("7. 問七：必要なことの説明（記述）【選択肢なし】")
    print("8. 問八：内容理解の誤り（選択）【5択（ア〜オ）】")
    
    # 選択肢数の集計
    print("\n### 選択肢数の分析\n")
    print("【大問1】")
    print("- 5択問題: 4問（問二、問三、問四、問六）")
    print("- 6択から2つ選択: 1問（問七）")
    print("- 記述・その他: 2問（問一、問五）")
    
    print("\n【大問2】")
    print("- 5択問題: 4問（問三、問五、問六、問八）")
    print("- 記述: 4問（問一、問二、問四、問七）")
    
    print("\n【全体集計】")
    print("- 5択問題: 8問（53.3%）")
    print("- 6択から2つ選択: 1問（6.7%）")
    print("- 記述・漢字: 6問（40.0%）")
    
    # 出題傾向分析
    print("\n### 出題傾向分析\n")
    print("1. 文学的文章（小説）と論理的文章（論説文）のバランス型出題")
    print("2. 現代的テーマ（多様性、友情、価値観）を扱った作品選定")
    print("3. 長文読解力重視（各大問7,000〜8,000字）")
    print("4. 選択問題が中心（60%）、5択が標準")
    print("5. 心情理解と論理的思考の両方を要求")
    print("6. 社会的視点を含む高度な内容理解を求める")
    print("7. 字数指定記述は51〜70字程度で比較的短め")
    
    # データ構造を返す
    analysis_result = {
        'total_characters': 15000,
        'total_questions': 15,
        'sections': [
            {
                'number': 1,
                'source': {
                    'author': '高瀬隼子',
                    'work': 'お小遣いの成果'
                },
                'characters': 8000,
                'genre': '小説・物語',
                'theme': '人間関係・成長／友情と価値観',
                'content_summary': '小学6年生のあゆみが、限られたお小遣いの中で好きなライトノベルを買うか友人関係のためファッション誌を買うか葛藤する。近所の田所さん（友人園葉の祖母）から園葉の善行を伝えたお礼にお小遣いをもらい、それで念願の本を買う。その後、私立中学に進学する園葉との友情を再確認する物語。',
                'questions': [
                    {'number': '一', 'type': '漢字・語句', 'choices': 0},
                    {'number': '二', 'type': '選択', 'choices': 5},
                    {'number': '三', 'type': '選択', 'choices': 5},
                    {'number': '四', 'type': '選択', 'choices': 5},
                    {'number': '五', 'type': '記述', 'choices': 0},
                    {'number': '六', 'type': '選択', 'choices': 5},
                    {'number': '七', 'type': '選択', 'choices': 6}
                ],
                'question_details': '問一:カタカナ→漢字、問二〜四:心情理解（5択）、問五:心情変化（記述61-70字）、問六:心情理解（5択）、問七:解釈の誤り（6択から2つ）'
            },
            {
                'number': 2,
                'source': {
                    'author': '朱喜哲',
                    'work': '〈公正〉を乗りこなす　正義の反対は別の正義か'
                },
                'characters': 7000,
                'genre': '論説文',
                'theme': '社会・文化／多様性と公正',
                'content_summary': '「インターセクショナリティ（交差性）」という概念を用いて、社会における様々な属性（人種、性別、階級等）の軸が交差する中での多様性と公正について論じる。マイノリティとマジョリティの関係性、複合差別の問題、コミュニケーションにおける配慮の必要性を説明。',
                'questions': [
                    {'number': '一', 'type': '漢字・語句', 'choices': 0},
                    {'number': '二', 'type': '記述', 'choices': 0},
                    {'number': '三', 'type': '選択', 'choices': 5},
                    {'number': '四', 'type': '記述', 'choices': 0},
                    {'number': '五', 'type': '選択', 'choices': 5},
                    {'number': '六', 'type': '選択', 'choices': 5},
                    {'number': '七', 'type': '記述', 'choices': 0},
                    {'number': '八', 'type': '選択', 'choices': 5}
                ],
                'question_details': '問一:カタカナ→漢字、問二:用語説明、問三:条件説明（5択）、問四:効果説明（記述51-60字）、問五:理由説明（5択）、問六:概念説明（5択）、問七:必要事項説明、問八:内容理解（5択）'
            }
        ],
        'question_types': {
            '記述': 6,
            '選択': 7,
            '漢字・語句': 2
        }
    }
    
    return analysis_result


def save_to_excel():
    """分析結果をExcelに保存"""
    
    print("\n" + "="*80)
    print("Excel保存処理を開始")
    print("="*80)
    
    # 分析結果を取得
    analysis_result = analyze_shibushibu_2025()
    
    # Excelフォーマッターを初期化
    formatter = FlexibleExcelFormatter(
        excel_path="entrance_exam_database.xlsx"
    )
    
    # 追加情報
    additional_info = {
        '記述_最大字数': 70,
        '記述_最小字数': 51,
        '選択肢_最大数': 6,
        '図表_使用有無': 'なし',
        '詩歌_有無': 'なし',
        '出題傾向': '文学的文章（小説）と論理的文章（論説文）のバランス型。選択問題中心（60%）で5択が標準。現代的テーマ（多様性、友情、価値観）を扱う。',
        '特記事項': '2025年度渋谷教育学園渋谷中学校入試問題。長文読解重視（各大問7,000〜8,000字）。'
    }
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="渋谷教育学園渋谷中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25渋渋.txt",
        additional_info=additional_info
    )
    
    # データを保存
    print("\nExcelデータベースに保存中...")
    success = formatter.save_to_excel(
        school_name="渋谷教育学園渋谷中学校",
        row_data=row_data,
        backup=True
    )
    
    if success:
        print("✅ 渋谷教育学園渋谷2025年のデータを保存しました")
        
        # サマリーを表示
        summary = formatter.get_school_summary("渋谷教育学園渋谷中学校")
        print("\n" + summary)
    else:
        print("❌ 保存に失敗しました")
    
    return success


if __name__ == "__main__":
    # 分析のみ実行
    analyze_shibushibu_2025()
    
    print("\n" + "="*80)
    print("※ Excelに保存する場合は、以下のコマンドを実行してください:")
    print("  python analyze_shibushibu_2025.py --save")
    
    # コマンドライン引数で保存を指定
    if len(sys.argv) > 1 and sys.argv[1] == "--save":
        save_to_excel()