#!/usr/bin/env python3
"""
ハイブリッドOCRシステム
Google Vision APIと高精度OCR（bunkoOCR等）の出力を統合
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from abc import ABC, abstractmethod


class OCRProvider(ABC):
    """OCRプロバイダーの基底クラス"""
    
    @abstractmethod
    def extract_text(self, source_path: str) -> str:
        """テキストを抽出する"""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """信頼度を取得（0.0-1.0）"""
        pass


class GoogleVisionProvider(OCRProvider):
    """Google Vision APIプロバイダー"""
    
    def extract_text(self, pdf_path: str) -> str:
        """PDFからGoogle Vision APIを使ってテキスト抽出"""
        # 既存のGoogle Vision API実装を使用
        from modules.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        pages = processor.extract_text_from_pdf(pdf_path)
        return "\n".join([page['text'] for page in pages])
    
    def get_confidence(self) -> float:
        """縦書き日本語での信頼度は中程度"""
        return 0.7


class HighAccuracyTextProvider(OCRProvider):
    """高精度テキストファイルプロバイダー（bunkoOCR等の出力）"""
    
    def __init__(self, text_file_path: str):
        self.text_file_path = text_file_path
    
    def extract_text(self, source_path: str = None) -> str:
        """テキストファイルから直接読み込み"""
        with open(self.text_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_confidence(self) -> float:
        """高精度OCRの信頼度は高い"""
        return 0.95


class BunkoOCRProvider(OCRProvider):
    """bunkoOCRプロバイダー"""
    
    def __init__(self, result_dir: str):
        self.result_dir = Path(result_dir)
    
    def extract_text(self, source_path: str = None) -> str:
        """bunkoOCRの結果から統合テキストを生成"""
        texts = []
        
        # text*.txtファイルを番号順に読み込み
        text_files = sorted(self.result_dir.glob("text*.txt"),
                          key=lambda x: int(re.search(r'text(\d+)', x.name).group(1)))
        
        for text_file in text_files:
            with open(text_file, 'r', encoding='utf-8') as f:
                texts.append(f.read())
        
        # result*.jsonから構造情報も取得可能
        return "\n".join(texts)
    
    def get_confidence(self) -> float:
        """bunkoOCRの縦書き日本語精度は非常に高い"""
        return 0.98


class HybridOCRAnalyzer:
    """複数のOCRソースを統合して分析するシステム"""
    
    def __init__(self):
        self.providers: List[OCRProvider] = []
        self.school_patterns = self._load_school_patterns()
    
    def add_provider(self, provider: OCRProvider):
        """OCRプロバイダーを追加"""
        self.providers.append(provider)
    
    def _load_school_patterns(self) -> Dict:
        """学校別の問題パターンを定義"""
        return {
            '桜蔭': {
                '2015': {
                    'sections': [
                        {'pattern': r'一、次の文章を読んで、後の問いに答えなさい。', 'expected_questions': 6},
                        {'pattern': r'二\s+次の文章を読んで、後の問いに答えなさい。', 'expected_questions': 5}
                    ],
                    'total_questions': 11
                }
            }
        }
    
    def analyze(self, school: str, year: str) -> Dict:
        """複数のOCRソースから最適な結果を選択して分析"""
        
        if not self.providers:
            raise ValueError("OCRプロバイダーが設定されていません")
        
        # 各プロバイダーから結果を取得
        results = []
        for provider in self.providers:
            try:
                text = provider.extract_text(None)
                confidence = provider.get_confidence()
                analysis = self._analyze_text(text, school, year)
                
                results.append({
                    'provider': provider.__class__.__name__,
                    'confidence': confidence,
                    'text': text,
                    'analysis': analysis,
                    'accuracy': self._calculate_accuracy(analysis, school, year)
                })
            except Exception as e:
                print(f"プロバイダー {provider.__class__.__name__} でエラー: {e}")
        
        # 最も精度の高い結果を選択
        best_result = max(results, key=lambda x: x['accuracy'] * x['confidence'])
        
        return {
            'selected_provider': best_result['provider'],
            'confidence': best_result['confidence'],
            'accuracy': best_result['accuracy'],
            'analysis': best_result['analysis'],
            'all_results': results
        }
    
    def _analyze_text(self, text: str, school: str, year: str) -> Dict:
        """テキストを分析（学校・年度別のロジック）"""
        
        if school == '桜蔭' and year == '2015':
            # 桜蔭2015年度専用の分析ロジックを使用
            from analyze_perfect_text import analyze_sakuragai_2015_perfect
            
            # テキストを一時ファイルに保存
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_path = f.name
            
            try:
                result = analyze_sakuragai_2015_perfect(temp_path)
            finally:
                os.unlink(temp_path)
            
            return result
        else:
            # 汎用分析ロジック
            from modules.text_analyzer import TextAnalyzer
            analyzer = TextAnalyzer()
            return analyzer.analyze_exam_structure(text)
    
    def _calculate_accuracy(self, analysis: Dict, school: str, year: str) -> float:
        """分析結果の精度を計算"""
        
        if school not in self.school_patterns:
            return 0.5  # 未知の学校
        
        if year not in self.school_patterns[school]:
            return 0.5  # 未知の年度
        
        expected = self.school_patterns[school][year]['total_questions']
        detected = analysis.get('total_questions', 0)
        
        if expected == 0:
            return 0.0
        
        # 検出率を精度として使用
        accuracy = min(detected / expected, 1.0)
        
        # 過検出の場合はペナルティ
        if detected > expected:
            accuracy = accuracy - 0.1 * (detected - expected)
        
        return max(0.0, accuracy)


def main():
    """使用例"""
    
    # ハイブリッドアナライザーを初期化
    analyzer = HybridOCRAnalyzer()
    
    # 1. Google Vision APIプロバイダー
    analyzer.add_provider(GoogleVisionProvider())
    
    # 2. 高精度テキストファイルプロバイダー（存在する場合）
    text_file = '/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/桜蔭/15桜蔭.txt'
    if os.path.exists(text_file):
        analyzer.add_provider(HighAccuracyTextProvider(text_file))
    
    # 3. bunkoOCRプロバイダー（存在する場合）
    # bunko_dir = '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results/...'
    # if os.path.exists(bunko_dir):
    #     analyzer.add_provider(BunkoOCRProvider(bunko_dir))
    
    # 分析実行
    result = analyzer.analyze('桜蔭', '2015')
    
    # 結果表示
    print("\n=== ハイブリッドOCR分析結果 ===\n")
    print(f"選択されたプロバイダー: {result['selected_provider']}")
    print(f"信頼度: {result['confidence']:.2%}")
    print(f"精度: {result['accuracy']:.2%}")
    
    analysis = result['analysis']
    print(f"\n検出結果:")
    print(f"学校: {analysis['school']}")
    print(f"年度: {analysis['year']}")
    print(f"総設問数: {analysis['total_questions']}問")
    
    print("\n【全プロバイダーの結果】")
    for r in result['all_results']:
        print(f"- {r['provider']}: 信頼度={r['confidence']:.2%}, "
              f"精度={r['accuracy']:.2%}, 検出数={r['analysis']['total_questions']}問")


if __name__ == "__main__":
    main()