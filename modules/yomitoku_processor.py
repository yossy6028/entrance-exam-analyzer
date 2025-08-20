"""
Yomitoku OCR処理モジュール
日本語特化の高精度OCRライブラリを使用したテキスト抽出
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import subprocess
import tempfile
from PIL import Image
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class YomitokuProcessor:
    """Yomitoku OCRを使用したドキュメント処理クラス"""
    
    def __init__(self, use_lite: bool = False, device: str = "cpu"):
        """
        初期化
        
        Args:
            use_lite: 軽量モデルを使用するか
            device: 使用デバイス（cpu/cuda）
        """
        self.use_lite = use_lite
        self.device = device
        
        # GPUが利用可能か確認
        try:
            import torch
            if torch.cuda.is_available() and device == "cuda":
                self.device = "cuda"
                logger.info(f"GPU使用: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("CPU使用")
        except ImportError:
            self.device = "cpu"
            
    def process_pdf(self, pdf_path: Path, 
                   output_format: str = "md",
                   output_dir: Optional[Path] = None,
                   extract_figures: bool = True,
                   visualize: bool = False) -> Dict[str, Any]:
        """
        PDFファイルをYomitokuで処理
        
        Args:
            pdf_path: PDFファイルのパス
            output_format: 出力形式（json/csv/html/md）
            output_dir: 出力ディレクトリ
            extract_figures: 図表を抽出するか
            visualize: 結果を可視化するか
            
        Returns:
            処理結果の辞書
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
            
        # 出力ディレクトリの準備
        if output_dir is None:
            output_dir = Path("yomitoku_output")
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Yomitoku処理開始: {pdf_path.name}")
        
        # PDFを画像に変換
        images = self._convert_pdf_to_images(pdf_path, output_dir)
        
        # 各ページを処理
        results = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'total_pages': len(images),
            'pages': [],
            'full_text': ''
        }
        
        all_text = []
        
        for i, image_path in enumerate(images, 1):
            logger.info(f"ページ {i}/{len(images)} を処理中...")
            
            # Yomitokuで処理
            page_result = self._process_image(
                image_path, 
                output_format,
                output_dir,
                extract_figures,
                visualize
            )
            
            results['pages'].append({
                'page_number': i,
                'text': page_result.get('text', ''),
                'layout': page_result.get('layout', {}),
                'tables': page_result.get('tables', []),
                'figures': page_result.get('figures', [])
            })
            
            all_text.append(page_result.get('text', ''))
            
        results['full_text'] = '\n\n'.join(all_text)
        
        # 入試問題特有の構造を検出
        results['exam_structure'] = self._extract_exam_structure(results['full_text'])
        
        # 高精度な出典情報抽出を適用
        try:
            from .enhanced_source_extractor import EnhancedSourceExtractor
            enhancer = EnhancedSourceExtractor()
            results = enhancer.enhance_yomitoku_results(results)
            logger.info("高精度出典抽出を適用しました")
        except Exception as e:
            logger.warning(f"出典抽出エラー: {e}")
        
        logger.info(f"処理完了: {pdf_path.name}")
        
        return results
        
    def _convert_pdf_to_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        PDFを画像に変換
        
        Args:
            pdf_path: PDFファイルのパス
            output_dir: 出力ディレクトリ
            
        Returns:
            画像ファイルパスのリスト
        """
        pdf_document = fitz.open(str(pdf_path))
        image_paths = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # 150 DPIで変換（Yomitoku推奨は720px以上）
            mat = fitz.Matrix(2.0, 2.0)  # 約150 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # 画像として保存
            image_path = output_dir / f"page_{page_num + 1:03d}.png"
            pix.save(str(image_path))
            image_paths.append(image_path)
            
        pdf_document.close()
        
        return image_paths
        
    def _process_image(self, image_path: Path,
                      output_format: str,
                      output_dir: Path,
                      extract_figures: bool,
                      visualize: bool) -> Dict[str, Any]:
        """
        画像をYomitokuで処理
        
        Args:
            image_path: 画像ファイルのパス
            output_format: 出力形式
            output_dir: 出力ディレクトリ
            extract_figures: 図表を抽出するか
            visualize: 可視化するか
            
        Returns:
            処理結果
        """
        # Yomitokuコマンドを構築
        cmd = [
            "yomitoku",
            str(image_path),
            "-f", output_format,
            "-o", str(output_dir),
            "-d", self.device
        ]
        
        if self.use_lite:
            cmd.append("--lite")
            
        if extract_figures:
            cmd.append("--figure")
            
        if visualize:
            cmd.append("-v")
            
        # 実行
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 出力ファイルを読み込み
            output_file = self._find_output_file(output_dir, image_path.stem, output_format)
            
            if output_file and output_file.exists():
                return self._parse_output(output_file, output_format)
            else:
                logger.warning(f"出力ファイルが見つかりません: {image_path.name}")
                return {'text': '', 'error': 'Output file not found'}
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Yomitoku処理エラー: {e.stderr}")
            return {'text': '', 'error': str(e)}
            
    def _find_output_file(self, output_dir: Path, stem: str, format: str) -> Optional[Path]:
        """
        出力ファイルを探す
        
        Args:
            output_dir: 出力ディレクトリ
            stem: ファイル名のステム
            format: 出力形式
            
        Returns:
            出力ファイルのパス
        """
        extensions = {
            'json': '.json',
            'csv': '.csv',
            'html': '.html',
            'md': '.md'
        }
        
        ext = extensions.get(format, '.txt')
        
        # Yomitokuの出力ファイル名パターンを試す
        patterns = [
            output_dir / f"{stem}{ext}",
            output_dir / f"{stem}_ocr{ext}",
            output_dir / f"ocr_{stem}{ext}"
        ]
        
        for pattern in patterns:
            if pattern.exists():
                return pattern
                
        # 最新のファイルを探す
        files = list(output_dir.glob(f"*{ext}"))
        if files:
            return max(files, key=lambda f: f.stat().st_mtime)
            
        return None
        
    def _parse_output(self, output_file: Path, format: str) -> Dict[str, Any]:
        """
        出力ファイルを解析
        
        Args:
            output_file: 出力ファイルのパス
            format: 出力形式
            
        Returns:
            解析結果
        """
        result = {'text': '', 'layout': {}, 'tables': [], 'figures': []}
        
        if format == 'json':
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # JSONから情報を抽出
            if isinstance(data, dict):
                result['text'] = data.get('text', '')
                result['layout'] = data.get('layout', {})
                result['tables'] = data.get('tables', [])
                result['figures'] = data.get('figures', [])
                
        elif format == 'md':
            with open(output_file, 'r', encoding='utf-8') as f:
                result['text'] = f.read()
                
        elif format == 'html':
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            # HTMLからテキストを抽出（簡易版）
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            result['text'] = text
            
        elif format == 'csv':
            import csv
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            result['text'] = '\n'.join([','.join(row) for row in rows])
            result['tables'] = [rows]
            
        return result
        
    def _extract_exam_structure(self, text: str) -> Dict[str, Any]:
        """
        入試問題の構造を抽出
        
        Args:
            text: 抽出されたテキスト
            
        Returns:
            入試問題構造
        """
        import re
        
        structure = {
            'has_multiple_sections': False,
            'sections': [],
            'question_count': 0,
            'has_answer_choices': False,
            'themes': [],
            'source_info': {}
        }
        
        # 大問を検出
        section_patterns = [
            r'[一二三四五六七八九十][\s、．]',
            r'第[一二三四五六七八九十]問',
            r'問題[１２３４５６７８９]'
        ]
        
        for pattern in section_patterns:
            sections = re.findall(pattern, text)
            if sections:
                structure['has_multiple_sections'] = True
                structure['sections'].extend(sections)
                break
                
        # 問題番号を検出
        question_patterns = [
            r'問[一二三四五六七八九十０-９]+',
            r'[（(][一二三四五六七八九十０-９]+[）)]',
            r'[①②③④⑤⑥⑦⑧⑨⑩]'
        ]
        
        for pattern in question_patterns:
            questions = re.findall(pattern, text)
            structure['question_count'] += len(questions)
            
        # 選択肢を検出
        choice_patterns = [
            r'[アイウエオカキクケコ][\s、．]',
            r'[あいうえおかきくけこ][\s、．]',
            r'[ＡＢＣＤＥ][\s、．]',
            r'[1-5][\s、．]'
        ]
        
        for pattern in choice_patterns:
            if re.search(pattern, text):
                structure['has_answer_choices'] = True
                break
                
        # 出典情報を抽出
        source_patterns = [
            r'『([^』]+)』',  # 作品名
            r'「([^」]+)」より',  # 出典
            r'（([^）]+)著）',  # 著者
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if '著' in pattern:
                    structure['source_info']['author'] = matches[0]
                else:
                    structure['source_info']['title'] = matches[0]
                    
        # テーマを推定
        theme_keywords = {
            '人間関係・成長': ['友', '家族', '成長', '心', '思い'],
            '自然・環境': ['自然', '環境', '動物', '植物', '季節'],
            '社会・文化': ['社会', '文化', '歴史', '伝統', '現代'],
            '科学・技術': ['科学', '技術', '実験', '研究', '発見']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                structure['themes'].append(theme)
                
        return structure
        
    def process_with_fallback(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Yomitokuを試み、失敗した場合はGoogle Cloud Visionにフォールバック
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            処理結果
        """
        try:
            # まずYomitokuを試みる
            return self.process_pdf(pdf_path)
        except Exception as e:
            logger.warning(f"Yomitoku処理失敗: {e}")
            
            # Google Cloud Vision APIにフォールバック
            logger.info("Google Cloud Vision APIにフォールバックします")
            from .pdf_ocr_processor import PDFOCRProcessor
            fallback_processor = PDFOCRProcessor()
            return fallback_processor.process_pdf(pdf_path)