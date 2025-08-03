#!/usr/bin/env python3
"""
bunkoOCRの結果から入試問題を分析してデータベースに追加
"""
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

def find_latest_bunko_result():
    """最新のbunkoOCR結果フォルダを見つける"""
    results_dir = Path("/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results")
    
    if not results_dir.exists():
        raise FileNotFoundError(f"bunkoOCR結果フォルダが見つかりません: {results_dir}")
    
    # 最新のフォルダを取得
    folders = [f for f in results_dir.iterdir() if f.is_dir()]
    if not folders:
        raise FileNotFoundError("bunkoOCR結果フォルダが空です")
    
    latest_folder = max(folders, key=lambda x: x.stat().st_mtime)
    print(f"📁 最新のOCR結果フォルダ: {latest_folder.name}")
    
    return latest_folder

def read_all_text_files(folder_path):
    """フォルダ内のすべてのtext*.txtファイルを読み取って結合"""
    text_files = sorted(folder_path.glob("text*.txt"), key=lambda x: int(x.stem.replace('text', '')))
    
    if not text_files:
        raise FileNotFoundError(f"text*.txtファイルが見つかりません: {folder_path}")
    
    print(f"📄 テキストファイル数: {len(text_files)}")
    
    all_text = ""
    for text_file in text_files:
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # 空でないファイルのみ追加
                    all_text += content + "\n"
                    print(f"   ✅ {text_file.name}: {len(content)}文字")
                else:
                    print(f"   ⚠️  {text_file.name}: 空ファイル")
        except Exception as e:
            print(f"   ❌ {text_file.name}: 読み取りエラー - {e}")
    
    return all_text

def extract_source_and_genre(text):
    """テキストから出典と作品情報を抽出"""
    # 出典パターンを探す
    source_patterns = [
        r'(?:作者|著者|詩人|随筆|小説|評論)[:：]?\s*([^\n\r]+)',
        r'「([^」]+)」\s*([^\n\r]+(?:著|作|詩集|小説|随筆|評論))',
        r'([^\n\r]*(?:著|作|詩集|小説|随筆|評論)[^\n\r]*)',
        r'出典[:：]\s*([^\n\r]+)',
    ]
    
    sources = []
    for pattern in source_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                sources.extend([m.strip() for m in match if m.strip()])
            else:
                sources.append(match.strip())
    
    # ジャンル判定
    genre_keywords = {
        '小説': ['小説', '物語', '短編', '長編'],
        '随筆': ['随筆', 'エッセイ', '日記', '手記'],
        '評論': ['評論', '論文', '批評', '解説'],
        '詩': ['詩', '詩集', '短歌', '俳句'],
        '古典': ['古典', '源氏物語', '枕草子', '徒然草'],
        '説明文': ['説明', '解説', '概論']
    }
    
    detected_genre = "不明"
    for genre, keywords in genre_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_genre = genre
            break
    
    return sources, detected_genre

def extract_questions(text):
    """問題文から設問を抽出"""
    # 問題番号パターン
    question_patterns = [
        r'問[一二三四五六七八九十\d]+',
        r'[一二三四五六七八九十\d]+\s*[．.]',
        r'\d+\.',
        r'［\d+］'
    ]
    
    questions = []
    for pattern in question_patterns:
        matches = re.findall(pattern, text)
        questions.extend(matches)
    
    return list(set(questions))  # 重複を除去

def analyze_difficulty(text):
    """問題の難易度を分析（簡易版）"""
    # 語彙の複雑さや問題文の長さなどから判定
    char_count = len(text)
    
    if char_count > 5000:
        return "高"
    elif char_count > 2000:
        return "中"
    else:
        return "低"

def main():
    print("🔍 bunkoOCR結果の分析を開始します...")
    
    try:
        # 最新の結果フォルダを取得
        latest_folder = find_latest_bunko_result()
        
        # すべてのテキストファイルを読み取り
        full_text = read_all_text_files(latest_folder)
        
        if not full_text.strip():
            print("❌ 有効なテキストが見つかりませんでした")
            return
        
        print(f"\n📊 分析開始 - 総文字数: {len(full_text)}")
        
        # 情報抽出
        sources, genre = extract_source_and_genre(full_text)
        questions = extract_questions(full_text)
        difficulty = analyze_difficulty(full_text)
        
        # 結果をまとめる
        analysis_result = {
            "学校名": "開成中学校",
            "年度": "2025",
            "科目": "国語",
            "大問": "1",  # 仮定
            "出典": "; ".join(sources) if sources else "不明",
            "ジャンル": genre,
            "設問数": len(questions),
            "難易度": difficulty,
            "分析日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "文字数": len(full_text),
            "OCRフォルダ": latest_folder.name
        }
        
        print("\n📋 分析結果:")
        for key, value in analysis_result.items():
            print(f"   {key}: {value}")
        
        # 既存のデータベースに追加
        db_path = Path("entrance_exam_database.xlsx")
        
        if db_path.exists():
            print(f"\n📁 既存データベースを読み込み中...")
            df = pd.read_excel(db_path)
        else:
            print(f"\n📝 新しいデータベースを作成中...")
            df = pd.DataFrame()
        
        # 新しい行を追加
        new_row = pd.DataFrame([analysis_result])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Excelファイルに保存
        df.to_excel(db_path, index=False)
        print(f"✅ データベースに保存完了: {db_path}")
        print(f"📊 現在のレコード数: {len(df)}")
        
        # サンプルテキストを表示
        print(f"\n📖 抽出テキスト（最初の500文字）:")
        print(full_text[:500] + "..." if len(full_text) > 500 else full_text)
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()