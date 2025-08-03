"""
改善されたテキスト分析モジュール
桜蔭15年度のような複雑な構造にも対応
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class ImprovedTextAnalyzer:
    """改善されたテキスト分析クラス"""
    
    def __init__(self, question_patterns: Dict[str, List[str]]):
        self.question_patterns = question_patterns
        self.compiled_patterns = {}
        
        # パターンをコンパイル
        for q_type, patterns in question_patterns.items():
            self.compiled_patterns[q_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
            
    def analyze_exam_structure(self, text: str) -> Dict[str, Any]:
        """
        試験問題の構造を分析（改善版）
        """
        result = {
            'total_characters': len(text.replace(' ', '').replace('\n', '')),
            'sections': [],
            'questions': [],
            'question_types': defaultdict(int),
            'theme': None
        }
        
        # 大問の検出（改善版）
        sections = self._detect_sections_improved(text)
        result['sections'] = sections
        
        # 各大問内の設問を検出
        for section in sections:
            questions = self._detect_questions_improved(section['text'], section['number'])
            for q in questions:
                q['section'] = section['number']
                result['questions'].append(q)
                
        # 設問タイプの分類
        for question in result['questions']:
            q_type = self._classify_question_type(question['text'])
            question['type'] = q_type
            result['question_types'][q_type] += 1
            
        return result
        
    def _detect_sections_improved(self, text: str) -> List[Dict[str, Any]]:
        """
        大問を検出（改善版）
        """
        sections = []
        
        # 大問パターン（桜蔭用に最適化）
        # パターン1: 「一、次の文章を読んで」
        pattern1 = re.compile(r'([一二三四五六七八九十])[\s、]+次の文章を読んで')
        # パターン2: ページ区切りを考慮
        
        # 全文から大問を検索
        matches = []
        for match in pattern1.finditer(text):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'number_text': match.group(1),
                'full_text': match.group(0)
            })
        
        # マッチがない場合は、ページごとに大問を推定
        if not matches:
            # ページ2の開始位置を探す
            page2_pattern = r'=== ページ 2 ==='
            page2_match = re.search(page2_pattern, text)
            if page2_match:
                # ページ1を大問一とする
                matches.append({
                    'start': 0,
                    'end': 100,
                    'number_text': '一',
                    'full_text': '一、'
                })
                
                # ページ2に大問二があるか確認
                page2_text = text[page2_match.end():]
                if '二 次の文章を読んで' in page2_text or '二　次の文章を読んで' in page2_text:
                    pos = page2_text.find('二')
                    if pos >= 0:
                        matches.append({
                            'start': page2_match.end() + pos,
                            'end': page2_match.end() + pos + 20,
                            'number_text': '二',
                            'full_text': '二 次の文章を読んで'
                        })
        
        # セクションを構築
        kanji_to_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
        
        for i, match in enumerate(matches):
            start = match['start']
            end = matches[i + 1]['start'] if i + 1 < len(matches) else len(text)
            
            section_text = text[start:end]
            number = kanji_to_num.get(match['number_text'], i + 1)
            
            sections.append({
                'number': number,
                'marker': match['full_text'],
                'text': section_text,
                'start_pos': start,
                'end_pos': end
            })
        
        # セクションが見つからない場合は全体を1つとする
        if not sections:
            sections = [{
                'number': 1,
                'marker': '',
                'text': text,
                'start_pos': 0,
                'end_pos': len(text)
            }]
            
        return sections
    
    def _detect_questions_improved(self, text: str, section_num: int) -> List[Dict[str, Any]]:
        """
        設問を検出（改善版）
        """
        questions = []
        
        # 設問パターン（包括的）
        patterns = [
            # 問一〜問六（漢数字）
            (r'問([一二三四五六七八九十])', 'kanji_question'),
            # 間一〜間六（OCR誤認識）
            (r'間([一二三四五六七八九十])', 'kanji_question_ocr'),
            # 問1〜問10（算用数字）
            (r'問([0-9０-９]+)', 'number_question'),
            # 丸数字
            (r'([①②③④⑤⑥⑦⑧⑨⑩])', 'circle_number'),
            # カッコ数字
            (r'[\(（]([0-9０-９]+)[\)）]', 'parenthesis_number'),
        ]
        
        all_matches = []
        for pattern, p_type in patterns:
            for match in re.finditer(pattern, text):
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'marker': match.group(0),
                    'type': p_type,
                    'number': match.group(1) if match.groups() else match.group(0)
                })
        
        # 位置でソート
        all_matches.sort(key=lambda x: x['start'])
        
        # 重複除去（改善版）
        seen_positions = set()
        unique_questions = []
        
        for match in all_matches:
            # 近い位置の重複をチェック
            pos_key = match['start'] // 50  # 50文字の範囲で同一視
            
            # 同じタイプの問題が近くにある場合はスキップ
            duplicate = False
            for seen_pos, seen_type in seen_positions:
                if abs(match['start'] - seen_pos) < 30 and match['type'] == seen_type:
                    duplicate = True
                    break
            
            if not duplicate:
                unique_questions.append(match)
                seen_positions.add((match['start'], match['type']))
        
        # 設問を構築
        for i, match in enumerate(unique_questions):
            q_start = match['start']
            q_end = unique_questions[i + 1]['start'] if i + 1 < len(unique_questions) else len(text)
            
            question_text = text[q_start:q_end].strip()
            
            # 有効な設問かチェック（改善版）
            if self._is_valid_question_improved(question_text, match['type']):
                questions.append({
                    'number': len(questions) + 1,
                    'marker': match['marker'],
                    'text': question_text,
                    'start_pos': q_start,
                    'end_pos': q_end,
                    'original_type': match['type']
                })
        
        return questions
    
    def _is_valid_question_improved(self, text: str, q_type: str) -> bool:
        """
        有効な設問かどうかを判定（改善版）
        """
        # 最低文字数チェック（タイプ別）
        if q_type in ['circle_number', 'parenthesis_number']:
            min_length = 5  # 記号問題は短くてもOK
        else:
            min_length = 10
            
        if len(text.strip()) < min_length:
            return False
        
        # 数字の羅列だけの場合は無効
        if re.match(r'^[\d\s、。]+$', text.strip()):
            return False
            
        # 設問を示すキーワード（拡張版）
        question_keywords = [
            'なさい', 'か。', 'て。', 'を。', 'に。',
            '答え', '説明', '述べ', '書き', '選び',
            'どの', 'なぜ', 'いつ', 'どこ', 'だれ',
            'について', 'とは', 'ですか', 'でしょうか',
            '漢字', '語句', '慣用句', 'から選び', '語群'
        ]
        
        # キーワードがあるか、または特定のパターンの場合はOK
        if any(keyword in text for keyword in question_keywords):
            return True
            
        # 丸数字で始まる場合は、語句問題の可能性が高い
        if q_type == 'circle_number' and len(text) > 5:
            return True
            
        return False
        
    def _classify_question_type(self, question_text: str) -> str:
        """
        設問タイプを分類（既存のメソッドを流用）
        """
        # 漢字・語句問題のチェック
        if any(pattern.search(question_text) for pattern in self.compiled_patterns.get('漢字・語句', [])):
            return '漢字・語句'
        
        # 丸数字で慣用句・語句問題の場合
        if re.search(r'^[①②③④⑤⑥⑦⑧⑨⑩]', question_text) and \
           re.search(r'慣用句|ことわざ|語句|漢字|語群|に入る', question_text):
            return '漢字・語句'
            
        # 選択肢の存在をチェック（記号選択）
        if re.search(r'[ア-ン]\s*[\.。、]', question_text) or \
           re.search(r'[A-H]\s*[\.。、]', question_text) or \
           any(pattern.search(question_text) for pattern in self.compiled_patterns.get('記号選択', [])):
            return '記号選択'
            
        # 抜き出し問題のチェック
        if any(pattern.search(question_text) for pattern in self.compiled_patterns.get('抜き出し', [])):
            return '抜き出し'
            
        # 脱文挿入のチェック
        if any(pattern.search(question_text) for pattern in self.compiled_patterns.get('脱文挿入', [])):
            return '脱文挿入'
            
        # 記述問題の判定
        if re.search(r'\d+字', question_text):
            return '記述'
            
        # 記述を示唆するキーワード
        description_keywords = [
            '説明し', '述べ', '書き', '答え', 'まとめ',
            '考えを', '理由を', 'どのよう', 'なぜ', 'どうして',
            '〜について', '〜とは', '具体的に', '詳しく'
        ]
        
        if re.search(r'(?:答えなさい|述べなさい|書きなさい|説明しなさい|まとめなさい)[。．]?', question_text):
            if not re.search(r'[ア-ン]\s*[\.。、]', question_text) and \
               not re.search(r'から選び', question_text):
                return '記述'
                
        if any(keyword in question_text for keyword in description_keywords):
            if not re.search(r'[ア-ン]\s*[\.。、]', question_text) and \
               not re.search(r'抜き出し', question_text) and \
               not re.search(r'から選び', question_text):
                return '記述'
                
        return 'その他'