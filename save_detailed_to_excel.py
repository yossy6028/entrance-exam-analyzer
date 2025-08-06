#!/usr/bin/env python3
"""
開成・桜蔭2025年の詳細データをExcelに保存
"""

import sys
from pathlib import Path
from datetime import datetime

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.flexible_excel_formatter import FlexibleExcelFormatter


def save_kaisei_2025():
    """開成2025年の詳細データを保存"""
    
    print("【開成2025年】詳細データを準備中...")
    
    analysis_result = {
        'total_characters': 7773,
        'total_questions': 6,
        'sections': [
            {
                'number': 1,
                'source': {
                    'author': '古内一絵',
                    'work': '百年の子'
                },
                'characters': 4500,
                'genre': '小説・物語',
                'theme': '児童文学論・戦後文学',
                'content_summary': '出版社で学年誌を担当する野山彬が、児童文学作家の佐野三津彦から児童文学の本質について話を聞く場面。戦災孤児だった三津彦の体験を通じて、子どもの人権の歴史と児童文学の役割について語られる。',
                'questions': [
                    {'number': '一', 'type': '記述'},
                    {'number': '二', 'type': '記述'},
                    {'number': '三', 'type': '記述'}
                ],
                'question_details': '問一:「それが児童文学の仕事だ」について三津彦の考えを説明、問二:「二重に捨てられた気分」の意味を説明、問三:「ああいう誠実さ」の内容を説明'
            },
            {
                'number': 2,
                'source': {
                    'author': '永井玲衣',
                    'work': '世界の適切な保存'
                },
                'characters': 3273,
                'genre': '随筆',
                'theme': 'コミュニケーション論・言語哲学',
                'content_summary': '「伝わらない」ということの本質について、大学でのシンポジウムや日常的な場面を例に考察。言語の限界と、それでも伝えようとする人間の営みについて哲学的に論じている。',
                'questions': [
                    {'number': '一', 'type': '漢字・語句'},
                    {'number': '二', 'type': '記述'},
                    {'number': '三', 'type': '記述'}
                ],
                'question_details': '漢字問題、「伝わらないことが喜劇である」理由の説明、魚と人間の対比についての説明'
            }
        ],
        'question_types': {
            '記述': 5,
            '漢字・語句': 1
        }
    }
    
    # Excelフォーマッターを初期化
    formatter = FlexibleExcelFormatter(
        excel_path="entrance_exam_database.xlsx"
    )
    
    # 追加情報
    additional_info = {
        '記述_最大字数': None,
        '記述_最小字数': None,
        '図表_使用有無': 'なし',
        '詩歌_有無': 'なし',
        '出題傾向': '文学的文章（小説）と論理的文章（随筆）のバランス型出題。現代文学から2作品を選定。社会的テーマ（児童文学、コミュニケーション）を扱った作品。記述問題中心の出題形式。',
        '特記事項': '2025年度開成中学校入試問題。傍線部の意味を問う問題が中心。'
    }
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="開成中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25開成.txt",
        additional_info=additional_info
    )
    
    # データを保存
    print("Excelデータベースに保存中...")
    success = formatter.save_to_excel(
        school_name="開成中学校",
        row_data=row_data,
        backup=True
    )
    
    if success:
        print("✅ 開成2025年のデータを保存しました")
    else:
        print("❌ 開成2025年の保存に失敗しました")
    
    return success


