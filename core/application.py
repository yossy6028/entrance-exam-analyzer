"""
メインアプリケーションクラス - 全体のコーディネーション
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from config.settings import Settings
from models import (
    AnalysisResult,
    ExamDocument,
    FileSelectionResult,
    YearDetectionResult,
    ExcelExportConfig,
    ProcessingStatus
)
from modules.year_detector import YearDetector
from modules.school_detector import SchoolDetector
from modules.file_selector import FileSelector
from modules.excel_manager import ExcelManager
from modules.text_analyzer import TextAnalyzer
from plugins.loader import get_plugin_loader
from exceptions import (
    EntranceExamAnalyzerError,
    FileProcessingError,
    AnalysisError
)
from utils.text_utils import detect_encoding, split_text_by_years
from utils.file_utils import is_valid_text_file, ensure_directory_exists
from utils.display_utils import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_progress
)


class EntranceExamAnalyzer:
    """入試問題分析アプリケーションのメインクラス"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初期化
        
        Args:
            config: アプリケーション設定（オプション）
        """
        self.config = config or {}
        self._initialize_components()
        self._setup_logging()
    
    def _initialize_components(self):
        """コンポーネントを初期化"""
        self.year_detector = YearDetector()
        self.school_detector = SchoolDetector()
        self.file_selector = FileSelector()
        self.text_analyzer = TextAnalyzer()
        self.excel_manager = ExcelManager()
        self.plugin_loader = get_plugin_loader()
        
        # ディレクトリを確保
        ensure_directory_exists(Settings.OUTPUT_DIR)
        ensure_directory_exists(Settings.BACKUP_DIR)
        ensure_directory_exists(Settings.LOG_DIR)
    
    def _setup_logging(self):
        """ロギングをセットアップ"""
        log_file = Settings.LOG_DIR / "analyzer.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self, file_path: Optional[str] = None) -> bool:
        """
        アプリケーションを実行
        
        Args:
            file_path: 解析対象ファイルのパス（オプション）
        
        Returns:
            成功した場合True
        """
        try:
            print_header("入試問題テキスト分析システム", 60)
            
            # ファイル選択
            file_result = self._select_file(file_path)
            if file_result.cancelled or not file_result.selected_file:
                print_warning("キャンセルされました。")
                return False
            
            # ファイル読み込み
            document = self._load_document(file_result.selected_file)
            if not document:
                return False
            
            # 学校名・年度の確認
            if not self._confirm_school_and_years(document):
                return False
            
            # 年度ごとに分析
            results = self._analyze_by_years(document)
            
            # 結果を保存
            self._save_results(results)
            
            print_success("分析が完了しました！")
            return True
        
        except EntranceExamAnalyzerError as e:
            print_error(f"エラー: {e}")
            self.logger.error(f"Application error: {e}", exc_info=True)
            return False
        
        except Exception as e:
            print_error(f"予期しないエラー: {e}")
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return False
    
    def _select_file(self, file_path: Optional[str]) -> FileSelectionResult:
        """ファイルを選択"""
        return self.file_selector.select_file(file_path)
    
    def _load_document(self, file_path: Path) -> Optional[ExamDocument]:
        """ドキュメントを読み込み"""
        try:
            print_section("ファイル読み込み中...")
            
            # エンコーディングを検出
            encoding = detect_encoding(file_path)
            if not encoding:
                raise FileProcessingError(f"エンコーディングを検出できません: {file_path}")
            
            # ファイルを読み込み
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 学校名を検出
            school_name, confidence = self.school_detector.detect_school(content, file_path)
            print_info(f"検出された学校: {school_name} (信頼度: {confidence:.1%})")
            
            # 年度を検出
            year_result = self.year_detector.detect_years(content, file_path)
            print_info(f"検出された年度: {', '.join(year_result.years)}")
            
            return ExamDocument(
                file_path=file_path,
                school_name=school_name,
                years=year_result.years,
                content=content,
                encoding=encoding
            )
        
        except Exception as e:
            print_error(f"ファイル読み込みエラー: {e}")
            return None
    
    def _confirm_school_and_years(self, document: ExamDocument) -> bool:
        """学校名と年度を確認"""
        print_section("検出結果の確認")
        print(f"学校名: {document.school_name}")
        print(f"年度: {', '.join(document.years)}")
        
        response = input("\nこの情報で正しいですか？ (y/n): ").strip().lower()
        
        if response != 'y':
            # 手動で修正
            print_section("手動修正")
            
            # 学校名の修正
            school_input = input(f"学校名 [{document.school_name}]: ").strip()
            if school_input:
                document.school_name = self.school_detector.normalize_school_name(school_input)
            
            # 年度の修正
            years_input = input(f"年度（カンマ区切り） [{', '.join(document.years)}]: ").strip()
            if years_input:
                document.years = [y.strip() for y in years_input.split(',')]
        
        return True
    
    def _analyze_by_years(self, document: ExamDocument) -> List[AnalysisResult]:
        """年度ごとに分析"""
        results = []
        
        # 適切なプラグインを取得
        plugin = self.plugin_loader.get_plugin_for_school(document.school_name)
        print_info(f"使用プラグイン: {plugin.info.name}")
        
        if document.is_multi_year():
            # 複数年度の場合はテキストを分割
            print_section("複数年度の分析")
            year_texts = self.year_detector.split_text_by_years(
                document.content,
                document.years
            )
            
            for i, (year, text) in enumerate(year_texts.items(), 1):
                print_progress(i, len(year_texts), f"分析中: {year}年")
                
                result = plugin.analyze(text, document.school_name, year)
                results.append(result)
        else:
            # 単一年度の場合
            print_section("分析中...")
            year = document.years[0] if document.years else "不明"
            
            result = plugin.analyze(document.content, document.school_name, year)
            results.append(result)
        
        return results
    
    def _save_results(self, results: List[AnalysisResult]):
        """結果を保存"""
        print_section("結果の保存")
        
        for result in results:
            # 結果を表示
            self._display_result(result)
            
            # Excelに保存
            if self.excel_manager.save_analysis_result(result):
                print_success(f"保存完了: {result.school_name} {result.year}年")
            else:
                print_warning(f"保存失敗: {result.school_name} {result.year}年")
    
    def _display_result(self, result: AnalysisResult):
        """分析結果を表示"""
        print(f"\n--- {result.school_name} {result.year}年 ---")
        print(f"総文字数: {result.total_characters:,}")
        print(f"大問数: {result.get_section_count()}")
        print(f"総設問数: {result.get_question_count()}")
        
        print("\n設問タイプ別:")
        for q_type, count in result.question_types.items():
            if count > 0:
                print(f"  {q_type}: {count}問")
        
        if result.sources:
            print("\n出典:")
            for i, source in enumerate(result.sources, 1):
                if source.author or source.title:
                    print(f"  {i}. ", end="")
                    if source.author:
                        print(f"{source.author}", end="")
                    if source.title:
                        print(f"『{source.title}』", end="")
                    print()
        
        if result.theme:
            print(f"\nテーマ: {result.theme}")
        if result.genre:
            print(f"ジャンル: {result.genre}")
    
    def batch_analyze(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        複数ファイルをバッチ分析
        
        Args:
            file_paths: ファイルパスのリスト
        
        Returns:
            分析結果のサマリー
        """
        summary = {
            'total': len(file_paths),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        print_header(f"バッチ分析 ({len(file_paths)}ファイル)", 60)
        
        for i, file_path in enumerate(file_paths, 1):
            print_progress(i, len(file_paths), f"処理中: {file_path.name}")
            
            try:
                # ドキュメントを読み込み
                document = self._load_document(file_path)
                if not document:
                    summary['failed'] += 1
                    continue
                
                # 分析
                results = self._analyze_by_years(document)
                
                # 保存
                for result in results:
                    if self.excel_manager.save_analysis_result(result):
                        summary['success'] += 1
                        summary['results'].append(result)
                    else:
                        summary['failed'] += 1
            
            except Exception as e:
                self.logger.error(f"Batch analysis error for {file_path}: {e}")
                summary['failed'] += 1
        
        return summary