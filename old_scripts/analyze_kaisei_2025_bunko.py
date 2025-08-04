#!/usr/bin/env python3
"""
開成中学校2025年度入試問題分析スクリプト
bunkoOCRで処理したテキストを使用
"""
import re
from pathlib import Path
import pandas as pd
from datetime import datetime
import subprocess
import time
import pyautogui
import pyperclip


def launch_bunko_ocr_for_kaisei():
    """bunkoOCRを起動して開成中2025年のPDFを処理"""
    
    print(f"\n{'='*60}")
    print(f"bunkoOCRを使用した開成中学校2025年度分析")
    print(f"{'='*60}")
    
    # PDFファイルパス
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/開成中学校/2025年開成中学校問題_国語.pdf"
    
    # bunkoOCRを起動
    print("\n📱 bunkoOCRを起動中...")
    subprocess.Popen(['open', '-a', 'bunkoOCR'])
    time.sleep(3)
    
    # bunkoOCRのPDFファイル選択をクリック
    print("📂 PDFファイルを選択...")
    pyautogui.click(x=689, y=475)  # PDFファイル選択ボタン
    time.sleep(2)
    
    # ファイルダイアログでPDFを選択
    pyperclip.copy(pdf_path)
    pyautogui.hotkey('cmd', 'shift', 'g')  # パス入力ダイアログ
    time.sleep(0.5)
    pyautogui.hotkey('cmd', 'v')  # パスをペースト
    time.sleep(0.5)
    pyautogui.press('return')
    time.sleep(1)
    pyautogui.press('return')  # ファイル選択
    time.sleep(2)
    
    # OCR実行
    print("🔍 OCR処理を実行中...")
    pyautogui.click(x=689, y=680)  # 実行ボタン
    
    print("\n⏳ OCR処理が完了するまでお待ちください（約2-3分）")
    print("   完了したらEnterキーを押してください...")
    input()
    
    # 結果の保存場所を確認
    results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
    if results_dir.exists():
        # 最新のフォルダを取得
        folders = [d for d in results_dir.iterdir() if d.is_dir()]
        if folders:
            latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
            print(f"\n✅ OCR結果フォルダ: {latest_folder.name}")
            
            # テキストファイルを結合
            text_files = list(latest_folder.glob("text*.txt"))
            if text_files:
                combined_text = []
                for txt_file in sorted(text_files):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        combined_text.append(f"=== {txt_file.name} ===\n{content}")
                
                # 結合したテキストを保存
                output_file = "開成2025_bunko.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(combined_text))
                
                print(f"✅ 結合テキストを保存: {output_file}")
                return output_file
    
    return None