def save_ouin_2025():
    """桜蔭2025年の詳細データを保存"""
    
    print("\n【桜蔭2025年】詳細データを準備中...")
    
    analysis_result = {
        'total_characters': 8303,
        'total_questions': 11,
        'sections': [
            {
                'number': 1,
                'source': None,
                'characters': 4000,
                'genre': '説明文',
                'theme': '科学・技術／人間とロボットの協働',
                'content_summary': '子どもたちと協力してゴミを集める「ゴミ箱ロボット」の実験を通じて、完全ではないロボットが人間の助けを引き出すことで機能を果たす「しなやかなシステム」について論じる。「注文をまちがえる料理店」やハサミなどの具体例も交えて説明。',
                'questions': [
                    {'number': '一', 'type': '漢字・語句'},
                    {'number': '二', 'type': '選択'},
                    {'number': '三', 'type': '記述'},
                    {'number': '四', 'type': '記述'},
                    {'number': '五', 'type': '記述'},
                    {'number': '六', 'type': '記述'}
                ],
                'question_details': '問一:四字熟語の完成（漢字・語句）、問二:空欄補充（選択）、問三:ゴミ箱ロボットと通常のゴミ箱の違いを説明（記述）、問四:「しなやかな強さ」と「脆さ」の対照について説明（記述）、問五:具体例に共通する考え方を説明（記述）、問六:童話との関連について説明（記述）'
            },
            {
                'number': 2,
                'source': {
                    'author': '植松三十里',
                    'work': 'イザベラ・バードと侍ボーイ'
                },
                'characters': 4303,
                'genre': '小説・物語',
                'theme': '人間関係・成長／異文化理解',
                'content_summary': '明治時代の日本を旅するイギリス人女性イザベラ・バードと、彼女の通訳を務める青年・鶴吉の物語。村人たちとの交流や、イザベラの旅の目的を巡る二人の対話を通じて、異文化理解と人間観察の意味を描く。',
                'questions': [
                    {'number': '一', 'type': '漢字・語句'},
                    {'number': '二', 'type': '漢字・語句'},
                    {'number': '三', 'type': '記述'},
                    {'number': '四', 'type': '記述'},
                    {'number': '五', 'type': '記述'}
                ],
                'question_details': '問一:カタカナを漢字に直す（漢字・語句）、問二:空欄に入る漢字一字（漢字・語句）、問三:鶴吉が「なおさら癪にさわった」理由を説明（記述）、問四:鶴吉がイザベラの書くものを受け入れられない理由を説明（記述）、問五:イザベラが書こうとする「真実」について説明（記述）'
            }
        ],
        'question_types': {
            '記述': 7,
            '選択': 1,
            '漢字・語句': 3
        }
    }
    
    # Excelフォーマッターを初期化
    formatter = FlexibleExcelFormatter(
        excel_path="entrance_exam_database.xlsx"
    )
    
    # 追加情報
    additional_info = {
        '記述_最大字数': None,
        '記述_最小字数': None,
        '図表_使用有無': 'なし',
        '詩歌_有無': 'なし',
        '出題傾向': '説明的文章（科学技術）と文学的文章（歴史小説）のバランス型出題。現代的テーマ（AI・ロボット）と歴史的テーマ（明治時代）の組み合わせ。人間の協働・相互理解をテーマとした作品選定。',
        '特記事項': '2025年度桜蔭中学校入試問題。記述問題が全体の約64%（7問/11問）を占める。具体例から抽象的概念を読み取る高度な読解力を要求。'
    }
    
    # データを整形
    row_data = formatter.format_analysis_data(
        school_name="桜蔭中学校",
        year=2025,
        analysis_result=analysis_result,
        ocr_filename="25桜蔭.txt",
        additional_info=additional_info
    )
    
    # データを保存
    print("Excelデータベースに保存中...")
    success = formatter.save_to_excel(
        school_name="桜蔭中学校",
        row_data=row_data,
        backup=True
    )
    
    if success:
        print("✅ 桜蔭2025年のデータを保存しました")
    else:
        print("❌ 桜蔭2025年の保存に失敗しました")
    
    return success


def main():
    """メイン処理"""
    print("="*80)
    print("開成・桜蔭2025年の詳細データをExcelに保存")
    print("="*80)
    
    # 開成のデータを保存
    kaisei_success = save_kaisei_2025()
    
    # 桜蔭のデータを保存
    ouin_success = save_ouin_2025()
    
    print("\n" + "="*80)
    print("処理完了")
    
    if kaisei_success and ouin_success:
        print("✅ すべてのデータを正常に保存しました")
    else:
        print("⚠️ 一部のデータの保存に失敗しました")
    
    # 各学校のサマリーを表示
    formatter = FlexibleExcelFormatter(
        excel_path="entrance_exam_database.xlsx"
    )
    
    print("\n【開成中学校】")
    print(formatter.get_school_summary("開成中学校"))
    
    print("\n【桜蔭中学校】")
    print(formatter.get_school_summary("桜蔭中学校"))


if __name__ == "__main__":
    main()