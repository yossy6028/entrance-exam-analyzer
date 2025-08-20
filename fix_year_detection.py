#!/usr/bin/env python3
"""
年度検出の改良版実装
文脈を考慮した年度検出で誤検出を削減
"""

import re
import sys
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

# プロジェクトのモジュールをインポートするためのパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.year_detector import YearDetector, YearPattern
from models import YearDetectionResult
from exceptions import YearDetectionError
from config.settings import Settings

class ImprovedYearDetector(YearDetector):
    """改良版年度検出クラス"""
    
    def __init__(self):
        super().__init__()
        self._initialize_context_patterns()
    
    def _initialize_context_patterns(self):
        """文脈判定用パターンを初期化"""
        # 歴史的文脈を示すパターン（年度ではない）
        self.historical_context_patterns = [
            r'[平成昭和](\d{1,2})年[にで]',  # 平成15年に、昭和60年で
            r'西暦(\d{4})年[のに]',          # 西暦2000年の、西暦1995年に
            r'(\d{4})年[のに]起[きこ]',      # 2000年に起きた、1995年の起こった
            r'(\d{4})年[のに]制定',          # 2000年に制定された
            r'(\d{4})年[のに][設建]',        # 2000年に設立、1995年に建設
            r'創立[記念]*[:\s]*(\d{4})年',   # 創立記念: 2000年、創立 1995年
        ]
        
        # 問題番号や回数を示すパターン（年度ではない）
        self.numeric_context_patterns = [
            r'問題(\d{1,2})[番号]*',         # 問題15番、問題15
            r'設問(\d{1,2})[番号]*',         # 設問15番、設問15
            r'第(\d{1,2})回',               # 第15回
            r'第(\d{1,2})[問章節]',          # 第15問、第15章
            r'(\d{1,2})[個問人分]',          # 15個、15問、15人、15分
            r'(\d{4})[mMメートル]',          # 2000m、2000メートル
            r'受験番号[:\s]*(\d+)',          # 受験番号: 2000
            r'生徒番号[:\s]*(\d+)',          # 生徒番号: 15
        ]
        
        # 実際の年度を示す強いパターン
        self.strong_year_patterns = [
            r'(\d{4})年度[入学試験生募集]',   # 2025年度入学試験、2025年度生募集
            r'令和(\d{1,2})年度[入学試験生募集]', # 令和7年度入学試験
            r'実施年度[:\s]*',              # 実施年度: 
            r'([一二三四五六七八九〇０-９]{4})年度[入学試験生募集]', # 二〇二五年度入学試験
        ]
    
    def detect_years(self, text: str, file_path: Optional[Path] = None) -> YearDetectionResult:
        """
        改良版年度検出
        文脈を考慮して歴史的年号と試験年度を区別
        """
        # 元の検出処理を実行
        original_result = super().detect_years(text, file_path)
        
        if len(original_result.years) <= 1:
            return original_result
        
        # 複数年度が検出された場合、文脈分析を実行
        filtered_years = self._filter_years_by_context(text, original_result)
        
        if not filtered_years:
            # フィルタリングで全て除外された場合は元の結果を返す
            filtered_years = original_result.years
        
        # 新しい結果を作成
        new_confidence = self._calculate_improved_confidence(filtered_years, original_result.detection_patterns)
        
        return YearDetectionResult(
            years=filtered_years,
            detection_patterns=original_result.detection_patterns,
            confidence=new_confidence
        )
    
    def _filter_years_by_context(self, text: str, result: YearDetectionResult) -> List[str]:
        """文脈に基づいて年度をフィルタリング"""
        year_scores = {}  # 年度ごとのスコア
        
        for year in result.years:
            year_scores[year] = 0
            
            # 強い年度パターンにマッチするかチェック
            for pattern in self.strong_year_patterns:
                if re.search(pattern.replace(r'(\d{4})', year), text):
                    year_scores[year] += 10
                    break
            
            # 歴史的文脈にマッチするかチェック（スコアを下げる）
            for pattern in self.historical_context_patterns:
                if re.search(pattern, text):
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        matched_year = self._extract_year_from_match(match, pattern)
                        if matched_year == year:
                            year_scores[year] -= 5
            
            # 数値的文脈にマッチするかチェック（スコアを下げる）
            for pattern in self.numeric_context_patterns:
                if re.search(pattern, text):
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        matched_year = self._extract_year_from_match(match, pattern)
                        if matched_year == year or self._two_digit_to_year(matched_year) == year:
                            year_scores[year] -= 3
            
            # 検出パターンによるスコア調整
            for pattern_name, pattern_matches in result.detection_patterns.items():
                for _, detected_year in pattern_matches:
                    if detected_year == year:
                        if pattern_name in ['year_kanji', 'year_4digit', 'reiwa']:
                            year_scores[year] += 5  # 明確な年度パターン
                        elif pattern_name in ['heisei']:
                            year_scores[year] += 2  # 平成は文脈次第
                        elif pattern_name in ['year_2digit']:
                            year_scores[year] += 1  # 2桁は信頼度低
        
        # スコアが最も高い年度を選択
        if not year_scores:
            return result.years
        
        max_score = max(year_scores.values())
        
        # 正のスコアの年度のみを選択
        best_years = [year for year, score in year_scores.items() if score == max_score and score > 0]
        
        if not best_years:
            # 全て負のスコアの場合、最もマイナスが少ない年度を選択
            best_years = [year for year, score in year_scores.items() if score == max_score]
        
        return best_years
    
    def _extract_year_from_match(self, match, pattern):
        """正規表現マッチから年度を抽出"""
        try:
            if r'平成' in pattern:
                heisei_year = match.group(1)
                return str(1988 + int(heisei_year))
            elif r'西暦' in pattern or r'\d{4}' in pattern:
                return match.group(1)
            else:
                return match.group(1)
        except:
            return None
    
    def _calculate_improved_confidence(self, years: List[str], patterns: Dict) -> float:
        """改良版信頼度計算"""
        if not years:
            return 0.0
        
        score = 0.0
        
        # 単一年度の場合は信頼度を上げる
        if len(years) == 1:
            score += 0.3
        
        # 高優先度パターンで検出された場合
        if any(p in patterns for p in ['year_kanji', 'year_4digit', 'reiwa']):
            score += 0.4
        
        # 複数パターンで検出された場合
        if len(patterns) > 1:
            score += 0.2
        
        # ファイル名から検出された場合
        if 'filename' in patterns:
            score += 0.3
        
        return min(score, 1.0)

