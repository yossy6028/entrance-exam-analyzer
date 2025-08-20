"""
出題形式（選択・記述・抜き出し等）の高精度判定モジュール
日本の中学入試問題に特化した問題タイプ分析
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class QuestionInfo:
    """個別の設問情報を格納するデータクラス"""
    number: str  # 問題番号（問1、(1)、①など）
    type: str  # 選択式、記述式、抜き出し、漢字・語句など
    subtype: Optional[str] = None  # より詳細な分類
    char_limit: Optional[Dict[str, Any]] = None  # 字数制限
    choice_count: Optional[int] = None  # 選択肢数
    difficulty_indicators: List[str] = field(default_factory=list)  # 難易度を示唆する表現
    line_number: int = 0
    text: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'number': self.number,
            'type': self.type,
            'subtype': self.subtype,
            'char_limit': self.char_limit,
            'choice_count': self.choice_count,
            'difficulty_indicators': self.difficulty_indicators,
            'line_number': self.line_number,
            'confidence': self.confidence
        }


class EnhancedQuestionTypeAnalyzer:
    """高精度な出題形式判定クラス"""
    
    def __init__(self):
        """初期化：判定パターンとルールを定義"""
        
        # 問題番号パターン（優先順位順）
        self.question_number_patterns = [
            # 問1、問2形式（最も一般的）
            (re.compile(r'問\s*([0-9０-９]{1,2})'), 'standard'),
            (re.compile(r'問\s*([一二三四五六七八九十]{1,2})'), 'standard'),
            
            # 設問1、設問2形式
            (re.compile(r'設問\s*([0-9０-９]{1,2})'), 'standard'),
            
            # (1)、(2)形式（小問）
            (re.compile(r'[(（]\s*([0-9０-９]{1,2})\s*[)）]'), 'sub'),
            (re.compile(r'[(（]\s*([一二三四五六七八九十]{1,2})\s*[)）]'), 'sub'),
            
            # ①、②形式（小問）
            (re.compile(r'([①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳])'), 'circle'),
            
            # ア、イ、ウ形式（選択肢または小問）
            (re.compile(r'([アイウエオカキクケコサシスセソタチツテトナニヌネノ])(?=[．、。\s\)])'), 'kana'),
            
            # A、B、C形式
            (re.compile(r'([A-ZＡ-Ｚ])(?=[．、。\s\)])'), 'alpha'),
        ]
        
        # 選択式問題の判定パターン（高精度版）
        self.selection_patterns = [
            # 明確な選択指示
            (re.compile(r'次の.*?から.*?選び'), 0.95),
            (re.compile(r'次の.*?うち.*?選び'), 0.95),
            (re.compile(r'[1-5１-５]つ選び'), 0.95),
            (re.compile(r'選択肢.*?から'), 0.95),
            (re.compile(r'最も(?:適切|ふさわしい|適当|正しい)な.*?選び'), 0.95),
            (re.compile(r'正しい.*?選び'), 0.9),
            (re.compile(r'誤って.*?選び'), 0.9),
            (re.compile(r'該当する.*?選び'), 0.9),
            
            # 選択肢の存在を示すパターン
            (re.compile(r'ア\s*[．.]\s*.*?\s*イ\s*[．.]'), 0.85),
            (re.compile(r'[①②③④⑤].*?[①②③④⑤]'), 0.85),
            (re.compile(r'[1１]\s*[．.]\s*.*?\s*[2２]\s*[．.]'), 0.8),
            
            # その他の選択を示唆するパターン
            (re.compile(r'どれ(?:です)?か'), 0.7),
            (re.compile(r'次の中から'), 0.75),
            (re.compile(r'いずれか'), 0.7),
        ]
        
        # 記述式問題の判定パターン（高精度版）
        self.description_patterns = [
            # 字数指定のある記述
            (re.compile(r'([0-9０-９]{2,3})\s*字\s*(?:以内|程度|前後)で'), 0.95),
            (re.compile(r'([0-9０-９]{2,3})\s*文字\s*(?:以内|程度|前後)で'), 0.95),
            (re.compile(r'([0-9０-９]{2,3})\s*字\s*～\s*([0-9０-９]{2,3})\s*字'), 0.95),
            
            # 説明を求める記述
            (re.compile(r'説明し(?:なさい|てください|ましょう)'), 0.9),
            (re.compile(r'述べ(?:なさい|てください|ましょう)'), 0.9),
            (re.compile(r'答え(?:なさい|てください|ましょう)'), 0.85),
            (re.compile(r'書き(?:なさい|てください|ましょう)'), 0.85),
            
            # 理由や内容の説明
            (re.compile(r'理由を.*?説明'), 0.9),
            (re.compile(r'どのような.*?か.*?説明'), 0.9),
            (re.compile(r'なぜ.*?か.*?説明'), 0.9),
            (re.compile(r'どういうこと.*?か'), 0.85),
            
            # その他の記述指示
            (re.compile(r'あなたの(?:考え|意見)'), 0.85),
            (re.compile(r'自分の(?:考え|意見|言葉)'), 0.85),
            (re.compile(r'まとめ(?:なさい|てください)'), 0.85),
        ]
        
        # 抜き出し問題の判定パターン
        self.extraction_patterns = [
            # 明確な抜き出し指示
            (re.compile(r'抜き出し'), 0.95),
            (re.compile(r'そのまま.*?書き'), 0.9),
            (re.compile(r'文中から.*?(?:探し|見つけ)'), 0.9),
            (re.compile(r'本文中の.*?答え'), 0.9),
            
            # 字数指定のある抜き出し
            (re.compile(r'([0-9０-９]{1,2})\s*字で\s*抜き出し'), 0.95),
            (re.compile(r'([0-9０-９]{1,2})\s*文字で\s*抜き出し'), 0.95),
            
            # 文中の言葉を使う指示
            (re.compile(r'文中の.*?(?:言葉|表現|ことば).*?(?:使って|用いて)'), 0.85),
            (re.compile(r'本文の.*?(?:言葉|表現|ことば).*?(?:使って|用いて)'), 0.85),
            
            # その他の抜き出しを示唆
            (re.compile(r'該当する(?:部分|箇所|ところ)'), 0.8),
            (re.compile(r'どこ.*?書かれて'), 0.75),
        ]
        
        # 漢字・語句問題の判定パターン
        self.kanji_vocab_patterns = [
            # 漢字の読み書き
            (re.compile(r'漢字に(?:直し|し(?:なさい|てください))'), 0.95),
            (re.compile(r'ひらがなに(?:直し|し(?:なさい|てください))'), 0.95),
            (re.compile(r'漢字で(?:書き|答え)'), 0.95),
            (re.compile(r'読み(?:を|方を)?.*?(?:書き|答え)'), 0.95),
            (re.compile(r'送り仮名'), 0.9),
            
            # 語句の意味
            (re.compile(r'(?:同じ|同様の|似た).*?意味'), 0.9),
            (re.compile(r'(?:反対|逆)の.*?意味'), 0.9),
            (re.compile(r'類義語'), 0.95),
            (re.compile(r'対義語'), 0.95),
            (re.compile(r'同義語'), 0.95),
            
            # 慣用表現
            (re.compile(r'ことわざ'), 0.95),
            (re.compile(r'慣用句'), 0.95),
            (re.compile(r'四字熟語'), 0.95),
            (re.compile(r'故事成語'), 0.95),
            
            # 文法
            (re.compile(r'品詞'), 0.9),
            (re.compile(r'助詞'), 0.9),
            (re.compile(r'助動詞'), 0.9),
        ]
        
        # 字数制限の詳細パターン
        self.char_limit_detailed_patterns = [
            # 単一制限
            re.compile(r'([0-9０-９]{1,3})\s*字\s*(以内|程度|前後|ぴったり|ちょうど)'),
            re.compile(r'([0-9０-９]{1,3})\s*文字\s*(以内|程度|前後|ぴったり|ちょうど)'),
            
            # 範囲指定
            re.compile(r'([0-9０-９]{1,3})\s*字\s*～\s*([0-9０-９]{1,3})\s*字'),
            re.compile(r'([0-9０-９]{1,3})\s*文字\s*～\s*([0-9０-９]{1,3})\s*文字'),
            re.compile(r'([0-9０-９]{1,3})\s*字\s*から\s*([0-9０-９]{1,3})\s*字'),
            
            # 最低・最大指定
            re.compile(r'([0-9０-９]{1,3})\s*字\s*以上'),
            re.compile(r'([0-9０-９]{1,3})\s*字\s*以下'),
        ]
        
        # 選択肢数の検出パターン
        self.choice_detection_patterns = [
            # カタカナ選択肢
            (re.compile(r'ア.*?イ.*?ウ.*?エ.*?オ'), 5),
            (re.compile(r'ア.*?イ.*?ウ.*?エ'), 4),
            (re.compile(r'ア.*?イ.*?ウ'), 3),
            
            # 数字選択肢
            (re.compile(r'[1１].*?[2２].*?[3３].*?[4４].*?[5５]'), 5),
            (re.compile(r'[1１].*?[2２].*?[3３].*?[4４]'), 4),
            
            # 丸数字選択肢
            (re.compile(r'①.*?②.*?③.*?④.*?⑤'), 5),
            (re.compile(r'①.*?②.*?③.*?④'), 4),
            
            # 明示的な数の指定
            (re.compile(r'次の([2-8２-８])つから'), None),  # グループから数を取得
        ]
    
    def analyze_questions(self, text: str, sections: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        テキストから出題形式を詳細分析
        
        Args:
            text: 分析対象のテキスト
            sections: 大問セクション情報（オプション）
            
        Returns:
            問題分析結果の辞書
        """
        result = {
            'total_questions': 0,
            'question_types': defaultdict(int),
            'questions': [],
            'sections': [],
            'statistics': {}
        }
        
        # テキストを行に分割
        lines = text.split('\n')
        
        # 問題を検出
        questions = self._detect_all_questions(lines)
        
        # 各問題を分析
        for question in questions:
            q_info = self._analyze_single_question(question, lines)
            result['questions'].append(q_info)
            result['question_types'][q_info.type] += 1
            
            # サブタイプも集計
            if q_info.subtype:
                subtype_key = f"{q_info.type}_{q_info.subtype}"
                result['question_types'][subtype_key] += 1
        
        result['total_questions'] = len(questions)
        
        # 大問ごとの分析
        if sections:
            for section in sections:
                section_analysis = self._analyze_section_questions(section, questions)
                result['sections'].append(section_analysis)
        
        # 統計情報を計算
        result['statistics'] = self._calculate_statistics(result)
        
        return result
    
    def _detect_all_questions(self, lines: List[str]) -> List[Dict[str, Any]]:
        """全ての問題を検出"""
        questions = []
        current_question = None
        question_lines = []
        
        for i, line in enumerate(lines):
            # 問題番号を検出
            question_start = self._detect_question_start(line)
            
            if question_start:
                # 前の問題を保存
                if current_question:
                    current_question['text'] = '\n'.join(question_lines)
                    current_question['end_line'] = i - 1
                    questions.append(current_question)
                
                # 新しい問題を開始
                current_question = {
                    'number': question_start['number'],
                    'number_type': question_start['type'],
                    'start_line': i,
                    'raw_match': question_start['match']
                }
                question_lines = [line]
            elif current_question:
                # 現在の問題に行を追加
                question_lines.append(line)
                
                # 次の大問の開始を検出したら終了
                if self._is_section_start(line):
                    current_question['text'] = '\n'.join(question_lines[:-1])
                    current_question['end_line'] = i - 1
                    questions.append(current_question)
                    current_question = None
                    question_lines = []
        
        # 最後の問題を保存
        if current_question:
            current_question['text'] = '\n'.join(question_lines)
            current_question['end_line'] = len(lines) - 1
            questions.append(current_question)
        
        return questions
    
    def _detect_question_start(self, line: str) -> Optional[Dict[str, Any]]:
        """行から問題の開始を検出"""
        for pattern, q_type in self.question_number_patterns:
            match = pattern.search(line)
            if match:
                return {
                    'number': match.group(1) if match.groups() else match.group(0),
                    'type': q_type,
                    'match': match.group(0)
                }
        return None
    
    def _is_section_start(self, line: str) -> bool:
        """大問の開始かどうかを判定"""
        section_patterns = [
            r'^[【\[［][一二三四五六七八九十1-9１-９][】\]］]',
            r'^[一二三四五六七八九十1-9１-９][．、。\s]',
            r'^第[一二三四五六七八九十1-9１-９]問',
        ]
        
        for pattern in section_patterns:
            if re.match(pattern, line.strip()):
                return True
        return False
    
    def _analyze_single_question(self, question: Dict[str, Any], 
                                all_lines: List[str]) -> QuestionInfo:
        """個別の問題を詳細分析"""
        text = question['text']
        
        # 基本情報を設定
        q_info = QuestionInfo(
            number=question['number'],
            type='その他',
            line_number=question['start_line']
        )
        
        # 各パターンでタイプを判定（優先順位順）
        type_confidence = 0.0
        
        # 1. 漢字・語句問題の判定
        for pattern, confidence in self.kanji_vocab_patterns:
            if pattern.search(text):
                q_info.type = '漢字・語句'
                q_info.subtype = self._determine_kanji_subtype(text)
                type_confidence = max(type_confidence, confidence)
                break
        
        # 2. 抜き出し問題の判定
        if type_confidence < 0.9:
            for pattern, confidence in self.extraction_patterns:
                if pattern.search(text):
                    q_info.type = '抜き出し'
                    q_info.char_limit = self._extract_char_limit(text)
                    type_confidence = max(type_confidence, confidence)
                    break
        
        # 3. 記述式問題の判定
        if type_confidence < 0.9:
            for pattern, confidence in self.description_patterns:
                if pattern.search(text):
                    q_info.type = '記述式'
                    q_info.char_limit = self._extract_char_limit(text)
                    q_info.subtype = self._determine_description_subtype(text)
                    type_confidence = max(type_confidence, confidence)
                    break
        
        # 4. 選択式問題の判定
        if type_confidence < 0.9:
            for pattern, confidence in self.selection_patterns:
                if pattern.search(text):
                    q_info.type = '選択式'
                    q_info.choice_count = self._count_choices(text)
                    q_info.subtype = self._determine_selection_subtype(text)
                    type_confidence = max(type_confidence, confidence)
                    break
        
        # 5. コンテキストから推測
        if q_info.type == 'その他':
            q_info.type = self._infer_from_context(question, all_lines)
            type_confidence = 0.5
        
        q_info.confidence = type_confidence
        q_info.text = text[:200]  # 最初の200文字を保存
        
        # 難易度指標を抽出
        q_info.difficulty_indicators = self._extract_difficulty_indicators(text)
        
        return q_info
    
    def _extract_char_limit(self, text: str) -> Optional[Dict[str, Any]]:
        """字数制限を抽出"""
        for pattern in self.char_limit_detailed_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                
                if '～' in pattern.pattern or 'から' in pattern.pattern:
                    # 範囲指定
                    return {
                        'type': 'range',
                        'min': int(self._normalize_number(groups[0])),
                        'max': int(self._normalize_number(groups[1]))
                    }
                elif '以上' in match.group(0):
                    return {
                        'type': 'minimum',
                        'min': int(self._normalize_number(groups[0]))
                    }
                elif '以下' in match.group(0):
                    return {
                        'type': 'maximum',
                        'max': int(self._normalize_number(groups[0]))
                    }
                else:
                    # 単一制限
                    limit = int(self._normalize_number(groups[0]))
                    condition = groups[1] if len(groups) > 1 else '以内'
                    return {
                        'type': 'single',
                        'limit': limit,
                        'condition': condition
                    }
        
        return None
    
    def _count_choices(self, text: str) -> Optional[int]:
        """選択肢数をカウント"""
        for pattern, count in self.choice_detection_patterns:
            match = pattern.search(text)
            if match:
                if count is None and match.groups():
                    # グループから数を取得
                    return int(self._normalize_number(match.group(1)))
                else:
                    return count
        
        # 選択肢を個別にカウント
        kata_choices = len(re.findall(r'[アイウエオカキクケコ]\s*[．.]', text))
        if kata_choices >= 2:
            return kata_choices
        
        num_choices = len(re.findall(r'[1-5１-５]\s*[．.]', text))
        if num_choices >= 2:
            return num_choices
        
        circle_choices = len(re.findall(r'[①②③④⑤⑥⑦⑧]', text))
        if circle_choices >= 2:
            return circle_choices
        
        return None
    
    def _determine_kanji_subtype(self, text: str) -> Optional[str]:
        """漢字・語句問題のサブタイプを判定"""
        if '読み' in text:
            return '読み'
        elif '書き' in text or '漢字に' in text:
            return '書き'
        elif '類義語' in text or '同義語' in text:
            return '類義語'
        elif '対義語' in text or '反対' in text:
            return '対義語'
        elif 'ことわざ' in text:
            return 'ことわざ'
        elif '慣用句' in text:
            return '慣用句'
        elif '四字熟語' in text:
            return '四字熟語'
        elif '品詞' in text:
            return '文法'
        return None
    
    def _determine_description_subtype(self, text: str) -> Optional[str]:
        """記述式問題のサブタイプを判定"""
        if '理由' in text or 'なぜ' in text:
            return '理由説明'
        elif 'どのような' in text or 'どういう' in text:
            return '内容説明'
        elif '気持ち' in text or '心情' in text:
            return '心情説明'
        elif 'あなたの考え' in text or '自分の意見' in text:
            return '意見記述'
        elif 'まとめ' in text or '要約' in text:
            return '要約'
        return None
    
    def _determine_selection_subtype(self, text: str) -> Optional[str]:
        """選択式問題のサブタイプを判定"""
        if '正しい' in text:
            return '正誤'
        elif '誤って' in text or '間違' in text:
            return '誤り選択'
        elif '最も' in text:
            return '最適選択'
        elif '該当' in text or '当てはまる' in text:
            return '該当選択'
        return None
    
    def _infer_from_context(self, question: Dict[str, Any], 
                           all_lines: List[str]) -> str:
        """コンテキストから問題タイプを推測"""
        # 前後の問題を確認
        start_line = question['start_line']
        
        # 直前の行を確認
        if start_line > 0:
            prev_line = all_lines[start_line - 1]
            # 選択肢が直前にある場合
            if re.search(r'[アイウエオ]\s*[．.]', prev_line):
                return '選択式'
        
        # 問題文の特徴から推測
        text = question['text']
        
        # 疑問詞で終わる場合
        if re.search(r'(?:何|どれ|どの|どちら|いつ|どこ).*?(?:か|ですか)[。．\s]*$', text):
            # 選択肢の兆候があれば選択式
            if re.search(r'次の|以下の|上の', text):
                return '選択式'
            # それ以外は記述式の可能性
            return '記述式'
        
        return 'その他'
    
    def _extract_difficulty_indicators(self, text: str) -> List[str]:
        """難易度を示唆する表現を抽出"""
        indicators = []
        
        difficulty_patterns = [
            '必ず', '全て', 'すべて', '詳しく', '具体的に',
            '簡潔に', '要約して', '自分の言葉で', '根拠を示して'
        ]
        
        for pattern in difficulty_patterns:
            if pattern in text:
                indicators.append(pattern)
        
        return indicators
    
    def _normalize_number(self, num_str: str) -> str:
        """漢数字・全角数字を半角数字に変換"""
        # 漢数字変換表
        kanji_map = {
            '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
            '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
            '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
            '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20',
            '三十': '30', '四十': '40', '五十': '50', '六十': '60',
            '七十': '70', '八十': '80', '九十': '90', '百': '100',
            '二百': '200', '三百': '300', '四百': '400', '五百': '500'
        }
        
        # 漢数字の変換
        if num_str in kanji_map:
            return kanji_map[num_str]
        
        # 全角数字を半角に変換
        num_str = num_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        return num_str
    
    def _analyze_section_questions(self, section: Dict, 
                                  all_questions: List[Dict]) -> Dict[str, Any]:
        """大問内の問題を分析"""
        section_analysis = {
            'section_number': section.get('number', ''),
            'question_count': 0,
            'question_types': defaultdict(int),
            'questions': []
        }
        
        # セクション内の問題を特定
        if 'start_line' in section and 'end_line' in section:
            for q in all_questions:
                if section['start_line'] <= q['start_line'] <= section['end_line']:
                    section_analysis['question_count'] += 1
                    # 問題タイプは既に分析済みのものを使用
        
        return section_analysis
    
    def _calculate_statistics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """統計情報を計算"""
        stats = {
            'total_questions': result['total_questions'],
            'type_distribution': {},
            'average_char_limit': None,
            'average_choice_count': None,
            'has_opinion_questions': False,
            'complexity_score': 0
        }
        
        # タイプ別の割合を計算
        if result['total_questions'] > 0:
            for q_type, count in result['question_types'].items():
                if '_' not in q_type:  # サブタイプは除外
                    percentage = (count / result['total_questions']) * 100
                    stats['type_distribution'][q_type] = {
                        'count': count,
                        'percentage': round(percentage, 1)
                    }
        
        # 記述式の平均字数制限
        char_limits = []
        choice_counts = []
        
        for q in result['questions']:
            if q.char_limit:
                if q.char_limit.get('limit'):
                    char_limits.append(q.char_limit['limit'])
                elif q.char_limit.get('max'):
                    char_limits.append(q.char_limit['max'])
            
            if q.choice_count:
                choice_counts.append(q.choice_count)
            
            # 意見記述問題の有無
            if q.subtype == '意見記述':
                stats['has_opinion_questions'] = True
        
        if char_limits:
            stats['average_char_limit'] = round(sum(char_limits) / len(char_limits))
        
        if choice_counts:
            stats['average_choice_count'] = round(sum(choice_counts) / len(choice_counts), 1)
        
        # 複雑度スコアを計算（記述式の割合と字数制限から）
        description_ratio = stats['type_distribution'].get('記述式', {}).get('percentage', 0)
        avg_char = stats['average_char_limit'] or 0
        
        stats['complexity_score'] = round(
            (description_ratio * 0.5) + (min(avg_char, 200) / 200 * 50),
            1
        )
        
        return stats