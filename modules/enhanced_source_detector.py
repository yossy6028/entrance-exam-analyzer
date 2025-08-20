"""
出典情報（著者名・タイトル）の高精度抽出モジュール
日本の中学入試問題に特化した出典検出ロジック
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SourceInfo:
    """出典情報を格納するデータクラス"""
    author: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[str] = None
    source_type: str = "unknown"  # 小説、評論、随筆、詩歌など
    confidence: float = 0.0
    line_number: int = 0
    context: str = ""
    
    def is_complete(self) -> bool:
        """著者名とタイトルの両方が揃っているか"""
        return bool(self.author and self.title)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'author': self.author,
            'title': self.title,
            'publisher': self.publisher,
            'year': self.year,
            'source_type': self.source_type,
            'confidence': self.confidence,
            'line_number': self.line_number,
            'context': self.context
        }


class EnhancedSourceDetector:
    """高精度な出典情報検出クラス"""
    
    def __init__(self):
        """初期化：パターンとルールを定義"""
        
        # より詳細な出典パターン（優先順位順）
        self.source_patterns = [
            # 最も一般的なパターン：（著者名『作品名』出版社、より）
            (re.compile(r'[（(]([^『』（）]{2,20})[『「]([^』」]+)[』」]([^（）]*?)[）)]'), 
             {'author': 0, 'title': 1, 'extra': 2}, 0.95),
            
            # 著者名「作品名」（出版社）パターン
            (re.compile(r'([^「」\s]{2,15})[「『]([^」』]+)[」』]\s*[（(]([^）)]+)[）)]'),
             {'author': 0, 'title': 1, 'publisher': 2}, 0.9),
            
            # （『作品名』著者名）パターン
            (re.compile(r'[（(][『「]([^』」]+)[』」]\s+([^（）]{2,20})[）)]'),
             {'title': 0, 'author': 1}, 0.9),
            
            # 出典：著者名『作品名』パターン
            (re.compile(r'出典[:：]\s*([^『「]{2,15})[『「]([^』」]+)[』」]'),
             {'author': 0, 'title': 1}, 0.95),
            
            # 「作品名」作者名 パターン
            (re.compile(r'[「『]([^」』]+)[」』]\s*([^（）\s]{2,15})(?:著|作|より)'),
             {'title': 0, 'author': 1}, 0.85),
            
            # より詳細な括弧内パターン
            (re.compile(r'[（(]([^『「]{2,15})\s*[『「]([^』」]+)[』」].*?([^）)]*出版[^）)]*)[）)]'),
             {'author': 0, 'title': 1, 'publisher': 2}, 0.95),
            
            # 文末の出典表記
            (re.compile(r'(?:より|から|出典)\s*[（(]?([^『「]{2,15})[『「]([^』」]+)[』」][）)]?$'),
             {'author': 0, 'title': 1}, 0.85),
        ]
        
        # 著者名のみのパターン
        self.author_only_patterns = [
            (re.compile(r'文[・･]\s*([^（）\s]{2,15})'), 0.7),
            (re.compile(r'作[・･]\s*([^（）\s]{2,15})'), 0.7),
            (re.compile(r'著者[・･：:]\s*([^（）\s]{2,15})'), 0.8),
            (re.compile(r'([^（）\s]{2,15})\s*著'), 0.75),
            (re.compile(r'([^（）\s]{2,15})\s*作'), 0.7),
        ]
        
        # タイトルのみのパターン
        self.title_only_patterns = [
            (re.compile(r'[『「]([^』」]+)[』」](?!.*[著作])'), 0.6),
            (re.compile(r'作品[・･：:]\s*[『「]([^』」]+)[』」]'), 0.8),
        ]
        
        # 出版社・出版年パターン
        self.publisher_patterns = [
            re.compile(r'([^（）]+(?:出版|書房|書店|社|堂|館))'),
            re.compile(r'([^（）]+(?:文庫|新書|選書))'),
        ]
        
        self.year_patterns = [
            re.compile(r'([12][0-9]{3}|平成[0-9]{1,2}|令和[0-9]{1,2}|昭和[0-9]{1,2})年'),
        ]
        
        # ジャンル判定キーワード
        self.genre_keywords = {
            '小説・物語': ['小説', '物語', 'ものがたり', '童話', 'ファンタジー', 'ミステリー'],
            '評論・論説': ['評論', '論説', '論文', '論考', '批評', '解説'],
            '随筆・エッセイ': ['随筆', 'エッセイ', 'エッセー', '随想', '紀行', '日記'],
            '詩歌': ['詩', '短歌', '俳句', '詩集', '歌集', '句集'],
            '伝記・ノンフィクション': ['伝記', 'ノンフィクション', 'ルポ', 'ドキュメント', '記録'],
            '古典': ['古文', '漢文', '古典', '源氏物語', '枕草子', '徒然草']
        }
        
        # 除外すべき偽陽性パターン
        self.false_positive_patterns = [
            re.compile(r'問[0-9一二三四五六七八九十]+'),
            re.compile(r'設問[0-9]+'),
            re.compile(r'[①②③④⑤⑥⑦⑧⑨⑩]'),
            re.compile(r'^[ぁ-ん]{1,2}$'),  # ひらがな1-2文字のみ
            re.compile(r'^[ァ-ヴ]{1,3}$'),  # カタカナ1-3文字のみ
        ]
    
    def extract_sources(self, text: str, sections: Optional[List[Dict]] = None) -> List[SourceInfo]:
        """
        テキストから出典情報を抽出
        
        Args:
            text: 分析対象のテキスト
            sections: 大問セクション情報（オプション）
            
        Returns:
            出典情報のリスト
        """
        sources = []
        
        # テキストを行に分割
        lines = text.split('\n')
        
        # 1. 文末付近から出典を探す（最も信頼性が高い）
        end_sources = self._extract_from_text_end(lines)
        sources.extend(end_sources)
        
        # 2. 大問ごとに出典を探す
        if sections:
            for section in sections:
                section_sources = self._extract_from_section(section)
                sources.extend(section_sources)
        
        # 3. 全文から出典パターンを探す
        full_text_sources = self._extract_from_full_text(text, lines)
        sources.extend(full_text_sources)
        
        # 4. 重複を除去し、信頼度順にソート
        unique_sources = self._merge_and_deduplicate(sources)
        
        # 5. 不完全な情報を補完
        completed_sources = self._complete_partial_sources(unique_sources, text)
        
        return completed_sources
    
    def _extract_from_text_end(self, lines: List[str]) -> List[SourceInfo]:
        """文末付近から出典を抽出（最も信頼性が高い）"""
        sources = []
        
        # 文末から100行程度を重点的に検索
        end_lines = lines[-100:] if len(lines) > 100 else lines
        
        for i, line in enumerate(end_lines):
            line_num = len(lines) - len(end_lines) + i + 1
            
            # 各パターンで検索
            for pattern, mapping, confidence in self.source_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    source = self._create_source_from_match(
                        match, mapping, confidence, line_num, line
                    )
                    if source and self._is_valid_source(source):
                        sources.append(source)
        
        return sources
    
    def _extract_from_section(self, section: Dict) -> List[SourceInfo]:
        """大問セクションから出典を抽出"""
        sources = []
        
        if 'text' not in section:
            return sources
        
        section_text = section['text']
        section_lines = section_text.split('\n')
        
        # セクションの最初と最後を重点的に検索
        for i, line in enumerate(section_lines[:10] + section_lines[-10:]):
            for pattern, mapping, confidence in self.source_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    source = self._create_source_from_match(
                        match, mapping, confidence * 0.9,  # セクション内は少し信頼度を下げる
                        section.get('start_line', 0) + i, line
                    )
                    if source and self._is_valid_source(source):
                        source.source_type = self._determine_genre(section_text)
                        sources.append(source)
        
        return sources
    
    def _extract_from_full_text(self, text: str, lines: List[str]) -> List[SourceInfo]:
        """全文から出典パターンを抽出"""
        sources = []
        
        for i, line in enumerate(lines):
            # 著者名のみのパターン
            for pattern, confidence in self.author_only_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    author = match.group(1).strip()
                    if self._is_valid_author(author):
                        source = SourceInfo(
                            author=author,
                            confidence=confidence,
                            line_number=i + 1,
                            context=line
                        )
                        sources.append(source)
            
            # タイトルのみのパターン
            for pattern, confidence in self.title_only_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    title = match.group(1).strip()
                    if self._is_valid_title(title):
                        source = SourceInfo(
                            title=title,
                            confidence=confidence,
                            line_number=i + 1,
                            context=line
                        )
                        sources.append(source)
        
        return sources
    
    def _create_source_from_match(self, match: re.Match, mapping: Dict[str, int], 
                                 confidence: float, line_number: int, 
                                 context: str) -> Optional[SourceInfo]:
        """正規表現マッチから出典情報を作成"""
        source = SourceInfo(
            confidence=confidence,
            line_number=line_number,
            context=context
        )
        
        groups = match.groups()
        
        for field, index in mapping.items():
            if index < len(groups) and groups[index]:
                value = groups[index].strip()
                
                if field == 'author':
                    source.author = self._clean_author_name(value)
                elif field == 'title':
                    source.title = self._clean_title(value)
                elif field == 'publisher':
                    source.publisher = self._extract_publisher(value)
                elif field == 'extra':
                    # 追加情報から出版社や年を抽出
                    source.publisher = self._extract_publisher(value)
                    source.year = self._extract_year(value)
        
        return source
    
    def _clean_author_name(self, name: str) -> str:
        """著者名をクリーンアップ"""
        # 不要な記号を削除
        name = re.sub(r'[「」『』（）()【】\[\]]', '', name)
        # 「著」「作」などの接尾辞を削除
        name = re.sub(r'(著|作|訳|編|監修)$', '', name)
        # 前後の空白を削除
        name = name.strip()
        
        return name
    
    def _clean_title(self, title: str) -> str:
        """タイトルをクリーンアップ"""
        # 「より」「から」などを削除
        title = re.sub(r'(より|から|出典)$', '', title)
        title = title.strip()
        
        return title
    
    def _extract_publisher(self, text: str) -> Optional[str]:
        """出版社を抽出"""
        for pattern in self.publisher_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_year(self, text: str) -> Optional[str]:
        """出版年を抽出"""
        for pattern in self.year_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return None
    
    def _is_valid_source(self, source: SourceInfo) -> bool:
        """有効な出典情報かチェック"""
        # 少なくとも著者かタイトルのどちらかは必要
        if not (source.author or source.title):
            return False
        
        # 著者名の妥当性チェック
        if source.author:
            if not self._is_valid_author(source.author):
                return False
        
        # タイトルの妥当性チェック
        if source.title:
            if not self._is_valid_title(source.title):
                return False
        
        return True
    
    def _is_valid_author(self, author: str) -> bool:
        """著者名の妥当性をチェック"""
        if not author or len(author) < 2:
            return False
        
        # 偽陽性パターンのチェック
        for pattern in self.false_positive_patterns:
            if pattern.match(author):
                return False
        
        # 数字のみ、記号のみは除外
        if re.match(r'^[0-9\-\s]+$', author):
            return False
        
        # 長すぎる名前は除外（20文字以上）
        if len(author) > 20:
            return False
        
        return True
    
    def _is_valid_title(self, title: str) -> bool:
        """タイトルの妥当性をチェック"""
        if not title or len(title) < 2:
            return False
        
        # 偽陽性パターンのチェック
        for pattern in self.false_positive_patterns:
            if pattern.match(title):
                return False
        
        # ページ番号っぽいものは除外
        if re.match(r'^[0-9\-\s]+$', title):
            return False
        
        return True
    
    def _merge_and_deduplicate(self, sources: List[SourceInfo]) -> List[SourceInfo]:
        """重複を除去し、情報をマージ"""
        merged = {}
        
        for source in sources:
            # キーを作成（著者名とタイトルの組み合わせ）
            key = (source.author or "", source.title or "")
            
            if key in merged:
                # 既存のものより信頼度が高い場合は更新
                if source.confidence > merged[key].confidence:
                    # 既存の情報で補完
                    if not source.author and merged[key].author:
                        source.author = merged[key].author
                    if not source.title and merged[key].title:
                        source.title = merged[key].title
                    if not source.publisher and merged[key].publisher:
                        source.publisher = merged[key].publisher
                    merged[key] = source
                else:
                    # 既存のものに情報を補完
                    if source.author and not merged[key].author:
                        merged[key].author = source.author
                    if source.title and not merged[key].title:
                        merged[key].title = source.title
                    if source.publisher and not merged[key].publisher:
                        merged[key].publisher = source.publisher
            else:
                merged[key] = source
        
        # 信頼度順にソート
        return sorted(merged.values(), key=lambda x: x.confidence, reverse=True)
    
    def _complete_partial_sources(self, sources: List[SourceInfo], text: str) -> List[SourceInfo]:
        """不完全な出典情報を補完"""
        # 著者名のみの情報とタイトルのみの情報をマッチング
        authors_only = [s for s in sources if s.author and not s.title]
        titles_only = [s for s in sources if s.title and not s.author]
        
        completed = []
        used_title_indices = set()  # インデックスで管理
        
        for author_source in authors_only:
            best_match = None
            best_match_index = -1
            best_distance = float('inf')
            
            for i, title_source in enumerate(titles_only):
                if i in used_title_indices:
                    continue
                
                # 行番号の距離を計算
                distance = abs(author_source.line_number - title_source.line_number)
                
                # 近い位置にある場合はマッチング
                if distance < 10 and distance < best_distance:
                    best_match = title_source
                    best_match_index = i
                    best_distance = distance
            
            if best_match:
                # 情報を統合
                combined = SourceInfo(
                    author=author_source.author,
                    title=best_match.title,
                    publisher=author_source.publisher or best_match.publisher,
                    year=author_source.year or best_match.year,
                    confidence=min(author_source.confidence, best_match.confidence) * 0.9,
                    line_number=author_source.line_number,
                    context=author_source.context
                )
                combined.source_type = self._determine_genre(text)
                completed.append(combined)
                used_title_indices.add(best_match_index)
            else:
                author_source.source_type = self._determine_genre(text)
                completed.append(author_source)
        
        # 使用されなかったタイトルも追加
        for i, title_source in enumerate(titles_only):
            if i not in used_title_indices:
                title_source.source_type = self._determine_genre(text)
                completed.append(title_source)
        
        # 完全な情報を持つソースも追加
        for source in sources:
            if source.is_complete():
                source.source_type = self._determine_genre(text)
                completed.append(source)
        
        return completed
    
    def _determine_genre(self, text: str) -> str:
        """テキストからジャンルを判定"""
        text_lower = text.lower()
        
        genre_scores = {}
        for genre, keywords in self.genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                genre_scores[genre] = score
        
        if genre_scores:
            return max(genre_scores, key=genre_scores.get)
        
        return "不明"