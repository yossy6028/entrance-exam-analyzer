"""
年度検出モジュール - テキストから入試年度を検出
"""
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

from config.settings import Settings
from models import YearDetectionResult
from exceptions import YearDetectionError
from utils.text_utils import normalize_text


@dataclass
class YearPattern:
    """年度パターンの定義"""
    name: str
    pattern: str
    converter: callable
    priority: int = 0


class YearDetector:
    """年度検出クラス"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self._compile_patterns()
    
    def _initialize_patterns(self) -> List[YearPattern]:
        """年度パターンを初期化"""
        patterns = []
        
        # 西暦4桁パターン
        patterns.append(YearPattern(
            name="year_4digit",
            pattern=r'(20\d{2})年度?',
            converter=lambda x: x,
            priority=10
        ))
        
        # 令和パターン
        patterns.append(YearPattern(
            name="reiwa",
            pattern=r'令和(\d{1,2})年度?',
            converter=self._reiwa_to_year,
            priority=9
        ))
        
        # 平成パターン
        patterns.append(YearPattern(
            name="heisei",
            pattern=r'平成(\d{1,2})年度?',
            converter=self._heisei_to_year,
            priority=8
        ))
        
        # 学校名+2桁年度パターン
        for school_pattern in Settings.SCHOOL_YEAR_PATTERNS:
            patterns.append(YearPattern(
                name=f"school_{school_pattern}",
                pattern=school_pattern,
                converter=self._two_digit_to_year,
                priority=7
            ))
        
        # 単独の2桁年度パターン（優先度低）
        patterns.append(YearPattern(
            name="year_2digit",
            pattern=r'(?:^|\s)(\d{2})(?:年|$)',
            converter=self._two_digit_to_year,
            priority=5
        ))
        
        return patterns
    
    def _compile_patterns(self):
        """正規表現パターンをコンパイル"""
        for pattern_obj in self.patterns:
            pattern_obj.compiled = re.compile(pattern_obj.pattern, re.MULTILINE)
    
    def detect_years(self, text: str, file_path: Optional[Path] = None) -> YearDetectionResult:
        """
        テキストから年度を検出
        
        Args:
            text: 検出対象のテキスト
            file_path: ファイルパス（ファイル名からも年度を推測）
        
        Returns:
            YearDetectionResult: 検出結果
        """
        detected_years = {}
        detection_patterns = {}
        
        # ファイル名から年度を推測
        if file_path:
            file_years = self._detect_from_filename(file_path.name)
            if file_years:
                detected_years.update({year: 0 for year in file_years})
                detection_patterns['filename'] = [(0, year) for year in file_years]
        
        # 各パターンで検出
        for pattern_obj in sorted(self.patterns, key=lambda x: x.priority, reverse=True):
            matches = pattern_obj.compiled.finditer(text)
            
            for match in matches:
                try:
                    year = pattern_obj.converter(match.group(1))
                    if self._is_valid_year(year):
                        position = match.start()
                        
                        # 重複チェック（位置が近い場合は優先度の高いものを採用）
                        if not self._is_duplicate(year, position, detected_years):
                            detected_years[year] = position
                            
                            if pattern_obj.name not in detection_patterns:
                                detection_patterns[pattern_obj.name] = []
                            detection_patterns[pattern_obj.name].append((position, year))
                except (ValueError, IndexError):
                    continue
        
        # 結果を作成
        years = sorted(detected_years.keys())
        confidence = self._calculate_confidence(years, detection_patterns)
        
        # 年度が検出できない場合でもファイル名から推測した年度があれば使用
        if not years and file_path:
            file_years = self._detect_from_filename(file_path.name)
            if file_years:
                years = file_years
                confidence = 0.5  # ファイル名のみからの推測なので信頼度は低め
        
        if not years:
            raise YearDetectionError(text[:200], [p.name for p in self.patterns])
        
        return YearDetectionResult(
            years=years,
            detection_patterns=detection_patterns,
            confidence=confidence
        )
    
    def _detect_from_filename(self, filename: str) -> List[str]:
        """ファイル名から年度を検出"""
        years = []
        
        # 連続する年度範囲（例: 14-25）
        range_match = re.search(r'(\d{2})-(\d{2})', filename)
        if range_match:
            start = self._two_digit_to_year(range_match.group(1))
            end = self._two_digit_to_year(range_match.group(2))
            
            if self._is_valid_year(start) and self._is_valid_year(end):
                start_year = int(start)
                end_year = int(end)
                if start_year <= end_year:
                    years = [str(year) for year in range(start_year, end_year + 1)]
        
        # 個別の年度
        if not years:
            # 4桁年度
            matches_4digit = re.findall(r'20\d{2}', filename)
            for match in matches_4digit:
                if self._is_valid_year(match) and match not in years:
                    years.append(match)
            
            # 2桁年度（学校名の前後にある場合）
            # パターン1: 学校名の後ろ（例: 開成25）
            school_pattern_after = r'(?:開成|武蔵|桜蔭|桜陰|麻布|渋谷|渋渋)(\d{2})'
            school_matches = re.findall(school_pattern_after, filename)
            for match in school_matches:
                year = self._two_digit_to_year(match)
                if self._is_valid_year(year) and year not in years:
                    years.append(year)
            
            # パターン2: 学校名の前（例: 25開成）
            school_pattern_before = r'(\d{2})(?:開成|武蔵|桜蔭|桜陰|麻布|渋谷|渋渋)'
            school_matches = re.findall(school_pattern_before, filename)
            for match in school_matches:
                year = self._two_digit_to_year(match)
                if self._is_valid_year(year) and year not in years:
                    years.append(year)
            
            # それでも見つからない場合は単独の2桁数字を試す
            if not years:
                matches_2digit = re.findall(r'(?:^|\D)(\d{2})(?:\D|$)', filename)
                for match in matches_2digit:
                    year = self._two_digit_to_year(match)
                    if self._is_valid_year(year) and year not in years:
                        years.append(year)
        
        return years
    
    def _two_digit_to_year(self, two_digit: str) -> str:
        """2桁年度を4桁に変換"""
        try:
            num = int(two_digit)
            if Settings.MIN_YEAR_2DIGIT <= num <= Settings.MAX_YEAR_2DIGIT:
                return f"20{num:02d}"
            elif 90 <= num <= 99:
                return f"19{num:02d}"
            else:
                return f"20{num:02d}"
        except ValueError:
            return two_digit
    
    def _reiwa_to_year(self, reiwa_year: str) -> str:
        """令和を西暦に変換"""
        try:
            year = 2018 + int(reiwa_year)
            return str(year)
        except ValueError:
            return reiwa_year
    
    def _heisei_to_year(self, heisei_year: str) -> str:
        """平成を西暦に変換"""
        try:
            year = 1988 + int(heisei_year)
            return str(year)
        except ValueError:
            return heisei_year
    
    def _is_valid_year(self, year: str) -> bool:
        """有効な年度かチェック"""
        try:
            year_num = int(year)
            return Settings.MIN_VALID_YEAR <= year_num <= Settings.MAX_VALID_YEAR
        except ValueError:
            return False
    
    def _is_duplicate(self, year: str, position: int, detected_years: Dict[str, int]) -> bool:
        """重複した検出かチェック"""
        if year not in detected_years:
            return False
        
        # 同じ年度が近い位置で検出された場合は重複とみなす
        existing_position = detected_years[year]
        return abs(position - existing_position) < 100
    
    def _calculate_confidence(self, years: List[str], patterns: Dict) -> float:
        """検出の信頼度を計算"""
        if not years:
            return 0.0
        
        score = 0.0
        
        # 複数のパターンで検出された場合は信頼度が高い
        if len(patterns) > 1:
            score += 0.3
        
        # 年度が連続している場合は信頼度が高い
        if len(years) > 1:
            year_nums = sorted([int(y) for y in years])
            consecutive = all(
                year_nums[i] + 1 == year_nums[i + 1]
                for i in range(len(year_nums) - 1)
            )
            if consecutive:
                score += 0.3
        
        # 高優先度パターンで検出された場合
        if any(p in patterns for p in ['year_4digit', 'reiwa', 'heisei']):
            score += 0.4
        else:
            score += 0.2
        
        return min(score, 1.0)
    
    def split_text_by_years(self, text: str, years: List[str]) -> Dict[str, str]:
        """
        年度ごとにテキストを分割
        
        Args:
            text: 分割対象のテキスト
            years: 検出された年度のリスト
        
        Returns:
            年度ごとのテキスト辞書
        """
        if len(years) <= 1:
            # 単一年度の場合は分割しない
            return {years[0]: text} if years else {}
        
        year_positions = []
        
        # 各年度の位置を特定
        for year in years:
            # 様々なパターンで年度マーカーを検索
            patterns = [
                f"{year}年",
                f"令和{self._year_to_reiwa(year)}年" if self._year_to_reiwa(year) else None,
                f"平成{self._year_to_heisei(year)}年" if self._year_to_heisei(year) else None,
            ]
            
            # 2桁年度の場合、学校名パターンも追加
            two_digit = year[-2:] if len(year) == 4 else year
            for school_pattern in ['武蔵', '開成', '麻布', '桜蔭']:
                patterns.append(f"{school_pattern}{two_digit}")
            
            for pattern in patterns:
                if pattern:
                    pos = text.find(pattern)
                    if pos != -1:
                        year_positions.append((pos, year))
                        break
        
        # 位置でソート
        year_positions.sort()
        
        # テキストを分割
        result = {}
        for i, (pos, year) in enumerate(year_positions):
            if i < len(year_positions) - 1:
                next_pos = year_positions[i + 1][0]
                year_text = text[pos:next_pos]
            else:
                year_text = text[pos:]
            
            result[year] = year_text
        
        return result
    
    def _year_to_reiwa(self, year: str) -> Optional[str]:
        """西暦を令和に変換"""
        try:
            year_num = int(year)
            if year_num >= 2019:
                return str(year_num - 2018)
        except ValueError:
            pass
        return None
    
    def _year_to_heisei(self, year: str) -> Optional[str]:
        """西暦を平成に変換"""
        try:
            year_num = int(year)
            if 1989 <= year_num <= 2019:
                return str(year_num - 1988)
        except ValueError:
            pass
        return None