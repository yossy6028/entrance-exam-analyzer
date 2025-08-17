"""
問題数・問題種別の詳細分析モジュール
入試問題の設問パターンを認識し、問題種別ごとに分類・集計
"""
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class QuestionAnalyzer:
    """入試問題の詳細分析クラス"""
    
    def __init__(self):
        # 大問パターン（算用数字・漢数字・記号）
        self.section_patterns = [
            r'[【\[［]([一二三四五六七八九十]+)[】\]］]',  # 【一】【二】形式
            r'[【\[［]([1-9１-９][0-9０-９]*)[】\]］]',  # 【1】【2】形式
            r'^([一二三四五六七八九十]+)[\.、。\s]',  # 一、二、形式
            r'^([1-9１-９][0-9０-９]*)[\.、。\s]',  # 1、2、形式
            r'■\s*([一二三四五六七八九十]+)',  # ■ 一 形式
            r'■\s*([1-9１-９])',  # ■ 1 形式
        ]
        
        # 小問パターン
        self.question_patterns = [
            # 問1、問2形式
            r'問([1-9１-９][0-9０-９]*)',
            r'問([一二三四五六七八九十]+)',
            # (1)、(2)形式
            r'[(（]([1-9１-９][0-9０-９]*)[)）](?!.*ページ)',
            r'[(（]([一二三四五六七八九十]+)[)）]',
            # ①、②形式
            r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]',
            # ア、イ、ウ形式
            r'[アイウエオカキクケコ](?=[\.、。\s])',
        ]
        
        # 問題種別パターン
        self.question_types = {
            '選択式': [
                r'次の.*から.*選び',
                r'次の.*うち.*選び',
                r'ア～[アイウエオ]から.*選び',
                r'[1-4１-４]つ選び',
                r'最も(適切|ふさわしい|適当)な.*選び',
                r'正しい.*選び',
                r'誤って.*選び',
                r'選択肢.*から',
                r'次の中から',
            ],
            '記述式': [
                r'[0-9０-９]{2,3}字(以内|程度|前後)で',
                r'[0-9０-９]{2,3}文字(以内|程度|前後)で',
                r'説明し(なさい|てください)',
                r'述べ(なさい|てください)',
                r'書き(なさい|てください)',
                r'答え(なさい|てください)',
                r'理由を.*説明',
                r'どのような.*か.*説明',
                r'なぜ.*か.*説明',
            ],
            '抜き出し': [
                r'抜き出し',
                r'そのまま.*書き',
                r'文中から.*探し',
                r'本文中の.*を答え',
                r'[0-9０-９]{1,2}字で抜き出し',
                r'[0-9０-９]{1,2}文字で抜き出し',
                r'文中の言葉を(使って|用いて)',
            ],
            '漢字・語句': [
                r'漢字に直し',
                r'ひらがなに直し',
                r'漢字で書き',
                r'読みを.*書き',
                r'送り仮名',
                r'同じ意味',
                r'反対の意味',
                r'類義語',
                r'対義語',
                r'ことわざ',
                r'慣用句',
                r'四字熟語',
            ],
        }
        
        # 字数制限パターン
        self.char_limit_patterns = [
            r'([0-9０-９]{2,3})\s*字\s*(以内|程度|前後)',
            r'([0-9０-９]{2,3})\s*文字\s*(以内|程度|前後)',
            r'([0-9０-９]{2,3})\s*字\s*～\s*([0-9０-９]{2,3})\s*字',
        ]
        
        # 選択肢数パターン
        self.choice_count_patterns = [
            r'ア\s*～\s*([アイウエオカキクケコ])',  # ア～エ形式
            r'[1１]\s*～\s*([4-8４-８])',  # 1～4形式
            r'次の([2-8２-８])つから',  # 次の4つから形式
        ]
    
    def analyze_questions(self, text: str, source_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        問題文から設問を詳細分析
        
        Args:
            text: 問題文テキスト
            source_info: 出典情報（大問区切りの参考用）
            
        Returns:
            問題分析結果の辞書
        """
        result = {
            'sections': [],  # 大問別情報
            'total_questions': 0,
            'question_types': defaultdict(int),
            'question_details': [],
            'char_limits': [],
            'choice_counts': [],
        }
        
        # テキストを行に分割
        lines = text.split('\n')
        
        # 大問を検出
        sections = self._detect_sections(lines, source_info)
        
        # 各大問を分析
        for section in sections:
            section_analysis = self._analyze_section(section)
            result['sections'].append(section_analysis)
            
            # 全体集計に追加
            result['total_questions'] += section_analysis['question_count']
            for q_type, count in section_analysis['question_types'].items():
                result['question_types'][q_type] += count
            result['question_details'].extend(section_analysis['questions'])
        
        # 統計情報を追加
        result['statistics'] = self._calculate_statistics(result)
        
        return result
    
    def _detect_sections(self, lines: List[str], source_info: Optional[Dict]) -> List[Dict]:
        """大問を検出して区切る"""
        sections = []
        current_section = None
        current_lines = []
        
        for i, line in enumerate(lines):
            # 大問の開始を検出
            section_match = None
            for pattern in self.section_patterns:
                match = re.search(pattern, line)
                if match:
                    section_match = match
                    break
            
            if section_match:
                # 前のセクションを保存
                if current_section:
                    current_section['lines'] = current_lines
                    sections.append(current_section)
                
                # 新しいセクション開始
                section_num = section_match.group(1)
                current_section = {
                    'section_number': self._normalize_number(section_num),
                    'start_line': i,
                    'title': line.strip(),
                    'source': None
                }
                current_lines = []
                
                # 出典情報があれば関連付け
                if source_info and source_info.get('found_sources'):
                    # 近い位置の出典を探す
                    for source in source_info['found_sources']:
                        # 簡易的な位置マッチング
                        if abs(i - lines.index(source.get('full_match', ''))) < 10:
                            current_section['source'] = source
                            break
            else:
                current_lines.append(line)
        
        # 最後のセクションを保存
        if current_section:
            current_section['lines'] = current_lines
            sections.append(current_section)
        
        # セクションが見つからない場合は全体を1つのセクションとする
        if not sections:
            sections = [{
                'section_number': 1,
                'start_line': 0,
                'title': '全体',
                'lines': lines,
                'source': source_info.get('found_sources', [{}])[0] if source_info else None
            }]
        
        return sections
    
    def _analyze_section(self, section: Dict) -> Dict[str, Any]:
        """大問を詳細分析"""
        analysis = {
            'section_number': section['section_number'],
            'title': section['title'],
            'source': section.get('source'),
            'question_count': 0,
            'question_types': defaultdict(int),
            'questions': [],
            'text_length': sum(len(line) for line in section['lines'])
        }
        
        # 小問を検出
        questions = self._detect_questions(section['lines'])
        analysis['question_count'] = len(questions)
        
        # 各小問を分析
        for q in questions:
            q_analysis = self._analyze_question(q)
            analysis['questions'].append(q_analysis)
            analysis['question_types'][q_analysis['type']] += 1
        
        # ジャンル判定（出典情報から）
        if section.get('source'):
            analysis['genre'] = self._determine_genre(section['source'])
        
        return analysis
    
    def _detect_questions(self, lines: List[str]) -> List[Dict]:
        """小問を検出"""
        questions = []
        current_question = None
        question_lines = []
        
        for i, line in enumerate(lines):
            # 小問の開始を検出
            question_match = None
            for pattern in self.question_patterns:
                match = re.search(pattern, line)
                if match:
                    question_match = match
                    break
            
            if question_match:
                # 前の問題を保存
                if current_question:
                    current_question['text'] = '\n'.join(question_lines)
                    questions.append(current_question)
                
                # 新しい問題開始
                if question_match.groups():
                    q_num = question_match.group(1) if question_match.groups() else str(len(questions) + 1)
                else:
                    # 丸数字などグループがない場合
                    q_num = str(len(questions) + 1)
                    
                current_question = {
                    'number': self._normalize_number(q_num),
                    'line_number': i,
                    'raw_match': question_match.group(0)
                }
                question_lines = [line]
            elif current_question:
                question_lines.append(line)
        
        # 最後の問題を保存
        if current_question:
            current_question['text'] = '\n'.join(question_lines)
            questions.append(current_question)
        
        return questions
    
    def _analyze_question(self, question: Dict) -> Dict[str, Any]:
        """個別の問題を分析"""
        text = question['text']
        
        analysis = {
            'number': question['number'],
            'type': 'その他',
            'char_limit': None,
            'choice_count': None,
            'keywords': []
        }
        
        # 問題種別を判定
        for q_type, patterns in self.question_types.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    analysis['type'] = q_type
                    break
            if analysis['type'] != 'その他':
                break
        
        # 字数制限を検出（記述式の場合）
        if analysis['type'] == '記述式':
            for pattern in self.char_limit_patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) == 2 and match.group(2):
                        # 範囲指定の場合
                        analysis['char_limit'] = {
                            'min': int(self._normalize_number(match.group(1))),
                            'max': int(self._normalize_number(match.group(2)))
                        }
                    else:
                        # 単一制限の場合
                        limit = int(self._normalize_number(match.group(1)))
                        condition = match.group(2) if len(match.groups()) > 1 else '以内'
                        analysis['char_limit'] = {
                            'limit': limit,
                            'condition': condition
                        }
                    break
        
        # 選択肢数を検出（選択式の場合）
        if analysis['type'] == '選択式':
            for pattern in self.choice_count_patterns:
                match = re.search(pattern, text)
                if match:
                    last_choice = match.group(1)
                    # 選択肢数を計算
                    if last_choice in 'アイウエオカキクケコ':
                        analysis['choice_count'] = 'アイウエオカキクケコ'.index(last_choice) + 1
                    else:
                        analysis['choice_count'] = int(self._normalize_number(last_choice))
                    break
        
        # キーワード抽出
        analysis['keywords'] = self._extract_keywords(text)
        
        return analysis
    
    def _normalize_number(self, num_str: str) -> int:
        """漢数字・全角数字を半角数字に変換"""
        # 漢数字変換表
        kanji_to_num = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        }
        
        # 全角数字変換
        num_str = num_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        # 漢数字の場合
        if num_str in kanji_to_num:
            return kanji_to_num[num_str]
        
        # 通常の数字
        try:
            return int(num_str)
        except ValueError:
            return 1  # デフォルト値
    
    def _determine_genre(self, source: Dict) -> str:
        """出典情報からジャンルを判定"""
        title = source.get('title', '')
        author = source.get('author', '')
        
        # タイトルや著者名からジャンルを推定
        if any(word in title for word in ['物語', '小説', 'ストーリー']):
            return '小説・物語'
        elif any(word in title for word in ['論', '考察', '研究', '分析']):
            return '評論・論説'
        elif any(word in title for word in ['随筆', 'エッセイ', '紀行']):
            return '随筆・エッセイ'
        elif any(word in title for word in ['詩', '短歌', '俳句']):
            return '詩歌'
        else:
            # デフォルトでコンテンツから判断
            return '評論・論説'  # 仮のデフォルト
    
    def _extract_keywords(self, text: str) -> List[str]:
        """問題文からキーワードを抽出"""
        keywords = []
        
        # 重要な指示語
        instruction_words = [
            '説明', '理由', '気持ち', '考え', '意味', '内容',
            '違い', '共通点', '対比', '変化', '原因', '結果'
        ]
        
        for word in instruction_words:
            if word in text:
                keywords.append(word)
        
        # 文中の「」内の重要語句
        quoted_matches = re.findall(r'「([^」]{2,20})」', text)
        keywords.extend(quoted_matches[:3])  # 最大3つまで
        
        return keywords
    
    def _calculate_statistics(self, result: Dict) -> Dict[str, Any]:
        """統計情報を計算"""
        stats = {
            'average_questions_per_section': 0,
            'question_type_distribution': {},
            'most_common_type': None,
            'char_limit_range': None,
            'has_choice_questions': False,
            'has_written_questions': False
        }
        
        # 大問あたりの平均問題数
        if result['sections']:
            stats['average_questions_per_section'] = result['total_questions'] / len(result['sections'])
        
        # 問題種別の分布
        total = result['total_questions']
        if total > 0:
            for q_type, count in result['question_types'].items():
                stats['question_type_distribution'][q_type] = {
                    'count': count,
                    'percentage': round(count / total * 100, 1)
                }
        
        # 最も多い問題種別
        if result['question_types']:
            stats['most_common_type'] = max(result['question_types'].items(), key=lambda x: x[1])[0]
        
        # 記述式と選択式の有無
        stats['has_choice_questions'] = result['question_types'].get('選択式', 0) > 0
        stats['has_written_questions'] = result['question_types'].get('記述式', 0) > 0
        
        # 字数制限の範囲
        char_limits = []
        for section in result['sections']:
            for q in section['questions']:
                if q['char_limit']:
                    if isinstance(q['char_limit'], dict):
                        if 'limit' in q['char_limit']:
                            char_limits.append(q['char_limit']['limit'])
                        elif 'max' in q['char_limit']:
                            char_limits.append(q['char_limit']['max'])
        
        if char_limits:
            stats['char_limit_range'] = {
                'min': min(char_limits),
                'max': max(char_limits),
                'average': round(sum(char_limits) / len(char_limits))
            }
        
        return stats
    
    def generate_report(self, analysis: Dict) -> str:
        """分析結果のレポートを生成"""
        report = []
        report.append("=" * 70)
        report.append("問題構成の詳細分析")
        report.append("=" * 70)
        report.append("")
        
        # 全体統計
        report.append(f"【全体統計】")
        report.append(f"総設問数: {analysis['total_questions']}問")
        report.append(f"大問数: {len(analysis['sections'])}問")
        stats = analysis['statistics']
        report.append(f"大問あたり平均設問数: {stats['average_questions_per_section']:.1f}問")
        report.append("")
        
        # 問題種別の分布
        report.append("【問題種別の内訳】")
        for q_type, data in sorted(stats['question_type_distribution'].items(), 
                                  key=lambda x: x[1]['count'], reverse=True):
            report.append(f"  {q_type}: {data['count']}問 ({data['percentage']}%)")
        report.append("")
        
        # 字数制限情報
        if stats['char_limit_range']:
            report.append("【記述式問題の字数制限】")
            report.append(f"  最小: {stats['char_limit_range']['min']}字")
            report.append(f"  最大: {stats['char_limit_range']['max']}字")
            report.append(f"  平均: {stats['char_limit_range']['average']}字")
            report.append("")
        
        # 大問別詳細
        report.append("【大問別詳細】")
        report.append("-" * 70)
        
        for section in analysis['sections']:
            report.append(f"\n■ 大問{section['section_number']}")
            
            # 出典情報
            if section.get('source'):
                source = section['source']
                if source.get('author') and source.get('title'):
                    report.append(f"  出典: {source['author']}『{source['title']}』")
                elif source.get('title'):
                    report.append(f"  出典: 『{source['title']}』")
            
            if section.get('genre'):
                report.append(f"  ジャンル: {section['genre']}")
            
            report.append(f"  設問数: {section['question_count']}問")
            report.append(f"  文字数: 約{section['text_length']:,}文字")
            
            # 設問種別
            if section['question_types']:
                report.append("  設問種別:")
                for q_type, count in sorted(section['question_types'].items()):
                    report.append(f"    - {q_type}: {count}問")
            
            # 個別設問の詳細（最初の3問のみ表示）
            if section['questions']:
                report.append("  設問詳細（抜粋）:")
                for q in section['questions'][:3]:
                    detail = f"    問{q['number']}: {q['type']}"
                    if q['char_limit']:
                        if 'limit' in q['char_limit']:
                            detail += f" ({q['char_limit']['limit']}字{q['char_limit']['condition']})"
                        elif 'max' in q['char_limit']:
                            detail += f" ({q['char_limit']['min']}～{q['char_limit']['max']}字)"
                    if q['choice_count']:
                        detail += f" ({q['choice_count']}択)"
                    report.append(detail)
                
                if len(section['questions']) > 3:
                    report.append(f"    ... 他{len(section['questions'])-3}問")
        
        report.append("")
        report.append("=" * 70)
        
        return '\n'.join(report)