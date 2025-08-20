"""
改善されたテーマ抽出システム
OCRノイズの除去と参照型問題の解決に特化
"""

import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TextAnalysisResult:
    """テキスト分析結果"""
    clean_text: str
    theme: Optional[str]
    confidence: float
    noise_removed: List[str]
    reference_content: Dict[str, str]


class ImprovedThemeExtractor:
    """改善されたテーマ抽出クラス"""
    
    def __init__(self):
        self.ocr_noise_patterns = self._init_noise_patterns()
        self.theme_keywords = self._init_theme_keywords()
        self.reference_patterns = self._init_reference_patterns()
    
    def _init_noise_patterns(self) -> Dict[str, List[str]]:
        """OCRノイズパターンの初期化"""
        return {
            'administrative': [
                r'受験番号[：:\s]*\d*',
                r'採点[欄者][：:\s]*',
                r'検印[：:\s]*',
                r'得点[：:\s]*\d*',
                r'解答用紙',
                r'答案用紙',
                r'記入欄',
                r'氏名欄',
                r'学校名',
                r'組[：:\s]*\d*',
                r'番[：:\s]*\d*'
            ],
            'formatting_instructions': [
                r'この人物について?',
                r'あらわしている?',
                r'若くして結婚した?',
                r'まちがっている文章を[選択]?',
                r'正しい文章を[選択]?',
                r'適切なものを[一つ]?選[べび]',
                r'次の中から選[べび]',
                r'以下の[問い問題]に答えなさい',
                r'記述しなさい',
                r'抜き出しなさい',
                r'語句選択',
                r'空欄補充'
            ],
            'reference_markers': [
                r'下線[①②③④⑤⑥⑦⑧⑨⑩]について?',
                r'※印の部分について?',
                r'★印について?',
                r'傍線部[ア-ン]について?',
                r'波線部について?'
            ]
        }
    
    def _init_theme_keywords(self) -> Dict[str, Dict[str, any]]:
        """より詳細なテーマキーワードの初期化"""
        return {
            '友情・人間関係': {
                'core_keywords': [
                    '友情', '友達', '友人', '親友', '仲間', 
                    '友', '一緒', '協力', '助け合い', '信頼'
                ],
                'context_keywords': [
                    '遊び', '学校', '思い出', '共有', '絆',
                    '理解', '支える', '励まし', '相談'
                ],
                'negative_keywords': ['敵', '裏切り', '喧嘩'],
                'weight': 3.0
            },
            '家族・親子関係': {
                'core_keywords': [
                    '家族', '父', '母', '親', '子', '息子', '娘',
                    '兄弟', '姉妹', '祖父', '祖母', '家庭'
                ],
                'context_keywords': [
                    '愛情', '教育', '育つ', '成長', '温かい',
                    '守る', '支える', '伝える', '継承'
                ],
                'weight': 3.0
            },
            '成長・自己発見': {
                'core_keywords': [
                    '成長', '大人', '変化', '発見', '気づき',
                    '学び', '体験', '経験', '挑戦', '努力'
                ],
                'context_keywords': [
                    '子供', '大人', '変わる', '分かる', '理解',
                    '新しい', '初めて', '失敗', '成功'
                ],
                'weight': 2.5
            },
            '自然・環境': {
                'core_keywords': [
                    '自然', '環境', '地球', '生態', '生物',
                    '森', '海', '山', '川', '空', '動物', '植物'
                ],
                'context_keywords': [
                    '保護', '破壊', '共生', '美しい', '豊か',
                    '季節', '気候', '温暖化', '汚染'
                ],
                'weight': 2.5
            },
            '科学・技術・未来': {
                'core_keywords': [
                    '科学', '技術', '発明', 'AI', 'ロボット',
                    '宇宙', '研究', '実験', '発見', '革新'
                ],
                'context_keywords': [
                    '進歩', '発達', '便利', '効率', '自動',
                    '未来', '可能性', 'データ', '情報'
                ],
                'weight': 2.0
            },
            '社会・文化・歴史': {
                'core_keywords': [
                    '社会', '文化', '歴史', '伝統', '現代',
                    '時代', '変遷', '発展', '制度', '政治'
                ],
                'context_keywords': [
                    '古い', '新しい', '継承', '変革', '影響',
                    '価値観', '習慣', '風俗', '民族'
                ],
                'weight': 2.0
            },
            '哲学・価値観・生き方': {
                'core_keywords': [
                    '哲学', '思想', '価値観', '生き方', '意味',
                    '本質', '真理', '道徳', '倫理', '正義'
                ],
                'context_keywords': [
                    '考える', '悩む', '答え', '問い', '疑問',
                    '信念', '原則', '判断', '選択'
                ],
                'weight': 1.8
            }
        }
    
    def _init_reference_patterns(self) -> Dict[str, str]:
        """参照マーカーのパターン初期化"""
        return {
            'underline': r'下線([①②③④⑤⑥⑦⑧⑨⑩])',
            'sideline': r'傍線部([ア-ン])',
            'asterisk': r'※印',
            'star': r'★印',
            'wave': r'波線部'
        }
    
    def clean_ocr_noise(self, text: str) -> Tuple[str, List[str]]:
        """OCRノイズを除去"""
        cleaned_text = text
        removed_noise = []
        
        for category, patterns in self.ocr_noise_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text)
                if matches:
                    removed_noise.extend([f"{category}: {match}" for match in matches])
                cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # 余分な空白を整理
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text, removed_noise
    
    def extract_reference_content(self, text: str) -> Dict[str, str]:
        """参照マーカー周辺のコンテンツを抽出"""
        reference_content = {}
        
        for ref_type, pattern in self.reference_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                marker = match.group(0)
                start_pos = match.start()
                
                # マーカー周辺のコンテンツを抽出（前後100文字）
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), start_pos + 200)
                context = text[context_start:context_end]
                
                # より具体的なコンテンツを抽出
                content = self._extract_meaningful_content(context, marker)
                if content:
                    reference_content[marker] = content
        
        return reference_content
    
    def _extract_meaningful_content(self, context: str, marker: str) -> str:
        """参照マーカー周辺から意味のあるコンテンツを抽出"""
        # マーカーを除去
        context = context.replace(marker, '')
        
        # より包括的な抽出ロジック
        # 1. 句点で区切られた文を抽出
        sentences = re.split(r'[。！？\n]', context)
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # 短すぎる文や指示文は除外、但し最小長を緩和
            if (len(sentence) > 5 and 
                not re.search(r'選択|記述|抜き出|答え|問[い題]|設問', sentence)):
                meaningful_sentences.append(sentence)
        
        if meaningful_sentences:
            # 最も長い文を返す
            return max(meaningful_sentences, key=len)
        
        # 2. フォールバック: 記号を除いて連続する意味のある部分を抽出
        cleaned_context = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩ア-ン※★]', '', context)
        words = cleaned_context.split()
        if len(words) > 3:
            return ' '.join(words[:15])  # 最初の15語を取る
        
        return ""
    
    def detect_theme_advanced(self, text: str) -> Tuple[Optional[str], float]:
        """改善されたテーマ検出"""
        theme_scores = {}
        
        # 各テーマについてスコアを計算
        for theme, config in self.theme_keywords.items():
            score = 0.0
            weight = config.get('weight', 1.0)
            
            # コアキーワードの重み付きスコア
            for keyword in config.get('core_keywords', []):
                count = len(re.findall(re.escape(keyword), text, re.IGNORECASE))
                score += count * 3.0 * weight
            
            # コンテキストキーワードのスコア
            for keyword in config.get('context_keywords', []):
                count = len(re.findall(re.escape(keyword), text, re.IGNORECASE))
                score += count * 1.5 * weight
            
            # ネガティブキーワードで減点
            for keyword in config.get('negative_keywords', []):
                count = len(re.findall(re.escape(keyword), text, re.IGNORECASE))
                score -= count * 2.0 * weight
            
            # 最小閾値を適用（5点以下は除外）
            if score >= 5.0:
                theme_scores[theme] = score
        
        if not theme_scores:
            return None, 0.0
        
        # 最高スコアのテーマを選択
        best_theme = max(theme_scores.items(), key=lambda x: x[1])
        theme_name, theme_score = best_theme
        
        # 信頼度を計算（0-100の範囲）
        max_possible_score = theme_score + 10  # 理論的最大スコア
        confidence = min(100.0, (theme_score / max_possible_score) * 100)
        
        return theme_name, confidence
    
    def analyze_text(self, text: str) -> TextAnalysisResult:
        """総合的なテキスト分析"""
        # 1. OCRノイズを除去
        clean_text, noise_removed = self.clean_ocr_noise(text)
        
        # 2. 参照コンテンツを抽出
        reference_content = self.extract_reference_content(text)
        
        # 3. 参照コンテンツも含めて分析用テキストを拡張
        analysis_text = clean_text
        for marker, content in reference_content.items():
            analysis_text += f" {content}"
        
        # 4. テーマを検出
        theme, confidence = self.detect_theme_advanced(analysis_text)
        
        return TextAnalysisResult(
            clean_text=clean_text,
            theme=theme,
            confidence=confidence,
            noise_removed=noise_removed,
            reference_content=reference_content
        )