def analyze_kaisei_2025_from_bunko_text(text_file_path: str):
    """bunkoOCRのテキストファイルから開成中2025年度を分析"""
    
    print(f"\n{'='*60}")
    print(f"開成中学校2025年度 入試問題分析")
    print(f"{'='*60}")
    
    # テキストファイルを読み込み
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"\n📄 読み込んだテキスト: {len(text)}文字")
    
    # 大問構造の検出
    sections = []
    
    # 大問パターン（開成中学校用）
    section_patterns = [
        # 「一、次の文章を読んで」パターン
        (r'([一二三四五六七八九十])、次の文章を読んで', 'main_section_comma'),
        # 「一 次の文章を読んで」パターン（スペース区切り）
        (r'([一二三四五六七八九十])\s+次の文章を読んで', 'main_section_space'),
        # 「第一問」などのパターン
        (r'第([一二三四五六七八九十]+)問', 'dai_mon'),
    ]
    
    # すべてのマッチを収集
    all_matches = []
    for pattern, p_type in section_patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            all_matches.append({
                'start': match.start(),
                'end': match.end(),
                'number': match.group(1),
                'type': p_type,
                'full_match': match.group(0)
            })
    
    # 位置順にソート
    all_matches.sort(key=lambda x: x['start'])
    
    # 大問を構築
    for i, match in enumerate(all_matches):
        section_num = len(sections) + 1
        
        # 大問の終了位置を決定
        if i < len(all_matches) - 1:
            end_pos = all_matches[i + 1]['start']
        else:
            end_pos = len(text)
        
        sections.append({
            'number': section_num,
            'start_pos': match['start'],
            'end_pos': end_pos,
            'text': text[match['start']:end_pos],
            'type': '文章読解'
        })
    
    # 大問が見つからない場合は全体を1つの大問として扱う
    if not sections:
        sections.append({
            'number': 1,
            'start_pos': 0,
            'end_pos': len(text),
            'text': text,
            'type': '文章読解'
        })
    
    print(f"\n検出された大問数: {len(sections)}")
    
    # 設問の検出
    all_questions = []
    
    # 設問パターン
    question_patterns = [
        # 基本パターン（問一、問二など）
        (r'問([一二三四五六七八九十]+)', 'kanji_num'),
        # OCR誤認識パターン（間など）
        (r'間([一二三四五六七八九十]+)', 'kanji_num_ocr'),
        # 問1、問2などの数字パターン
        (r'問([1-9])', 'hankaku_num'),
    ]
    
    print(f"\n【設問検出】")
    
    for pattern, pattern_type in question_patterns:
        for match in re.finditer(pattern, text):
            # 設問の周辺テキストを取得
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 200)
            context = text[start:end].replace('\n', ' ')
            
            # 設問タイプを判定
            if '漢字' in context or 'カタカナを漢字に' in context:
                q_type = '漢字・語句'
            elif '記号で答えなさい' in context or '選び' in context:
                q_type = '選択'
            elif '説明しなさい' in context or '理由' in context:
                q_type = '記述'
            elif '抜き出' in context:
                q_type = '抜き出し'
            else:
                q_type = '記述'
            
            # どの大問に属するか判定
            section_num = 1
            for section in sections:
                if section['start_pos'] <= match.start() < section['end_pos']:
                    section_num = section['number']
                    break
            
            question_info = {
                'section': section_num,
                'question': match.group(0),
                'type': q_type,
                'position': match.start(),
                'context': context[:150] + '...' if len(context) > 150 else context
            }
            
            # 重複を避ける
            is_duplicate = False
            for existing_q in all_questions:
                if abs(existing_q['position'] - question_info['position']) < 50:
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
    
    # 出典パターン
    source_patterns = [
        r'（([^）]{1,50}『[^』]{1,100}』[^）]{0,20})）',  # 日本語括弧
        r'（([^）]{1,50}「[^」]{1,100}」[^）]{0,20})）',
        r'\(([^)]{1,50}『[^』]{1,100}』[^)]{0,20})\)',  # 半角括弧
    ]
    
    sources = []
    for pattern in source_patterns:
        for match in re.finditer(pattern, text):
            source_text = match.group(1)
            if len(source_text) > 150:
                continue
            
            # 著者名と作品名を抽出
            if '『' in source_text:
                parts = source_text.split('『')
                if len(parts) >= 2:
                    author = parts[0].strip()
                    title = parts[1].split('』')[0].strip()
                    if 1 <= len(author) <= 20 and 1 <= len(title) <= 50:
                        sources.append({
                            'author': author,
                            'title': title,
                            'full': source_text,
                            'position': match.start()
                        })
    
    # 各大問の出典を特定
    for section in sections:
        section_sources = [s for s in sources if section['start_pos'] <= s['position'] < section['end_pos']]
        if section_sources:
            # 最も近い出典を選択
            closest_source = min(section_sources, key=lambda x: abs(x['position'] - section['start_pos']))
            section['author'] = closest_source['author']
            section['title'] = closest_source['title']
            print(f"\n大問{section['number']}の出典:")
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
        
        # 特殊文字を除去
        problematic_chars = {
            '\ufff9', '\ufffa', '\ufffb', '\ufeff',
            '\u200b', '\u200c', '\u200d',
        }
        cleaned = ''.join(char for char in text if char not in problematic_chars)
        
        # 山括弧〈〉を通常の括弧に置換
        cleaned = cleaned.replace('〈', '＜').replace('〉', '＞')
        
        # 制御文字を除去
        sanitized = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
        
        # 先頭の特殊括弧を修正
        if sanitized.startswith('＜') or sanitized.startswith('〈'):
            sanitized = '「' + sanitized[1:]
        if sanitized.endswith('＞') or sanitized.endswith('〉'):
            sanitized = sanitized[:-1] + '」'
        
        return sanitized[:500]
    
    # データベース形式で保存
    create_database_excel(sections, all_questions, len(text), sanitize_for_excel)
    
    # 通常の分析結果も保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"開成中学校_2025_bunko分析結果_{timestamp}.xlsx"
    
    # 分析結果をExcelに保存
    save_analysis_result(output_file, sections, all_questions, type_counts, len(text), sanitize_for_excel)
    
    print(f"\n✅ 分析結果を保存: {output_file}")
    
    return {
        'sections': sections,
        'questions': all_questions,
        'type_counts': type_counts
    }


