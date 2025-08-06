"""
最終版コンテンツ抽出モジュール
中学入試国語問題から著者名・作品名を確実に抽出する
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class FinalContentExtractor:
    """入試問題テキストから著者・作品情報を確実に抽出する最終版クラス"""
    
    def extract_all_content(self, text: str) -> Dict[str, Any]:
        """
        入試問題から全ての出典・設問情報を抽出
        
        Args:
            text: OCR結果の全テキスト
            
        Returns:
            完全な分析結果
        """
        # 結果を格納する辞書
        result = {
            'total_characters': len(text.replace(' ', '').replace('\n', '')),
            'sources': [],  # 全ての出典情報
            'sections': [],  # 各大問の詳細
            'total_questions': 0,
            'question_types': {
                '記述': 0,
                '選択': 0,
                '漢字・語句': 0,
                '抜き出し': 0
            }
        }
        
        # 1. 全ての出典を抽出（括弧付きの著者・作品名）
        sources = self._extract_all_sources(text)
        result['sources'] = sources
        
        # 2. 文章を出典で区切って大問に分割
        sections = self._divide_by_sources(text, sources)
        
        # 3. 各大問の設問を分析
        for i, section in enumerate(sections, 1):
            section_info = {
                'number': i,
                'source': section['source'],
                'start_pos': section['start'],
                'end_pos': section['end'],
                'characters': len(section['text'].replace(' ', '').replace('\n', '')),
                'questions': [],
                'genre': self._detect_genre(section['text']),
                'theme': self._detect_theme(section['text'])
            }
            
            # 設問を抽出
            questions = self._extract_questions_from_section(section['text'])
            section_info['questions'] = questions
            result['total_questions'] += len(questions)
            
            # 設問タイプを分類
            for q in questions:
                q_type = self._classify_question(q['text'])
                q['type'] = q_type
                if q_type in result['question_types']:
                    result['question_types'][q_type] += 1
            
            result['sections'].append(section_info)
        
        return result
    
    def _extract_all_sources(self, text: str) -> List[Dict[str, Any]]:
        """
        テキストから全ての出典情報を抽出
        
        Args:
            text: 全テキスト
            
        Returns:
            出典情報のリスト
        """
        sources = []
        
        # 主要なパターン：（著者名『作品名』より）
        pattern1 = re.compile(r'（([^『』（）]+)[『「]([^』」]+)[』」]より）')
        for match in pattern1.finditer(text):
            author = match.group(1).strip()
            work = match.group(2).strip()
            
            # 有効な著者名かチェック
            if self._is_valid_author(author) and len(work) > 1:
                sources.append({
                    'author': author,
                    'work': work,
                    'position': match.start(),
                    'full_text': match.group(0)
                })
        
        # パターン2：（『作品名』著者名より）
        pattern2 = re.compile(r'（[『「]([^』」]+)[』」]\s*([^（）]+)より）')
        for match in pattern2.finditer(text):
            work = match.group(1).strip()
            author = match.group(2).strip()
            
            if self._is_valid_author(author) and len(work) > 1:
                # 既に同じ位置で検出していないかチェック
                if not any(s['position'] == match.start() for s in sources):
                    sources.append({
                        'author': author,
                        'work': work,
                        'position': match.start(),
                        'full_text': match.group(0)
                    })
        
        # 位置でソート
        sources.sort(key=lambda x: x['position'])
        
        return sources
    
    def _is_valid_author(self, name: str) -> bool:
        """
        有効な著者名かチェック
        
        Args:
            name: 著者名候補
            
        Returns:
            有効な場合True
        """
        if not name or len(name) < 2 or len(name) > 20:
            return False
        
        # 除外パターン
        exclude_patterns = [
            r'^[0-9\-\s]+$',  # 数字のみ
            r'^――',  # 傍線記号
            r'^問[一二三四五六七八九十0-9]',  # 設問番号
            r'部[アイウエオ]',  # 傍線部記号
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, name):
                return False
        
        return True
    
    def _divide_by_sources(self, text: str, sources: List[Dict]) -> List[Dict]:
        """
        出典情報を基に文章を大問に分割
        
        Args:
            text: 全テキスト
            sources: 出典情報リスト
            
        Returns:
            各大問の情報リスト
        """
        sections = []
        
        if not sources:
            # 出典が見つからない場合は全体を1つの大問とする
            sections.append({
                'text': text,
                'source': None,
                'start': 0,
                'end': len(text)
            })
        else:
            # 各出典の前までを1つの大問とする
            for i, source in enumerate(sources):
                # この出典が属する文章の開始位置を決定
                if i == 0:
                    # 最初の出典の場合、テキストの最初から
                    start = 0
                else:
                    # 前の出典の直後から
                    start = sources[i-1]['position'] + len(sources[i-1]['full_text'])
                
                # 出典の位置まで
                end = source['position'] + len(source['full_text'])
                
                section_text = text[start:end]
                
                # 有効な文章かチェック（短すぎる場合は除外）
                if len(section_text) > 500:
                    sections.append({
                        'text': section_text,
                        'source': source,
                        'start': start,
                        'end': end
                    })
        
        return sections
    
    def _extract_questions_from_section(self, section_text: str) -> List[Dict[str, Any]]:
        """
        セクションから設問を抽出
        
        Args:
            section_text: セクションのテキスト
            
        Returns:
            設問のリスト
        """
        questions = []
        
        # 設問のパターン
        patterns = [
            (r'問([一二三四五六七八九十])', 'kanji_num'),
            (r'問([０-９0-9]+)', 'arabic_num'),
            (r'設問([０-９0-9]+)', 'setsumon'),
        ]
        
        all_matches = []
        for pattern_str, q_type in patterns:
            pattern = re.compile(pattern_str)
            for match in pattern.finditer(section_text):
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'number': match.group(1),
                    'type': q_type,
                    'full_match': match.group(0)
                })
        
        # 位置でソート
        all_matches.sort(key=lambda x: x['start'])
        
        # 各設問のテキストを抽出
        for i, match in enumerate(all_matches):
            # 次の設問または文末までをこの設問のテキストとする
            text_start = match['start']
            if i + 1 < len(all_matches):
                text_end = all_matches[i + 1]['start']
            else:
                text_end = len(section_text)
            
            question_text = section_text[text_start:text_end].strip()
            
            # 有効な設問かチェック
            if self._is_valid_question(question_text):
                questions.append({
                    'number': match['number'],
                    'text': question_text[:300],  # 最初の300文字
                    'full_text': question_text,
                    'position': text_start
                })
        
        return questions
    
    def _is_valid_question(self, text: str) -> bool:
        """
        有効な設問かチェック
        
        Args:
            text: 設問テキスト
            
        Returns:
            有効な場合True
        """
        if len(text) < 20:
            return False
        
        # 設問を示すキーワード
        keywords = [
            'なさい', '答え', '説明', '述べ', '選び',
            'について', 'とは', 'ですか', 'ありますが',
            'どのような', 'なぜ', 'どういうこと',
            '意味を', '理由を'
        ]
        
        # 最初の200文字に設問キーワードが含まれているか
        search_area = text[:200] if len(text) > 200 else text
        return any(keyword in search_area for keyword in keywords)
    
    def _classify_question(self, text: str) -> str:
        """
        設問のタイプを分類
        
        Args:
            text: 設問テキスト
            
        Returns:
            設問タイプ
        """
        # 漢字・語句問題
        if any(keyword in text for keyword in ['漢字', '語句', '慣用句', 'ことわざ', '語群']):
            return '漢字・語句'
        
        # 抜き出し問題
        if any(keyword in text for keyword in ['抜き出し', '書き抜き', 'そのまま抜き出']):
            return '抜き出し'
        
        # 選択問題（記号がある場合）
        if re.search(r'[ア-ン][。、．\s]', text) or '選び' in text:
            return '選択'
        
        # それ以外は記述問題
        return '記述'
    
    def _detect_genre(self, text: str) -> str:
        """
        文章のジャンルを判定（中学受験用）
        
        Args:
            text: テキスト
            
        Returns:
            ジャンル
        """
        # 会話文の数をカウント
        dialogue_count = text.count('「') + text.count('」')
        
        # 小説・物語の判定（会話文が多い）
        if dialogue_count > 20:
            return '小説・物語'
        
        # 論説文の判定（論理的な展開）
        elif any(keyword in text for keyword in ['である', 'のだ', '考察', '論じる', '主張', 'べきだ']):
            return '論説文'
        
        # 説明文の判定（客観的な説明）
        elif any(keyword in text for keyword in ['について説明', 'とは', '定義', '仕組み', 'つまり']):
            return '説明文'
        
        # それ以外は随筆（エッセイ）
        else:
            return '随筆'
    
    def _detect_theme(self, text: str) -> str:
        """
        文章のテーマを判定
        
        Args:
            text: テキスト
            
        Returns:
            テーマ
        """
        theme_keywords = {
            '人間関係・成長': ['友', '家族', '成長', '大人', '子ども', '親', '兄弟'],
            '社会・文化': ['社会', '文化', '歴史', '戦争', '平和', '日本', '世界'],
            '自然・環境': ['自然', '環境', '動物', '植物', '森', '海', '山'],
            '科学・技術': ['科学', '技術', '実験', '研究', 'データ'],
            '哲学・思想': ['考え', '思', '意味', '価値', '存在']
        }
        
        scores = {}
        for theme, keywords in theme_keywords.items():
            score = sum(text.count(keyword) for keyword in keywords)
            scores[theme] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return '不明'