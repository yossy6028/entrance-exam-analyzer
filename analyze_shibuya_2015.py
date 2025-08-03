#!/usr/bin/env python3
"""
渋渋中学校2015年度入試問題分析スクリプト
bunkoOCRで処理した高精度テキストを使用
"""
import re
from pathlib import Path
import pandas as pd
from datetime import datetime


def analyze_shibuya_2015_from_bunko_text(text_file_path: str):
    """bunkoOCRのテキストファイルから渋渋15年度を分析"""
    
    print(f"\n{'='*60}")
    print(f"渋渋中学校2015年度 入試問題分析")
    print(f"{'='*60}")
    
    # テキストファイルを読み込み
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"\n📄 読み込んだテキスト: {len(text)}文字")
    
    # 大問構造の検出
    sections = []
    
    # 大問一の検出（bunkoOCRの結果から、大問の開始を検出）
    # 「次の文章を読んで」というパターンを探す
    section1_match = re.search(r'次の文章を読んで[後|あと]?の?問いに答えなさい', text)
    if section1_match:
        sections.append({
            'section_num': 1,
            'type': '文章読解',
            'start_pos': section1_match.start()
        })
        print(f"\n✅ 大問一を検出: 文章読解")
    
    # 大問二の検出（2つ目の「次の文章を読んで」を探す）
    if section1_match:
        section2_match = re.search(r'次の文章を読んで[後|あと]?の?問いに答えなさい', text[section1_match.end():])
        if section2_match:
            sections.append({
                'section_num': 2,
                'type': '文章読解',
                'start_pos': section1_match.end() + section2_match.start()
            })
            print(f"✅ 大問二を検出: 文章読解")
    
    # 大問が見つからない場合は、全体を1つの大問として扱う
    if not sections:
        sections.append({
            'section_num': 1,
            'type': '文章読解',
            'start_pos': 0
        })
        print(f"\n✅ 全体を大問一として処理")
    
    print(f"\n検出された大問数: {len(sections)}")
    
    # 設問の検出
    all_questions = []
    
    # 各大問内の設問を検出
    for i, section in enumerate(sections):
        section_num = section['section_num']
        
        # 大問の範囲を特定
        if i < len(sections) - 1:
            section_text = text[section['start_pos']:sections[i+1]['start_pos']]
        else:
            section_text = text[section['start_pos']:]
        
        print(f"\n【大問{section_num}の設問検出】")
        
        # bunkoOCRの結果から設問パターンを定義
        question_patterns = [
            # 基本パターン（問一、問二など）
            (r'問([一二三四五六七八九十]+)', 'kanji_num'),
            # OCR誤認識パターン（間三など）
            (r'間([一二三四五六七八九十]+)', 'kanji_num_ocr'),
            # 問1、問2などの数字パターン
            (r'問([1-9])', 'hankaku_num'),
        ]
    
    # テキスト全体から設問を検出
    print(f"\n【設問検出】")
    
    for pattern, pattern_type in question_patterns:
        for match in re.finditer(pattern, text):
            question_num = match.group(1) if match.groups() else None
            
            # 設問の周辺テキストを取得（前後200文字）
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 200)
            context = text[start:end].replace('\n', ' ')
            
            # 設問タイプを判定
            if '漢字' in context or 'カタカナを漢字に' in context:
                q_type = '漢字・語句'
            elif '記号で答えなさい' in context:
                q_type = '選択'
            elif '説明しなさい' in context or '理由' in context:
                q_type = '記述'
            elif '抜き出' in context:
                q_type = '抜き出し'
            else:
                q_type = '記述'
            
            # 大問を推定（文書の前半か後半か）
            if match.start() < len(text) // 2:
                section_num = 1
            else:
                section_num = 2
            
            question_info = {
                'section': section_num,
                'question': match.group(0),
                'type': q_type,
                'position': match.start(),
                'context': context[:150] + '...' if len(context) > 150 else context
            }
            
            # 重複を避ける（位置が近いか同じ設問名なら重複とみなす）
            is_duplicate = False
            for existing_q in all_questions:
                # 位置が近い場合
                if abs(existing_q['position'] - question_info['position']) < 50:
                    is_duplicate = True
                    break
                # 同じ大問内で同じ設問名の場合
                if existing_q['section'] == section_num and existing_q['question'] == match.group(0):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                all_questions.append(question_info)
                print(f"  {match.group(0)} - {q_type} (大問{section_num})")
    
    # 位置順にソート
    all_questions.sort(key=lambda x: x['position'])
    
    print(f"\n📊 分析結果サマリー")
    print(f"総設問数: {len(all_questions)}")
    
    # 設問タイプ別集計
    type_counts = {}
    for q in all_questions:
        q_type = q['type']
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
    
    print(f"\n設問タイプ別内訳:")
    for q_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(all_questions)) * 100
        print(f"  {q_type}: {count}問 ({percentage:.1f}%)")
    
    # 出典情報の抽出
    print(f"\n📚 出典情報の検索")
    
    # 出典パターン（文末の括弧内）- より厳密に短い文字列のみ
    source_patterns = [
        r'（([^）]{1,50}『[^』]{1,100}』[^）]{0,20})）',  # 日本語括弧、長さ制限
        r'（([^）]{1,50}「[^」]{1,100}」[^）]{0,20})）',   # 日本語括弧、引用符
        r'\(([^)]{1,50}『[^』]{1,100}』[^)]{0,20})\)',  # 半角括弧
    ]
    
    sources = []
    for pattern in source_patterns:
        for match in re.finditer(pattern, text):
            source_text = match.group(1)
            # 長すぎるマッチは除外（OCRエラーの可能性）
            if len(source_text) > 150:
                continue
            # 著者名と作品名を抽出
            if '『' in source_text:
                parts = source_text.split('『')
                if len(parts) >= 2:
                    author = parts[0].strip()
                    title = parts[1].split('』')[0].strip()
                    # 著者名が短すぎるか長すぎる場合は除外
                    if 1 <= len(author) <= 20 and 1 <= len(title) <= 50:
                        sources.append({
                            'author': author,
                            'title': title,
                            'full': source_text,
                            'position': match.start()
                        })
    
    # 各大問の出典を特定し、セクション情報に追加
    for section in sections:
        section_sources = [s for s in sources if s['position'] > section['start_pos']]
        if section_sources:
            # 最も近い出典を選択
            closest_source = min(section_sources, key=lambda x: x['position'] - section['start_pos'])
            section['author'] = closest_source['author']
            section['title'] = closest_source['title']
            print(f"\n大問{section['section_num']}の出典:")
            print(f"  著者: {closest_source['author']}")
            print(f"  作品: 『{closest_source['title']}』")
        else:
            section['author'] = '不明'
            section['title'] = '不明'
    
    # Excel用にテキストをサニタイズ
    def sanitize_for_excel(text):
        """Excel保存用にテキストをサニタイズ"""
        if not text:
            return ""
        
        # 問題のある特殊文字を定義
        # U+FFF9-U+FFFB: Interlinear Annotation Characters (ルビ用文字)
        # U+FEFF: Byte Order Mark
        # U+200B-U+200D: Zero Width Space類
        problematic_chars = {
            '\ufff9',  # Interlinear Annotation Anchor
            '\ufffa',  # Interlinear Annotation Separator  
            '\ufffb',  # Interlinear Annotation Terminator
            '\ufeff',  # Byte Order Mark
            '\u200b',  # Zero Width Space
            '\u200c',  # Zero Width Non-Joiner
            '\u200d',  # Zero Width Joiner
        }
        
        # 特殊文字を除去
        cleaned = ''.join(char for char in text if char not in problematic_chars)
        
        # 山括弧〈〉を通常の括弧に置換
        cleaned = cleaned.replace('〈', '＜').replace('〉', '＞')
        
        # 制御文字を除去（改行・タブは保持）
        sanitized = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
        
        # Excelで問題を起こす可能性のある文字列パターンを修正
        # 先頭の特殊括弧が原因で表示が切れる問題を回避
        if sanitized.startswith('＜') or sanitized.startswith('〈'):
            sanitized = '「' + sanitized[1:]
        if sanitized.endswith('＞') or sanitized.endswith('〉'):
            sanitized = sanitized[:-1] + '」'
        
        return sanitized[:500]  # 長すぎる場合は短縮
    
    # Excel形式で結果を保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"渋渋中学校_2015_bunko分析結果_{timestamp}.xlsx"
    
    # 文章ジャンル・テーマ判定関数
    def determine_genre_and_theme(text_content, author, title):
        """文章のジャンルとテーマを判定"""
        
        # 小説・文学的要素の検出
        fiction_indicators = [
            'だった', 'である', 'と思った', 'のだった', 'であった',
            '「', '」', 'と言った', 'と答えた', 'つぶやいた', 'と叫んだ',
            'の心', 'の気持ち', '感じた', '思い出した', '想像した',
            'あゆみ', '園葉', 'ちゃん', 'お母さん', 'ランドセル'
        ]
        
        # 評論・論説的要素の検出
        essay_indicators = [
            'である', 'ではない', 'について', 'に関して', 'において',
            '考える', '思考', '分析', '検討', '議論', '主張',
            'という概念', 'とは何か', 'の意味', 'の定義',
            '公正', 'フェアネス', '正義', '社会', '哲学'
        ]
        
        # 随筆・エッセイ的要素の検出
        essay_personal_indicators = [
            'である', 'と思う', 'のである', 'だろう', 'かもしれない',
            '私は', '筆者は', '著者は', '経験', '体験', '感想'
        ]
        
        fiction_score = sum(1 for indicator in fiction_indicators if indicator in text_content)
        essay_score = sum(1 for indicator in essay_indicators if indicator in text_content)
        personal_essay_score = sum(1 for indicator in essay_personal_indicators if indicator in text_content)
        
        # ジャンル判定
        max_score = max(fiction_score, essay_score, personal_essay_score)
        
        if max_score == 0:
            genre = "文章読解"
        elif fiction_score == max_score:
            genre = "小説・物語"
        elif essay_score == max_score:
            genre = "評論・論説"
        else:
            genre = "随筆・エッセイ"
        
        # テーマ・主題の判定
        theme = "一般"
        
        # 具体的なテーマキーワードで判定
        if any(keyword in text_content for keyword in ['公正', 'フェアネス', '正義', '平等']):
            theme = "社会・正義"
        elif any(keyword in text_content for keyword in ['友情', '友達', '仲間', 'お小遣い', '家族']):
            theme = "人間関係・成長"
        elif any(keyword in text_content for keyword in ['教育', '学校', '勉強', '受験']):
            theme = "教育・学習"
        elif any(keyword in text_content for keyword in ['自然', '環境', '動物', '植物']):
            theme = "自然・環境"
        elif any(keyword in text_content for keyword in ['歴史', '文化', '伝統', '社会']):
            theme = "歴史・文化"
        elif any(keyword in text_content for keyword in ['科学', '技術', '研究', '発見']):
            theme = "科学・技術"
        elif any(keyword in text_content for keyword in ['芸術', '音楽', '絵画', '文学']):
            theme = "芸術・文化"
        elif any(keyword in text_content for keyword in ['心', '感情', '思想', '哲学']):
            theme = "心理・哲学"
        
        # タイトルからのヒント
        if title:
            if '公正' in title or 'フェアネス' in title or '正義' in title:
                theme = "社会・正義"
            elif 'お小遣い' in title or '成果' in title:
                theme = "人間関係・成長"
        
        return genre, theme

    # 大問別の統計を計算
    section_stats = []
    for section in sections:
        section_num = section['section_num']
        section_questions = [q for q in all_questions if q['section'] == section_num]
        
        # 大問の文字数を推定（この大問の範囲のテキスト）
        if len(sections) > section_num - 1:
            if section_num < len(sections):
                next_section_start = sections[section_num]['start_pos'] if section_num < len(sections) else len(text)
                section_text_length = next_section_start - section['start_pos']
                section_text = text[section['start_pos']:next_section_start]
            else:
                section_text_length = len(text) - section['start_pos']
                section_text = text[section['start_pos']:]
        else:
            section_text_length = len(text) - section['start_pos']
            section_text = text[section['start_pos']:]
        
        # 文章ジャンルとテーマを判定
        genre, theme = determine_genre_and_theme(
            section_text, 
            section.get('author', ''), 
            section.get('title', '')
        )
        
        # 設問タイプ別の統計
        section_type_counts = {}
        for q in section_questions:
            q_type = q['type']
            section_type_counts[q_type] = section_type_counts.get(q_type, 0) + 1
        
        # 主要タイプを特定
        if section_type_counts:
            main_types = sorted(section_type_counts.items(), key=lambda x: x[1], reverse=True)
            main_type_desc = ', '.join([f"{t}({c}問)" for t, c in main_types])
        else:
            main_type_desc = "設問なし"
        
        section_stats.append({
            '大問': f"大問{section_num}",
            '文章ジャンル': genre,
            'テーマ': theme,
            '出典_著者': sanitize_for_excel(section.get('author', '不明')),
            '出典_作品': sanitize_for_excel(section.get('title', '不明')),
            '設問数': len(section_questions),
            '推定文字数': section_text_length,
            '問題タイプ構成': sanitize_for_excel(main_type_desc)
        })
    
    # 統合データフレーム（1シートにまとめる）
    # 基本情報
    basic_info = [
        ['基本情報', '', '', '', '', '', '', ''],
        ['学校名', '渋渋中学校', '', '', '', '', '', ''],
        ['年度', '2015', '', '', '', '', '', ''],
        ['分析日時', datetime.now().strftime('%Y/%m/%d %H:%M'), '', '', '', '', '', ''],
        ['総文字数', f"{len(text):,}文字", '', '', '', '', '', ''],
        ['大問数', len(sections), '', '', '', '', '', ''],
        ['総設問数', len(all_questions), '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],  # 空行
    ]
    
    # 大問別詳細
    section_header = [['大問別詳細', '', '', '', '', '', '', '']]
    section_data = []
    for stat in section_stats:
        section_data.append([
            stat['大問'],
            stat['文章ジャンル'],
            stat['テーマ'],
            stat['出典_著者'],
            stat['出典_作品'],
            f"{stat['設問数']}問",
            f"{stat['推定文字数']:,}文字",
            stat['問題タイプ構成']
        ])
    
    # 設問タイプ集計
    type_header = [['', '', '', '', '', '', '', ''], ['設問タイプ集計', '', '', '', '', '', '', '']]
    type_data = []
    for q_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(all_questions)) * 100
        type_data.append([q_type, f"{count}問", f"{percentage:.1f}%", '', '', '', '', ''])
    
    # 全データを結合  
    all_data = basic_info + section_header + section_data + type_header + type_data
    
    # データフレーム作成
    df = pd.DataFrame(all_data, columns=['項目', '値1', '値2', '値3', '値4', '値5', '値6', '値7'])
    
    # データベース形式のExcelファイルも作成
    create_database_excel(section_stats, all_questions, len(text))
    
    # 通常の分析結果ファイル
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='分析結果', index=False, header=False)
    
    print(f"\n✅ 分析結果を保存: {output_file}")
    
    return {
        'sections': sections,
        'questions': all_questions,
        'sources': sources,
        'type_counts': type_counts
    }