def create_database_excel(sections, all_questions, total_chars, sanitize_func):
    """データベース形式のExcelファイルを作成・更新"""
    
    db_filename = "entrance_exam_database.xlsx"
    school_name = "開成中学校"
    year = 2025
    
    try:
        existing_sheets = pd.ExcelFile(db_filename, engine='openpyxl').sheet_names
    except FileNotFoundError:
        existing_sheets = []
    
    # データ行を準備
    data_row = {
        '年度': year,
        '総設問数': len(all_questions),
        '総文字数': total_chars,
        '大問数': len(sections)
    }
    
    # 各大問のデータ
    for i, section in enumerate(sections, 1):
        # 文章ジャンルとテーマを判定
        section_text = section['text'][:1000]
        
        # ジャンル判定
        if any(word in section_text for word in ['小説', '物語', '「', '」', 'と言った']):
            genre = '小説・物語'
        elif any(word in section_text for word in ['評論', '論説', 'について']):
            genre = '評論・論説'
        elif any(word in section_text for word in ['随筆', 'エッセイ', '私は']):
            genre = '随筆・エッセイ'
        else:
            genre = '評論・論説'
        
        # テーマ判定
        if any(word in section_text for word in ['家族', '友情', '成長']):
            theme = '人間関係・成長'
        elif any(word in section_text for word in ['自然', '環境', '生物']):
            theme = '自然・環境'
        elif any(word in section_text for word in ['社会', '文化', '歴史']):
            theme = '社会・文化'
        else:
            theme = '一般'
        
        section_questions = [q for q in all_questions if q['section'] == section['number']]
        
        data_row[f'大問{i}_ジャンル'] = genre
        data_row[f'大問{i}_テーマ'] = theme
        data_row[f'大問{i}_著者'] = sanitize_func(section.get('author', '不明'))
        data_row[f'大問{i}_作品'] = sanitize_func(section.get('title', '不明'))
        data_row[f'大問{i}_設問数'] = len(section_questions)
        data_row[f'大問{i}_文字数'] = len(section['text'])
    
    # 設問タイプ別集計
    type_counts = {}
    for q in all_questions:
        q_type = q['type']
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
    
    for q_type, count in type_counts.items():
        data_row[f'{q_type}_問題数'] = count
    
    # データフレーム作成
    new_df = pd.DataFrame([data_row])
    
    # Excelファイルに書き込み
    with pd.ExcelWriter(db_filename, engine='openpyxl', mode='a' if existing_sheets else 'w', if_sheet_exists='replace') as writer:
        if school_name in existing_sheets:
            existing_df = pd.read_excel(db_filename, sheet_name=school_name)
            existing_df['年度'] = pd.to_numeric(existing_df['年度'], errors='coerce')
            if year in existing_df['年度'].values:
                existing_df = existing_df[existing_df['年度'] != year]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df['年度'] = pd.to_numeric(combined_df['年度'], errors='coerce')
            combined_df = combined_df.sort_values('年度')
        else:
            combined_df = new_df
        
        combined_df.to_excel(writer, sheet_name=school_name, index=False)
    
    print(f"📊 データベース更新: {db_filename} - {school_name}シート")


def save_analysis_result(output_file, sections, all_questions, type_counts, total_chars, sanitize_func):
    """分析結果をExcelファイルに保存"""
    
    # 基本情報
    basic_info = [
        ['基本情報', '', '', '', '', '', '', ''],
        ['学校名', '開成中学校', '', '', '', '', '', ''],
        ['年度', '2025', '', '', '', '', '', ''],
        ['分析日時', datetime.now().strftime('%Y/%m/%d %H:%M'), '', '', '', '', '', ''],
        ['総文字数', f"{total_chars:,}文字", '', '', '', '', '', ''],
        ['大問数', len(sections), '', '', '', '', '', ''],
        ['総設問数', len(all_questions), '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
    ]
    
    # 大問別詳細
    section_header = [['大問別詳細', '', '', '', '', '', '', '']]
    section_data = []
    
    for section in sections:
        section_questions = [q for q in all_questions if q['section'] == section['number']]
        
        # 設問タイプ別集計
        section_type_counts = {}
        for q in section_questions:
            q_type = q['type']
            section_type_counts[q_type] = section_type_counts.get(q_type, 0) + 1
        
        type_desc = ', '.join([f"{t}({c}問)" for t, c in section_type_counts.items()])
        
        section_data.append([
            f"大問{section['number']}",
            '文章読解',
            '',
            sanitize_func(section.get('author', '不明')),
            sanitize_func(section.get('title', '不明')),
            f"{len(section_questions)}問",
            f"{len(section['text']):,}文字",
            type_desc
        ])
    
    # 設問タイプ集計
    type_header = [['', '', '', '', '', '', '', ''], ['設問タイプ集計', '', '', '', '', '', '', '']]
    type_data = []
    for q_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(all_questions)) * 100
        type_data.append([q_type, f"{count}問", f"{percentage:.1f}%", '', '', '', '', ''])
    
    # データフレーム作成
    all_data = basic_info + section_header + section_data + type_header + type_data
    df = pd.DataFrame(all_data)
    
    # Excelに保存
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='分析結果', index=False, header=False)


def main():
    """メイン処理"""
    
    # 既存のテキストファイルを確認
    if Path("開成2025_bunko.txt").exists():
        print("✅ 既存のテキストファイルを使用: 開成2025_bunko.txt")
        text_file = "開成2025_bunko.txt"
    else:
        # bunkoOCRで処理
        text_file = launch_bunko_ocr_for_kaisei()
        if not text_file:
            print("❌ bunkoOCRの処理に失敗しました")
            return
    
    # 分析実行
    result = analyze_kaisei_2025_from_bunko_text(text_file)
    
    print(f"\n{'='*60}")
    print(f"【精度評価】")
    print(f"検出された設問数: {len(result['questions'])}問")
    print(f"目標設問数: 10-15問（一般的な開成の問題数）")
    
    if 10 <= len(result['questions']) <= 15:
        print(f"✅ 高精度での検出に成功しました！")
    else:
        print(f"⚠️  設問数が想定範囲外です。OCR精度を確認してください。")


if __name__ == "__main__":
    main()