def test_improved_detector():
    """改良版検出器のテスト"""
    print("=== 改良版年度検出器のテスト ===\n")
    
    test_cases = [
        {
            'name': '聖光学院タイプ（複数年度誤検出）',
            'text': """聖光学院中学校
二〇二五年度入学試験問題

【歴史問題】
1. 平成15年に制定された法律について述べよ。
2. 西暦2000年に起きた出来事を説明せよ。

【参考資料】 
・創立記念: 2000年設立
・第15回記念行事開催
・令和7年度入学生募集要項

【試験概要】
実施年度: 二〇二五年度
試験科目: 国語・数学・社会・理科
""",
            'expected': ['2025']
        },
        {
            'name': '歴史問題が多い場合',
            'text': """2025年度入学試験問題（歴史）
1. 平成15年に制定された個人情報保護法について
2. 昭和39年の東京オリンピック開催について  
3. 西暦2000年のIT革命について
4. 1995年の阪神淡路大震災について
""",
            'expected': ['2025']
        },
        {
            'name': '問題番号が多い場合',
            'text': """令和7年度入学試験問題
問題15番: 次の計算をしなさい
設問25: 以下から正しいものを選べ
第30回記念問題
""",
            'expected': ['2025']
        }
    ]
    
    original_detector = YearDetector()
    improved_detector = ImprovedYearDetector()
    
    for test_case in test_cases:
        print(f"【{test_case['name']}】")
        
        # 元のデテクター
        original_result = original_detector.detect_years(test_case['text'])
        print(f"元の結果: {original_result.years} (信頼度: {original_result.confidence:.2f})")
        
        # 改良版デテクター
        improved_result = improved_detector.detect_years(test_case['text'])
        print(f"改良版: {improved_result.years} (信頼度: {improved_result.confidence:.2f})")
        
        print(f"期待値: {test_case['expected']}")
        print(f"改良版一致: {'✓' if improved_result.years == test_case['expected'] else '✗'}")
        print("-" * 60)

def create_patch_file():
    """YearDetectorクラスへの修正パッチを作成"""
    print("\n=== 修正パッチの作成 ===\n")
    
    patch_content = '''
def _filter_historical_contexts(self, text: str, detected_years: Dict[str, int], patterns: Dict) -> Dict[str, int]:
    """歴史的文脈の年号を除外"""
    historical_patterns = [
        r'[平成昭和]\\d{1,2}年[にで]',     # 平成15年に、昭和60年で
        r'西暦\\d{4}年[のに]',            # 西暦2000年の、西暦1995年に  
        r'\\d{4}年[のに]起[きこ]',        # 2000年に起きた
        r'\\d{4}年[のに]制定',           # 2000年に制定された
        r'創立[記念]*[:\\s]*\\d{4}年',    # 創立記念: 2000年
    ]
    
    filtered_years = detected_years.copy()
    
    for pattern in historical_patterns:
        for match in re.finditer(pattern, text):
            # マッチした年度を除外対象として検討
            for year in list(filtered_years.keys()):
                if year in match.group(0):
                    # 強い年度パターン（試験年度）で検出されていない場合は除外
                    is_strong_year = any(
                        pattern_name in ['year_kanji', 'reiwa'] and 
                        any(pos < 100 for pos, y in matches if y == year)  # 文書前半での検出
                        for pattern_name, matches in patterns.items()
                    )
                    
                    if not is_strong_year:
                        del filtered_years[year]
    
    return filtered_years
'''
    
    print("YearDetectorクラスに追加するメソッド:")
    print(patch_content)
    
    # 実際の修正案を年度検出器に適用するコードも提案
    print("\ndetect_yearsメソッドへの修正箇所:")
    print("""
# 152行目付近に追加:
# 複数年度が検出された場合、歴史的文脈をフィルタリング
if len(years) > 1:
    original_detected_years = detected_years.copy()
    filtered_detected_years = self._filter_historical_contexts(text, detected_years, detection_patterns)
    
    if len(filtered_detected_years) == 1:
        # フィルタリングで単一年度になった場合はそれを採用
        years = list(filtered_detected_years.keys())
        confidence = 0.9  # 文脈フィルタリングで特定されたので高信頼度
""")

if __name__ == "__main__":
    test_improved_detector()
    create_patch_file()