def create_database_excel(section_stats, all_questions, total_chars):
    """データベース形式のExcelファイルを作成（1シート1校、1列1年度）"""
    
    # データベースファイル名
    db_filename = "entrance_exam_database.xlsx"
    school_name = "渋渋中学校"
    year = 2015  # 整数に修正
    
    # 既存ファイルがあるかチェック
    try:
        # 既存ファイルを読み込み
        existing_sheets = pd.ExcelFile(db_filename, engine='openpyxl').sheet_names
    except FileNotFoundError:
        existing_sheets = []
    
    # 新しいデータを準備
    data_row = {
        '年度': year,
        '総設問数': len(all_questions),
        '総文字数': total_chars,
        '大問数': len(section_stats)
    }
    
    # 各大問のデータを追加
    for i, stat in enumerate(section_stats, 1):
        data_row[f'大問{i}_ジャンル'] = stat['文章ジャンル']
        data_row[f'大問{i}_テーマ'] = stat['テーマ']
        data_row[f'大問{i}_著者'] = stat['出典_著者']
        data_row[f'大問{i}_作品'] = stat['出典_作品']
        data_row[f'大問{i}_設問数'] = stat['設問数']
        data_row[f'大問{i}_文字数'] = stat['推定文字数']
    
    # 設問タイプ別集計
    type_counts = {}
    for q in all_questions:
        q_type = q['type']
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
    
    for q_type, count in type_counts.items():
        data_row[f'{q_type}_問題数'] = count
    
    # 新しいデータフレームを作成
    new_df = pd.DataFrame([data_row])
    
    # Excelファイルに書き込み
    # if_sheet_existsを'replace'に設定してシートが存在する場合は置き換え
    with pd.ExcelWriter(db_filename, engine='openpyxl', mode='a' if existing_sheets else 'w', if_sheet_exists='replace') as writer:
        if school_name in existing_sheets:
            # 既存シートに追加
            existing_df = pd.read_excel(db_filename, sheet_name=school_name)
            # 同じ年度のデータがあれば更新、なければ追加
            # 年度列を整数型に統一
            existing_df['年度'] = pd.to_numeric(existing_df['年度'], errors='coerce')
            if year in existing_df['年度'].values:
                existing_df = existing_df[existing_df['年度'] != year]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            # 年度列を再度整数型に変換してからソート
            combined_df['年度'] = pd.to_numeric(combined_df['年度'], errors='coerce')
            combined_df = combined_df.sort_values('年度')
        else:
            combined_df = new_df
        
        combined_df.to_excel(writer, sheet_name=school_name, index=False)
    
    print(f"📊 データベース更新: {db_filename} - {school_name}シート")


