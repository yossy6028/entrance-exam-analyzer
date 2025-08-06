"""
汎用入試問題分析モジュール
すべての学校に対応する統一された分析ロジック
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from models import AnalysisResult, Section, ExamSource as Source
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


class UniversalAnalyzer:
    """すべての学校に対応する汎用分析クラス"""
    
    def __init__(self):
        """初期化"""
        self.question_patterns = Settings.QUESTION_PATTERNS
        self.compiled_patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, List]:
        """パターンをコンパイル"""
        compiled = {}
        for q_type, patterns in self.question_patterns.items():
            compiled[q_type] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in patterns
            ]
        return compiled
    
    def analyze(self, text: str, school_name: str, year: str) -> AnalysisResult:
        """
        入試問題テキストを分析
        
        Args:
            text: 分析対象のテキスト
            school_name: 学校名
            year: 年度
            
        Returns:
            分析結果
        """
        logger.info(f"分析開始: {school_name} {year}年")
        
        # 基本分析
        sections = self._analyze_sections(text)
        question_types = self._analyze_question_types(text)
        sources = self._extract_sources(text)
        theme = self._detect_theme(text)
        genre = self._detect_genre(text)
        
        # 結果を作成
        result = AnalysisResult(
            school_name=school_name,
            year=year,
            total_characters=len(text.replace(' ', '').replace('\n', '')),
            sections=sections,
            questions=[],  # 空のリストを設定
            question_types=question_types,
            sources=sources,
            theme=theme,
            genre=genre
        )
        
        logger.info(f"分析完了: 大問{len(sections)}個、設問{result.get_question_count()}問")
        
        return result
    
    def _analyze_sections(self, text: str) -> List[Section]:
        """セクション（大問）を分析"""
        sections = []
        
        # 大問パターン
        section_patterns = [
            r'[一二三四五六七八九十][\s　]*[．.]',
            r'第[一二三四五六七八九十]問',
            r'問[一二三四五六七八九十]',
            r'[１２３４５６７８９０]+[\s　]*[．.]',
            r'\d+[\s　]*[．.]',
        ]
        
        # パターンマッチング
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text))
            if len(matches) >= 2:  # 少なくとも2つの大問がある
                for i, match in enumerate(matches):
                    start_pos = match.start()
                    end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
                    
                    section_text = text[start_pos:end_pos]
                    if len(section_text) > Settings.MIN_SECTION_CONTENT:
                        section = Section(
                            number=i + 1,
                            title=f"大問{i+1}",
                            content=section_text[:500],  # 冒頭のみ保存
                            question_count=self._count_questions_in_section(section_text)
                        )
                        sections.append(section)
                break
        
        # セクションが見つからない場合は全体を1つのセクションとする
        if not sections:
            sections.append(Section(
                number=1,
                title="全体",
                content=text[:500],
                question_count=self._count_questions_in_section(text)
            ))
        
        return sections
    
    def _count_questions_in_section(self, text: str) -> int:
        """セクション内の設問数をカウント"""
        # 設問パターン
        question_patterns = [
            r'問[一二三四五六七八九十０-９0-9]+',
            r'設問[０-９0-9]+',
            r'\([一二三四五六七八九十０-９0-9]+\)',
            r'[①②③④⑤⑥⑦⑧⑨⑩]',
        ]
        
        count = 0
        for pattern in question_patterns:
            matches = re.findall(pattern, text)
            if matches:
                count = max(count, len(matches))
        
        return max(count, 1)  # 最低1問はあるとする
    
    def _analyze_question_types(self, text: str) -> Dict[str, int]:
        """設問タイプを分析"""
        result = {
            '記述': 0,
            '選択': 0,
            '漢字・語句': 0,
            '抜き出し': 0,
        }
        
        # 各パターンでマッチングをカウント
        for q_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    result[q_type] += len(matches)
        
        # 最低限の推定（パターンに一致しない場合）
        if sum(result.values()) == 0:
            # テキストの長さから推定
            estimated_questions = max(5, len(text) // 2000)
            result['選択'] = estimated_questions // 2
            result['記述'] = estimated_questions // 3
            result['漢字・語句'] = estimated_questions // 6
        
        return result
    
    def _extract_sources(self, text: str) -> List[Source]:
        """出典を抽出"""
        sources = []
        
        # 出典パターン
        source_patterns = [
            r'『([^』]+)』[^（）]*（([^）]+)）',
            r'「([^」]+)」[^（）]*（([^）]+)）',
            r'『([^』]+)』\s*([^\s　]+(?:著|作))',
            r'([^\s　]+)\s*[著作]\s*『([^』]+)』',
            r'出典[：:]\s*([^。\n]+)',
            r'（([^）]+)の文による）',
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    # タイトルと著者を判別
                    if '『' in match[0] or '」' in match[0]:
                        title = match[0]
                        author = match[1] if len(match) > 1 else None
                    else:
                        author = match[0]
                        title = match[1] if len(match) > 1 else None
                elif isinstance(match, str):
                    title = match
                    author = None
                else:
                    continue
                
                # 重複チェック
                if not any(s.title == title and s.author == author for s in sources):
                    sources.append(Source(
                        title=title.strip() if title else None,
                        author=author.strip() if author else None
                    ))
        
        return sources[:5]  # 最大5つまで
    
    def _detect_theme(self, text: str) -> Optional[str]:
        """テーマを検出"""
        theme_keywords = {
            '人間関係・成長': ['友', '成長', '家族', '親子', '友達', '仲間'],
            '自然・環境': ['自然', '環境', '生態', '動物', '植物', '地球'],
            '社会・文化': ['社会', '文化', '伝統', '歴史', '日本', '世界'],
            '科学・技術': ['科学', '技術', '実験', '研究', 'コンピュータ', 'AI'],
            '哲学・思想': ['哲学', '思想', '考える', '意味', '価値', '真理'],
        }
        
        theme_scores = {}
        for theme, keywords in theme_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                theme_scores[theme] = score
        
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        
        return None
    
    def _detect_genre(self, text: str) -> Optional[str]:
        """ジャンルを検出"""
        genre_keywords = {
            '小説・物語': ['物語', '小説', 'だった。', 'のである。', '〜と思った'],
            '評論・論説': ['論じ', '考察', 'について', 'ところで', 'しかし'],
            '随筆・エッセイ': ['私は', '思う', '感じ', 'エッセイ', '随筆'],
            '詩・韻文': ['詩', '俳句', '短歌', '韻', '調べ'],
        }
        
        genre_scores = {}
        for genre, keywords in genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                genre_scores[genre] = score
        
        if genre_scores:
            return max(genre_scores, key=genre_scores.get)
        
        return '評論・論説'  # デフォルト