def test_improved_theme_extractor():
    """改善されたテーマ抽出器のテスト"""
    extractor = ImprovedThemeExtractor()
    
    # テストケース
    test_cases = [
        {
            'text': '''
            受験番号: 2025001 採点欄: 
            この人物について述べている。下線①について答えなさい。
            友達と一緒に過ごした楽しい思い出を振り返る。
            まちがっている文章を選択しなさい。
            ''',
            'expected_theme': '友情・人間関係'
        },
        {
            'text': '''
            解答用紙 氏名欄: 
            あらわしている内容について。
            自然の美しさを感じながら、森の中を歩いた。
            動物たちと共に生きる環境の大切さを学んだ。
            ''',
            'expected_theme': '自然・環境'
        },
        {
            'text': '''
            若くして結婚した人物の話。
            下線②について答えよ。
            科学技術の発展により、AIやロボットが普及している。
            未来の可能性について研究が進んでいる。
            ''',
            'expected_theme': '科学・技術・未来'
        }
    ]
    
    print("=== 改善されたテーマ抽出器のテスト ===")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        print(f"原文: {case['text'][:100]}...")
        
        result = extractor.analyze_text(case['text'])
        
        print(f"除去されたノイズ: {result.noise_removed}")
        print(f"参照コンテンツ: {result.reference_content}")
        print(f"クリーンテキスト: {result.clean_text}")
        print(f"検出テーマ: {result.theme}")
        print(f"信頼度: {result.confidence:.1f}%")
        print(f"期待テーマ: {case['expected_theme']}")
        
        success = result.theme == case['expected_theme']
        print(f"結果: {'✅ 成功' if success else '❌ 失敗'}")


if __name__ == "__main__":
    test_improved_theme_extractor()