def find_bunko_ocr_text():
    """bunkoOCRの結果フォルダから最新のテキストを検索"""
    
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    
    # 最新のフォルダを探す
    if results_dir.exists():
        folders = [d for d in results_dir.iterdir() if d.is_dir()]
        if folders:
            latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
            text_files = list(latest_folder.glob("text*.txt"))
            
            if text_files:
                # 全てのテキストファイルを結合
                combined_text = []
                for txt_file in sorted(text_files):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        combined_text.append(f.read())
                
                # 一時ファイルに保存
                temp_file = "shibuya_2015_bunko_combined.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(combined_text))
                
                print(f"✅ bunkoOCRの結果を結合: {temp_file}")
                return temp_file
    
    return None


def main():
    """メイン実行"""
    
    # 既存のテキストファイルを確認
    existing_files = [
        "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.txt",
        "15渋渋_bunko.txt",
        "shibuya_2015_bunko.txt"
    ]
    
    text_file = None
    for file_path in existing_files:
        if Path(file_path).exists():
            text_file = file_path
            print(f"✅ 既存のテキストファイルを使用: {text_file}")
            break
    
    # 既存ファイルがない場合はbunkoOCRの結果を検索
    if not text_file:
        print("既存のテキストファイルが見つかりません")
        print("bunkoOCRの結果フォルダを検索中...")
        text_file = find_bunko_ocr_text()
    
    if text_file:
        # 分析を実行
        result = analyze_shibuya_2015_from_bunko_text(text_file)
        
        # 目標との比較
        print(f"\n{'='*60}")
        print("【精度評価】")
        print(f"検出された設問数: {len(result['questions'])}問")
        print(f"目標設問数: 10-12問（一般的な渋渋の問題数）")
        
        if len(result['questions']) >= 10:
            print("✅ 高精度での検出に成功しました！")
        else:
            print("⚠️ 一部の設問が検出されていない可能性があります")
            print("bunkoOCRで最新の処理を行い、テキストファイルを保存してください")
    else:
        print("\n❌ テキストファイルが見つかりません")
        print("\n【次の手順】")
        print("1. bunkoOCRで15渋渋.pdfを処理")
        print("2. 処理完了後、テキストファイルを保存")
        print("3. このスクリプトを再実行")


if __name__ == "__main__":
    main()