"""
OCR後処理モジュール
改行で分断された文章の再結合とクリーンアップ
"""
import re
import logging
from typing import List, Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class OCRPostProcessor:
    """OCR結果の後処理を行うクラス"""
    
    def __init__(self):
        # 日本語の文末パターン
        self.sentence_end_patterns = [
            r'。$',  # 句点
            r'」$',  # 鍵括弧閉じ
            r'』$',  # 二重鍵括弧閉じ
            r'\)$',  # 括弧閉じ
            r'）$',  # 全角括弧閉じ
        ]
        
        # 出典パターンのマーカー
        self.source_markers = [
            'より',
            'による',
            '所収',
            '出典',
            '著',
            '作',
            '訳',
        ]
        
        # 著者名の可能性が高いパターン
        self.author_patterns = [
            r'^[一-龯]{2,4}[一-龯]*\s*[一-龯]{2,4}$',  # 漢字のフルネーム
            r'^[ぁ-ん]{2,4}[ぁ-ん]*\s*[ぁ-ん]{2,4}$',  # ひらがなのフルネーム
            r'^[ァ-ヴー]{2,8}[・\s][ァ-ヴー]{2,8}$',  # カタカナの外国人名
        ]
        
        # 作品名の可能性が高いパターン
        self.title_patterns = [
            r'『[^』]+』',  # 二重鍵括弧
            r'「[^」]+」',  # 鍵括弧
        ]
    
    def process_text(self, text: str) -> str:
        """
        OCRテキスト全体を処理
        
        Args:
            text: OCR結果のテキスト
            
        Returns:
            処理済みのテキスト
        """
        # 行ごとに分割
        lines = text.split('\n')
        
        # 改行で分断された文章を再結合
        lines = self._rejoin_broken_sentences(lines)
        
        # 出典部分を特定して処理
        lines = self._process_source_citations(lines)
        
        # 不要な空白やノイズを除去
        lines = self._clean_lines(lines)
        
        return '\n'.join(lines)
    
    def _rejoin_broken_sentences(self, lines: List[str]) -> List[str]:
        """
        改行で分断された文章を再結合
        
        Args:
            lines: 行のリスト
            
        Returns:
            再結合された行のリスト
        """
        processed_lines = []
        buffer = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                # 空行はそのまま保持
                if buffer:
                    processed_lines.append(buffer)
                    buffer = ""
                processed_lines.append("")
                continue
            
            # 文末かどうかをチェック
            is_sentence_end = any(re.search(pattern, line) for pattern in self.sentence_end_patterns)
            
            # 次の行が存在し、かつ大文字や記号で始まらない場合は結合候補
            is_continuation = False
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if next_line and not re.match(r'^[A-Z０-９\d【】■□◆◇●○▼▲]', next_line):
                    # 次の行が小文字や日本語で始まる場合は継続の可能性が高い
                    is_continuation = not is_sentence_end
            
            if buffer:
                # バッファに内容がある場合
                if is_continuation:
                    # 継続行として結合
                    buffer += line
                else:
                    # 文の終わりなので、バッファを出力して新しい文を開始
                    buffer += line
                    processed_lines.append(buffer)
                    buffer = ""
            else:
                # バッファが空の場合
                if is_continuation:
                    buffer = line
                else:
                    processed_lines.append(line)
        
        # 残りのバッファを出力
        if buffer:
            processed_lines.append(buffer)
        
        return processed_lines
    
    def _process_source_citations(self, lines: List[str]) -> List[str]:
        """
        出典部分を特定して処理
        
        Args:
            lines: 行のリスト
            
        Returns:
            処理済みの行のリスト
        """
        processed_lines = []
        
        for i, line in enumerate(lines):
            # 出典マーカーを含む行を検出
            if any(marker in line for marker in self.source_markers):
                # 前後の行も含めて出典の可能性を評価
                context_lines = []
                
                # 前の2行を取得
                for j in range(max(0, i-2), i):
                    context_lines.append(lines[j])
                
                # 現在の行
                context_lines.append(line)
                
                # 後の2行を取得
                for j in range(i+1, min(len(lines), i+3)):
                    context_lines.append(lines[j])
                
                # 出典部分を抽出・整形
                processed_line = self._extract_and_format_source(context_lines, line)
                processed_lines.append(processed_line)
            else:
                processed_lines.append(line)
        
        return processed_lines
    
    def _extract_and_format_source(self, context_lines: List[str], target_line: str) -> str:
        """
        コンテキストから出典情報を抽出して整形
        
        Args:
            context_lines: コンテキスト行のリスト
            target_line: 対象行
            
        Returns:
            整形された出典行
        """
        # 全体のコンテキストを結合
        full_context = ' '.join(context_lines)
        
        # 括弧で囲まれた出典パターンを探す
        # 例: (片田珠美 『一億総ガキ社会 「成熟拒否」という病』より)
        bracket_pattern = r'[（\(]([^）\)]*(?:『[^』]+』|「[^」]+」)[^）\)]*(?:より|による))[）\)]'
        match = re.search(bracket_pattern, full_context)
        
        if match:
            source_content = match.group(1)
            
            # 著者名と作品名を分離
            author, title = self._separate_author_and_title(source_content)
            
            if author and title:
                # きれいに整形して返す
                return f"({author}『{title}』より)"
            else:
                # そのまま返す
                return f"({source_content})"
        
        # 括弧なしの出典パターン
        # 例: 片田珠美 『一億総ガキ社会』より
        no_bracket_pattern = r'([^。\n]*(?:『[^』]+』|「[^」]+」)[^。\n]*(?:より|による))'
        match = re.search(no_bracket_pattern, full_context)
        
        if match:
            source_content = match.group(1).strip()
            
            # 不要な前置きを除去
            source_content = self._remove_unnecessary_prefix(source_content)
            
            return source_content
        
        return target_line
    
    def _separate_author_and_title(self, source_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        著者名と作品名を分離
        
        Args:
            source_text: 出典テキスト
            
        Returns:
            (著者名, 作品名)のタプル
        """
        author = None
        title = None
        
        # 作品名を抽出（『』または「」で囲まれた部分）
        title_match = re.search(r'[『「]([^』」]+)[』」]', source_text)
        if title_match:
            title = title_match.group(1)
            
            # 作品名の前の部分を著者名として抽出
            before_title = source_text[:title_match.start()].strip()
            
            # 著者名のクリーンアップ
            author = self._clean_author_name(before_title)
        
        return author, title
    
    def _clean_author_name(self, text: str) -> Optional[str]:
        """
        著者名をクリーンアップ
        
        Args:
            text: 著者名候補のテキスト
            
        Returns:
            クリーンアップされた著者名
        """
        if not text:
            return None
        
        # 不要な記号を除去
        text = re.sub(r'[※＊・\s]+', ' ', text).strip()
        
        # 明らかに著者名でないパターンを除外
        noise_patterns = [
            r'^[ぁ-ん]{1}$',  # ひらがな1文字
            r'^[ァ-ヴ]{1}$',  # カタカナ1文字
            r'^\d+$',  # 数字のみ
            r'^[a-zA-Z]{1,2}$',  # アルファベット1-2文字
            r'Never give up',  # 明らかな誤認識
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, text):
                return None
        
        # 長すぎる場合は最初の部分だけを取る
        if len(text) > 20:
            # スペースや句読点で分割して最初の部分を取る
            parts = re.split(r'[、，\s]+', text)
            if parts:
                text = parts[0]
        
        # 著者名パターンにマッチするかチェック
        for pattern in self.author_patterns:
            if re.match(pattern, text):
                return text
        
        # 最低限の条件（2文字以上、20文字以下）
        if 2 <= len(text) <= 20:
            return text
        
        return None
    
    def _remove_unnecessary_prefix(self, text: str) -> str:
        """
        不要な前置きを除去
        
        Args:
            text: テキスト
            
        Returns:
            クリーンアップされたテキスト
        """
        # 不要な前置きパターン
        prefix_patterns = [
            r'^.*?という現実に直面し[^（\(]*',
            r'^.*?いまや、皆が[^（\(]*',
            r'^.*?もちろん、[^（\(]*',
            r'^.*?たまみ\s*',
        ]
        
        for pattern in prefix_patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()
    
    def _clean_lines(self, lines: List[str]) -> List[str]:
        """
        不要な空白やノイズを除去
        
        Args:
            lines: 行のリスト
            
        Returns:
            クリーンアップされた行のリスト
        """
        cleaned_lines = []
        
        for line in lines:
            # 前後の空白を除去
            line = line.strip()
            
            # 連続する空白を1つに
            line = re.sub(r'\s+', ' ', line)
            
            # HTMLタグを除去
            line = re.sub(r'<[^>]+>', '', line)
            
            # エスケープされた括弧を正規化
            line = line.replace('\\(', '(').replace('\\)', ')')
            
            cleaned_lines.append(line)
        
        return cleaned_lines
    
    def extract_clean_sources(self, text: str) -> List[Dict[str, Any]]:
        """
        テキストからクリーンな出典情報を抽出
        
        Args:
            text: OCRテキスト
            
        Returns:
            出典情報のリスト
        """
        # まずテキストを後処理
        processed_text = self.process_text(text)
        
        sources = []
        lines = processed_text.split('\n')
        
        for line in lines:
            # 出典パターンにマッチする行を探す
            if any(marker in line for marker in self.source_markers):
                # 括弧付き出典（副題も含む）
                # パターン1: 『作品名「副題」』
                bracket_match = re.search(r'[（\(]([^）\)]*『([^』]+(?:「[^」]+」[^』]*)?)』[^）\)]*より)[）\)]', line)
                if bracket_match:
                    content = bracket_match.group(1)
                    title = bracket_match.group(2)
                    
                    # 著者名を抽出
                    author_part = content.split('『')[0].strip()
                    author = self._clean_author_name(author_part)
                    
                    if author and title:
                        sources.append({
                            'author': author,
                            'title': title,
                            'full_text': line,
                            'confidence': 0.9
                        })
                        continue
                
                # 括弧なし出典
                no_bracket_match = re.search(r'([^。\n『]*)\s*『([^』]+)』\s*より', line)
                if no_bracket_match:
                    author = self._clean_author_name(no_bracket_match.group(1))
                    title = no_bracket_match.group(2)
                    
                    if author and title:
                        sources.append({
                            'author': author,
                            'title': title,
                            'full_text': line,
                            'confidence': 0.8
                        })
        
        return sources