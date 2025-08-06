"""
柔軟なExcelデータベース用フォーマッター
様々な出題パターンに対応可能な設計
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import shutil


class FlexibleExcelFormatter:
    """様々な学校の出題パターンに対応する柔軟なExcelフォーマッター"""
    
    # 基本列（全学校共通）
    BASE_COLUMNS = [
        '年度',
        '分析日',
        '総文字数',
        '大問数',
        '総設問数',
    ]
    
    # 大問関連の列テンプレート（最大6問まで対応）
    SECTION_TEMPLATE = [
        '大問{}_ジャンル',  # 小説・物語、論説文、随筆、説明文、詩、韻文
        '大問{}_テーマ',
        '大問{}_著者',
        '大問{}_作品',
        '大問{}_出版社',
        '大問{}_文字数',
        '大問{}_設問数',
        '大問{}_内容概要',  # 詳細な内容説明
        '大問{}_設問詳細',  # 各設問の内容
        '大問{}_出題形式',  # 本文のみ、本文＋資料、会話文形式など
        '大問{}_特殊要素',  # 図表、グラフ、写真などの有無
    ]
    
    # 設問タイプ（拡張版）
    QUESTION_TYPES = [
        '記述_問題数',
        '記述_字数指定あり',  # 字数指定がある記述問題の数
        '記述_字数指定なし',  # 字数指定がない記述問題の数
        '選択_問題数',
        '選択_3択',
        '選択_4択',
        '選択_5択',
        '選択_6択',
        '選択_複数選択',  # 複数選択（2つ以上選ぶ）
        '抜き出し_問題数',
        '漢字_問題数',
        '語句_問題数',
        '文法_問題数',
        '脱文挿入_問題数',
        '並び替え_問題数',
        '空欄補充_問題数',
        '要約_問題数',
        '作文_問題数',
        'その他_問題数',
    ]
    
    # 追加情報列
    ADDITIONAL_COLUMNS = [
        '記述_最大字数',  # 記述問題の最大字数制限
        '記述_最小字数',  # 記述問題の最小字数制限
        '選択肢_最大数',  # 選択問題の最大選択肢数
        '図表_使用有無',  # 図表を使った問題の有無
        '詩歌_有無',      # 詩や短歌・俳句の出題有無
        '出題傾向',
        '特記事項',
        'OCRファイル名',
        '備考',
    ]
    
    def __init__(self, excel_path: str = "entrance_exam_database.xlsx", max_sections: int = 6):
        """
        初期化
        
        Args:
            excel_path: Excelファイルのパス
            max_sections: 対応する最大大問数（デフォルト6）
        """
        self.excel_path = excel_path
        self.max_sections = max_sections
        
        # 動的に列を生成
        self.columns = self._generate_columns()
    
    def _generate_columns(self) -> List[str]:
        """列定義を動的に生成"""
        columns = self.BASE_COLUMNS.copy()
        
        # 大問の列を追加（最大数まで）
        for i in range(1, self.max_sections + 1):
            for template in self.SECTION_TEMPLATE:
                columns.append(template.format(i))
        
        # 設問タイプと追加情報を追加
        columns.extend(self.QUESTION_TYPES)
        columns.extend(self.ADDITIONAL_COLUMNS)
        
        return columns
    
    def format_analysis_data(self, 
                            school_name: str,
                            year: int,
                            analysis_result: Dict[str, Any],
                            ocr_filename: str = None,
                            additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析結果を柔軟なフォーマットに整形
        
        Args:
            school_name: 学校名
            year: 年度
            analysis_result: 分析結果の辞書
            ocr_filename: OCRファイル名
            additional_info: 追加情報（記述字数、特殊要素など）
            
        Returns:
            整形されたデータ辞書
        """
        # 空の行データを作成
        row_data = {col: None for col in self.columns}
        
        # 基本情報を設定
        row_data['年度'] = year
        row_data['分析日'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_data['総文字数'] = analysis_result.get('total_characters', 0)
        row_data['大問数'] = len(analysis_result.get('sections', []))
        row_data['総設問数'] = analysis_result.get('total_questions', 0)
        
        # 各大問の情報を設定
        sections = analysis_result.get('sections', [])
        for i, section in enumerate(sections[:self.max_sections], 1):
            prefix = f'大問{i}_'
            
            # 出典情報
            if section.get('source'):
                row_data[f'{prefix}著者'] = section['source'].get('author')
                row_data[f'{prefix}作品'] = section['source'].get('work')
                row_data[f'{prefix}出版社'] = section['source'].get('publisher')
            
            # 基本情報
            row_data[f'{prefix}ジャンル'] = section.get('genre', '不明')
            row_data[f'{prefix}テーマ'] = section.get('theme', '不明')
            row_data[f'{prefix}文字数'] = section.get('characters', 0)
            row_data[f'{prefix}設問数'] = len(section.get('questions', []))
            
            # 追加情報
            if section.get('content_summary'):
                row_data[f'{prefix}内容概要'] = section['content_summary']
            if section.get('question_details'):
                row_data[f'{prefix}設問詳細'] = section['question_details']
            if section.get('format'):
                row_data[f'{prefix}出題形式'] = section['format']
            if section.get('special_elements'):
                row_data[f'{prefix}特殊要素'] = section['special_elements']
        
        # 設問タイプ別集計（より詳細に）
        question_types = analysis_result.get('question_types', {})
        
        # 標準的なマッピング
        type_mapping = {
            '記述': '記述_問題数',
            '選択': '選択_問題数',
            '記号選択': '選択_問題数',
            '抜き出し': '抜き出し_問題数',
            '漢字': '漢字_問題数',
            '語句': '語句_問題数',
            '漢字・語句': ['漢字_問題数', '語句_問題数'],  # 分割
            '文法': '文法_問題数',
            '脱文挿入': '脱文挿入_問題数',
            '並び替え': '並び替え_問題数',
            '空欄補充': '空欄補充_問題数',
            '要約': '要約_問題数',
            '作文': '作文_問題数',
        }
        
        # カウントを設定
        for q_type, count in question_types.items():
            if q_type in type_mapping:
                mapped = type_mapping[q_type]
                if isinstance(mapped, list):
                    # 複数の列に分割する場合
                    for col in mapped:
                        if col in row_data:
                            row_data[col] = (row_data[col] or 0) + count // len(mapped)
                else:
                    # 単一の列にマップ
                    if mapped in row_data:
                        row_data[mapped] = count
            else:
                # その他として扱う
                row_data['その他_問題数'] = (row_data['その他_問題数'] or 0) + count
        
        # 追加情報を設定
        if additional_info:
            for key, value in additional_info.items():
                if key in row_data:
                    row_data[key] = value
        
        # OCRファイル名
        if ocr_filename:
            row_data['OCRファイル名'] = ocr_filename
        
        return row_data
    
    def save_to_excel(self, 
                     school_name: str,
                     row_data: Dict[str, Any],
                     backup: bool = True) -> bool:
        """
        データをExcelファイルに保存（改良版）
        
        Args:
            school_name: 学校名（シート名）
            row_data: 保存するデータ
            backup: バックアップを作成するか
            
        Returns:
            成功した場合True
        """
        try:
            # バックアップ作成
            if backup and os.path.exists(self.excel_path):
                backup_dir = "data/backups"
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(
                    backup_dir,
                    f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.excel_path)}"
                )
                shutil.copy2(self.excel_path, backup_path)
                print(f"バックアップを作成: {backup_path}")
            
            # 既存のExcelファイルを読み込むか新規作成
            if os.path.exists(self.excel_path):
                # 既存ファイルから全シートを読み込み
                with pd.ExcelFile(self.excel_path) as xls:
                    sheets = {sheet: pd.read_excel(xls, sheet_name=sheet) 
                             for sheet in xls.sheet_names}
            else:
                sheets = {}
            
            # 学校のシートが存在しない場合は新規作成
            if school_name not in sheets:
                # 必要な列のみでDataFrameを作成
                sheets[school_name] = pd.DataFrame(columns=self.columns)
            
            # データフレームを取得
            df = sheets[school_name]
            
            # 列の整合性を確保（新しい列があれば追加）
            for col in row_data.keys():
                if col not in df.columns:
                    df[col] = None
            
            # 同じ年度のデータが存在する場合は更新、なければ追加
            year = row_data['年度']
            if not df.empty and year in df['年度'].values:
                # 既存データを更新
                index = df[df['年度'] == year].index[0]
                for col, value in row_data.items():
                    if col in df.columns:
                        df.at[index, col] = value
                print(f"{school_name} {year}年のデータを更新")
            else:
                # 新規データを追加
                new_row = pd.DataFrame([row_data])
                df = pd.concat([df, new_row], ignore_index=True)
                print(f"{school_name} {year}年のデータを新規追加")
            
            # 年度順にソート
            df = df.sort_values('年度')
            sheets[school_name] = df
            
            # Excelファイルに書き込み
            with pd.ExcelWriter(self.excel_path, engine='openpyxl', mode='w') as writer:
                for sheet_name, sheet_df in sheets.items():
                    # NaNを空文字に変換してから保存
                    sheet_df = sheet_df.fillna('')
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"データを保存しました: {self.excel_path}")
            return True
            
        except Exception as e:
            print(f"Excel保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_school_summary(self, school_name: str) -> str:
        """
        学校のデータサマリーを取得
        
        Args:
            school_name: 学校名
            
        Returns:
            サマリー文字列
        """
        if not os.path.exists(self.excel_path):
            return f"{school_name}のデータが存在しません"
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name=school_name)
            
            if df.empty:
                return f"{school_name}のデータが空です"
            
            summary = []
            summary.append(f"【{school_name} データサマリー】")
            summary.append(f"登録年度: {df['年度'].min()}年 〜 {df['年度'].max()}年（計{len(df)}年分）")
            
            # 平均値の計算
            if '総文字数' in df.columns:
                avg_chars = df['総文字数'].mean()
                summary.append(f"平均総文字数: {avg_chars:,.0f}文字")
            
            if '総設問数' in df.columns:
                avg_questions = df['総設問数'].mean()
                summary.append(f"平均設問数: {avg_questions:.1f}問")
            
            # 最頻出ジャンル
            genre_cols = [col for col in df.columns if 'ジャンル' in col]
            if genre_cols:
                all_genres = []
                for col in genre_cols:
                    genres = df[col].dropna().tolist()
                    all_genres.extend([g for g in genres if g])
                
                if all_genres:
                    from collections import Counter
                    genre_counter = Counter(all_genres)
                    most_common = genre_counter.most_common(3)
                    summary.append(f"頻出ジャンル: {', '.join([f'{g[0]}({g[1]}回)' for g in most_common])}")
            
            return '\n'.join(summary)
            
        except Exception as e:
            return f"データ読み込みエラー: {e}"