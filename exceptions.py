"""
カスタム例外クラスの定義
"""


class EntranceExamAnalyzerError(Exception):
    """入試問題分析システムの基底例外クラス"""
    pass


class FileProcessingError(EntranceExamAnalyzerError):
    """ファイル処理に関する例外"""
    pass


class EncodingError(FileProcessingError):
    """エンコーディング関連のエラー"""
    def __init__(self, file_path: str, tried_encodings: list = None):
        self.file_path = file_path
        self.tried_encodings = tried_encodings or []
        message = f"ファイル '{file_path}' のエンコーディングを検出できませんでした。"
        if self.tried_encodings:
            message += f" 試行したエンコーディング: {', '.join(self.tried_encodings)}"
        super().__init__(message)


class InvalidFileError(FileProcessingError):
    """無効なファイルエラー"""
    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        message = f"無効なファイル: '{file_path}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class PathTraversalError(FileProcessingError):
    """パストラバーサル攻撃の検出"""
    def __init__(self, path: str):
        self.path = path
        message = f"セキュリティ違反: 許可されていないパスへのアクセス試行 '{path}'"
        super().__init__(message)


class AnalysisError(EntranceExamAnalyzerError):
    """テキスト分析に関する例外"""
    pass


class YearDetectionError(AnalysisError):
    """年度検出エラー"""
    def __init__(self, text_sample: str = "", patterns_tried: list = None):
        self.text_sample = text_sample[:100] if text_sample else ""
        self.patterns_tried = patterns_tried or []
        message = "テキストから年度を検出できませんでした。"
        if self.text_sample:
            message += f" サンプル: '{self.text_sample}...'"
        super().__init__(message)


class SchoolDetectionError(AnalysisError):
    """学校名検出エラー"""
    def __init__(self, text_sample: str = ""):
        self.text_sample = text_sample[:100] if text_sample else ""
        message = "テキストから学校名を検出できませんでした。"
        if self.text_sample:
            message += f" サンプル: '{self.text_sample}...'"
        super().__init__(message)


class SectionParsingError(AnalysisError):
    """セクション（大問）解析エラー"""
    def __init__(self, section_number: int = None, reason: str = ""):
        self.section_number = section_number
        self.reason = reason
        message = "セクションの解析に失敗しました。"
        if section_number is not None:
            message = f"セクション {section_number} の解析に失敗しました。"
        if reason:
            message += f" 理由: {reason}"
        super().__init__(message)


class QuestionParsingError(AnalysisError):
    """設問解析エラー"""
    def __init__(self, question_text: str = "", reason: str = ""):
        self.question_text = question_text[:50] if question_text else ""
        self.reason = reason
        message = "設問の解析に失敗しました。"
        if self.question_text:
            message += f" 設問: '{self.question_text}...'"
        if reason:
            message += f" 理由: {reason}"
        super().__init__(message)


class DatabaseError(EntranceExamAnalyzerError):
    """データベース（Excel）操作に関する例外"""
    pass


class ExcelReadError(DatabaseError):
    """Excel読み込みエラー"""
    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        message = f"Excelファイル '{file_path}' の読み込みに失敗しました。"
        if reason:
            message += f" 理由: {reason}"
        super().__init__(message)


class ExcelWriteError(DatabaseError):
    """Excel書き込みエラー"""
    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        message = f"Excelファイル '{file_path}' への書き込みに失敗しました。"
        if reason:
            message += f" 理由: {reason}"
        super().__init__(message)


class BackupError(DatabaseError):
    """バックアップエラー"""
    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        message = f"ファイル '{file_path}' のバックアップに失敗しました。"
        if reason:
            message += f" 理由: {reason}"
        super().__init__(message)


class ConfigurationError(EntranceExamAnalyzerError):
    """設定に関する例外"""
    pass


class MissingConfigError(ConfigurationError):
    """必須設定の欠落"""
    def __init__(self, config_name: str):
        self.config_name = config_name
        message = f"必須設定 '{config_name}' が見つかりません。"
        super().__init__(message)


class InvalidConfigError(ConfigurationError):
    """無効な設定値"""
    def __init__(self, config_name: str, value: any, expected_type: str = ""):
        self.config_name = config_name
        self.value = value
        self.expected_type = expected_type
        message = f"設定 '{config_name}' の値が無効です: {value}"
        if expected_type:
            message += f" (期待される型: {expected_type})"
        super().__init__(message)


class ValidationError(EntranceExamAnalyzerError):
    """バリデーションエラー"""
    def __init__(self, field: str, value: any, constraint: str = ""):
        self.field = field
        self.value = value
        self.constraint = constraint
        message = f"バリデーションエラー: フィールド '{field}' の値 '{value}' が無効です。"
        if constraint:
            message += f" 制約: {constraint}"
        super().__init__(message)