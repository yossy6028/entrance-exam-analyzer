"""
Excel操作モジュール - データベースの読み書きとバックアップ管理
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import shutil

from config.settings import Settings
from models import AnalysisResult, ExcelExportConfig
from exceptions import (
    ExcelReadError,
    ExcelWriteError,
    BackupError,
    DatabaseError
)
from utils.file_utils import create_backup, ensure_directory_exists
from utils.display_utils import print_success, print_warning, print_error, print_info


class ExcelManager:
    """Excel データベース管理クラス"""
    
    def __init__(self, config: Optional[ExcelExportConfig] = None):
        """
        初期化
        
        Args:
            config: Excel出力設定
        """
        self.config = config or ExcelExportConfig()
        self.db_path = Path(self.config.db_filename)
        
        # 出力ディレクトリを確保
        if self.db_path.parent != Path('.'):
            ensure_directory_exists(self.db_path.parent)
    
    def save_analysis_result(self, result: AnalysisResult) -> bool:
        """
        分析結果をExcelに保存
        
        Args:
            result: 分析結果
        
        Returns:
            成功した場合True
        """
        try:
            # バックアップを作成
            if self.config.create_backup and self.db_path.exists():
                backup_path = self._create_backup()
                if backup_path:
                    print_info(f"バックアップを作成: {backup_path}")
            
            # データフレームを作成
            df = self._create_dataframe(result)
            
            # Excelファイルに書き込み
            self._write_to_excel(df, result.school_name, result.year)
            
            print_success(f"分析結果を保存しました: {result.school_name} {result.year}年")
            return True
        
        except Exception as e:
            print_error(f"Excel保存に失敗しました: {str(e)}")
            return False
    
    def _create_dataframe(self, result: AnalysisResult) -> pd.DataFrame:
        """分析結果からDataFrameを作成"""
        data = {
            '年度': [int(result.year)],
            '総設問数': [result.get_question_count()],
            '総文字数': [result.total_characters],
            '大問数': [result.get_section_count()],
        }
        
        # 大問別情報
        for i, section in enumerate(result.sections, 1):
            # 出典情報を取得
            source = result.sources[i-1] if i <= len(result.sources) else None
            
            data[f'大問{i}_ジャンル'] = [result.genre or '']
            data[f'大問{i}_テーマ'] = [result.theme or '']
            data[f'大問{i}_著者'] = [source.author if source else '']
            data[f'大問{i}_作品'] = [source.title if source else '']
            data[f'大問{i}_設問数'] = [len(section.questions)]
            data[f'大問{i}_文字数'] = [len(section.text)]
        
        # 設問タイプ別集計
        for q_type, count in result.question_types.items():
            data[f'{q_type}_問題数'] = [count]
        
        # タイムスタンプを追加（オプション）
        if self.config.include_timestamp:
            data['更新日時'] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        
        return pd.DataFrame(data)
    
    def _write_to_excel(self, df: pd.DataFrame, school_name: str, year: str):
        """DataFrameをExcelに書き込み"""
        sheet_name = self.config.sheet_name_format.format(school_name=school_name)
        
        try:
            if self.db_path.exists():
                # 既存ファイルを読み込み
                with pd.ExcelFile(self.db_path, engine=Settings.EXCEL_ENGINE) as excel_file:
                    existing_sheets = excel_file.sheet_names
                    
                    # すべてのシートを読み込み
                    all_data = {}
                    for sheet in existing_sheets:
                        all_data[sheet] = pd.read_excel(
                            excel_file,
                            sheet_name=sheet,
                            engine=Settings.EXCEL_ENGINE
                        )
                    
                    # 対象シートの処理
                    if sheet_name in all_data:
                        existing_df = all_data[sheet_name]
                        # 同じ年度のデータを更新または追加
                        updated_df = self._update_or_append(existing_df, df, int(year))
                        all_data[sheet_name] = updated_df
                    else:
                        all_data[sheet_name] = df
                
                # すべてのシートを書き込み
                with pd.ExcelWriter(
                    self.db_path,
                    engine=Settings.EXCEL_ENGINE,
                    mode='w'
                ) as writer:
                    for sheet, data in all_data.items():
                        data.to_excel(writer, sheet_name=sheet, index=False)
            
            else:
                # 新規ファイル作成
                with pd.ExcelWriter(
                    self.db_path,
                    engine=Settings.EXCEL_ENGINE,
                    mode='w'
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        except Exception as e:
            raise ExcelWriteError(str(self.db_path), str(e))
    
    def _update_or_append(self, existing_df: pd.DataFrame, new_df: pd.DataFrame, year: int) -> pd.DataFrame:
        """既存データフレームを更新または追加"""
        # 年度列が存在するか確認
        if '年度' not in existing_df.columns:
            return pd.concat([existing_df, new_df], ignore_index=True)
        
        # 同じ年度のデータがあるか確認
        year_mask = existing_df['年度'] == year
        
        if year_mask.any():
            # 既存データを更新
            # まず該当年度の行を削除
            updated_df = existing_df[~year_mask].copy()
            # 新しいデータを追加
            updated_df = pd.concat([updated_df, new_df], ignore_index=True)
        else:
            # 新しいデータを追加
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # 年度でソート
        updated_df = updated_df.sort_values('年度').reset_index(drop=True)
        
        return updated_df
    
    def _create_backup(self) -> Optional[Path]:
        """バックアップを作成"""
        try:
            backup_dir = Settings.BACKUP_DIR
            return create_backup(self.db_path, backup_dir)
        except Exception as e:
            raise BackupError(str(self.db_path), str(e))
    
    def read_school_data(self, school_name: str) -> Optional[pd.DataFrame]:
        """
        特定の学校のデータを読み込み
        
        Args:
            school_name: 学校名
        
        Returns:
            データフレーム、存在しない場合はNone
        """
        if not self.db_path.exists():
            return None
        
        sheet_name = self.config.sheet_name_format.format(school_name=school_name)
        
        try:
            df = pd.read_excel(
                self.db_path,
                sheet_name=sheet_name,
                engine=Settings.EXCEL_ENGINE
            )
            return df
        except Exception:
            return None
    
    def get_all_schools(self) -> List[str]:
        """
        データベース内のすべての学校名を取得
        
        Returns:
            学校名のリスト
        """
        if not self.db_path.exists():
            return []
        
        try:
            with pd.ExcelFile(self.db_path, engine=Settings.EXCEL_ENGINE) as excel_file:
                return excel_file.sheet_names
        except Exception:
            return []
    
    def export_summary_report(self, output_path: Optional[Path] = None) -> bool:
        """
        サマリーレポートを出力
        
        Args:
            output_path: 出力先パス
        
        Returns:
            成功した場合True
        """
        if not self.db_path.exists():
            print_warning("データベースが存在しません。")
            return False
        
        try:
            output_path = output_path or Path("summary_report.xlsx")
            
            with pd.ExcelFile(self.db_path, engine=Settings.EXCEL_ENGINE) as excel_file:
                summary_data = []
                
                for school in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=school)
                    
                    if not df.empty and '年度' in df.columns:
                        summary = {
                            '学校名': school,
                            'データ年数': len(df),
                            '最古年度': df['年度'].min(),
                            '最新年度': df['年度'].max(),
                            '平均文字数': df['総文字数'].mean() if '総文字数' in df.columns else 0,
                            '平均設問数': df['総設問数'].mean() if '総設問数' in df.columns else 0,
                        }
                        summary_data.append(summary)
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(output_path, index=False, engine=Settings.EXCEL_ENGINE)
                    print_success(f"サマリーレポートを出力: {output_path}")
                    return True
                else:
                    print_warning("サマリーデータがありません。")
                    return False
        
        except Exception as e:
            print_error(f"サマリーレポートの出力に失敗: {str(e)}")
            return False
    
    def validate_database(self) -> Dict[str, Any]:
        """
        データベースの整合性を検証
        
        Returns:
            検証結果の辞書
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        if not self.db_path.exists():
            validation_result['is_valid'] = False
            validation_result['errors'].append("データベースファイルが存在しません")
            return validation_result
        
        try:
            with pd.ExcelFile(self.db_path, engine=Settings.EXCEL_ENGINE) as excel_file:
                validation_result['info']['school_count'] = len(excel_file.sheet_names)
                validation_result['info']['total_records'] = 0
                
                for school in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=school)
                    validation_result['info']['total_records'] += len(df)
                    
                    # 必須列のチェック
                    required_columns = ['年度', '総設問数', '総文字数', '大問数']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        validation_result['warnings'].append(
                            f"{school}: 必須列が不足 {missing_columns}"
                        )
                    
                    # データ型のチェック
                    if '年度' in df.columns:
                        try:
                            df['年度'].astype(int)
                        except Exception:
                            validation_result['errors'].append(
                                f"{school}: 年度列に無効なデータが含まれています"
                            )
                            validation_result['is_valid'] = False
        
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"データベースの読み込みエラー: {str(e)}")
        
        return validation_result