"""
データモデル定義 - データクラスを使用した型安全な構造
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path


@dataclass
class ExamSource:
    """出典情報"""
    author: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[str] = None
    raw_source: Optional[str] = None


@dataclass
class Question:
    """設問情報"""
    number: int
    text: str
    type: str  # '記述', '選択', '漢字・語句', '抜き出し'
    section: int
    character_limit: Optional[tuple[int, int]] = None  # (min, max)
    choice_count: Optional[int] = None


@dataclass
class Section:
    """大問（セクション）情報"""
    number: int
    marker: str
    text: str
    start_pos: int
    end_pos: int
    questions: List[Question] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """分析結果"""
    school_name: str
    year: str
    total_characters: int
    sections: List[Section]
    questions: List[Question]
    question_types: Dict[str, int]
    sources: List[ExamSource]
    theme: Optional[str] = None
    genre: Optional[str] = None
    
    def get_question_count(self) -> int:
        """総設問数を取得"""
        return len(self.questions)
    
    def get_section_count(self) -> int:
        """大問数を取得"""
        return len(self.sections)
    
    def get_source_count(self) -> int:
        """出典数を取得"""
        return len(self.sources)


@dataclass
class ExamDocument:
    """入試問題文書"""
    file_path: Path
    school_name: str
    years: List[str]
    content: str
    encoding: str = 'utf-8'
    
    def is_multi_year(self) -> bool:
        """複数年度を含むかチェック"""
        return len(self.years) > 1


@dataclass
class FileSelectionResult:
    """ファイル選択結果"""
    selected_file: Optional[Path]
    selection_method: str  # 'list', 'drag_drop', 'gui', 'manual', 'cli_arg'
    cancelled: bool = False


@dataclass
class YearDetectionResult:
    """年度検出結果"""
    years: List[str]
    detection_patterns: Dict[str, List[tuple[int, str]]]  # パターン名: [(位置, 年度)]
    confidence: float  # 0.0-1.0


@dataclass
class ExcelExportConfig:
    """Excel出力設定"""
    db_filename: str = "entrance_exam_database.xlsx"
    create_backup: bool = True
    include_timestamp: bool = True
    sheet_name_format: str = "{school_name}"
    
    
@dataclass
class ProcessingStatus:
    """処理状態"""
    current_step: str
    total_steps: int
    current_progress: float  # 0.0-1.0
    message: str
    start_time: datetime = field(default_factory=datetime.now)
    
    def get_elapsed_time(self) -> float:
        """経過時間（秒）を取得"""
        return (datetime.now() - self.start_time).total_seconds()