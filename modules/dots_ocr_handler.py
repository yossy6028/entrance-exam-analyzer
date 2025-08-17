"""
DotsOCR処理モジュール
dots.ocrを使用した多言語ドキュメントレイアウト解析とOCR処理
"""
import logging
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import tempfile

logger = logging.getLogger(__name__)


class DotsOCRHandler:
    """dots.ocrを使用したOCR処理クラス"""
    
    def __init__(self, model_path: str = "./weights/DotsOCR", use_gpu: bool = True):
        """
        初期化
        
        Args:
            model_path: DotsOCRモデルのパス
            use_gpu: GPUを使用するか
        """
        self.model_path = Path(model_path)
        self.use_gpu = use_gpu
        self.parser_script = None
        
        # dots.ocrがインストールされているか確認
        self._check_installation()
        
    def _check_installation(self):
        """dots.ocrのインストール状態を確認"""
        try:
            # dots_ocrパッケージのインポートテスト
            import dots_ocr.parser
            self.parser_script = Path(dots_ocr.parser.__file__).parent / "parser.py"
            logger.info(f"dots_ocr found at: {self.parser_script}")
        except ImportError:
            logger.warning("dots_ocr package not found. Using command-line interface.")
            # コマンドラインインターフェースを使用
            self.parser_script = Path("dots_ocr/parser.py")
            
    def process_pdf(self, pdf_path: Path, num_threads: int = 4) -> Dict[str, Any]:
        """
        PDFファイルをDotsOCRで処理
        
        Args:
            pdf_path: PDFファイルのパス
            num_threads: 並列処理のスレッド数
            
        Returns:
            OCR結果の辞書
        """
        try:
            logger.info(f"DotsOCR処理開始: {pdf_path}")
            
            # Pathオブジェクトに変換
            pdf_path = Path(pdf_path) if not isinstance(pdf_path, Path) else pdf_path
            
            # 出力ディレクトリを作成
            output_dir = pdf_path.parent / f"{pdf_path.stem}_dots_ocr_output"
            output_dir.mkdir(exist_ok=True)
            
            # コマンドラインでDotsOCRを実行
            result = self._run_dots_ocr_cli(pdf_path, output_dir, num_threads)
            
            # 結果を解析
            parsed_result = self._parse_results(output_dir, pdf_path)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"DotsOCR処理エラー: {e}")
            raise
            
    def _run_dots_ocr_cli(self, pdf_path: Path, output_dir: Path, num_threads: int) -> subprocess.CompletedProcess:
        """
        コマンドラインインターフェースでDotsOCRを実行
        
        Args:
            pdf_path: PDFファイルのパス
            output_dir: 出力ディレクトリ
            num_threads: スレッド数
            
        Returns:
            実行結果
        """
        cmd = [
            "python3",
            str(self.parser_script),
            str(pdf_path),
            "--num_thread", str(num_threads),
            "--output_dir", str(output_dir)
        ]
        
        logger.info(f"実行コマンド: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"DotsOCR実行エラー: {result.stderr}")
            raise RuntimeError(f"DotsOCR実行失敗: {result.stderr}")
            
        return result
        
    def process_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        画像をDotsOCRで処理（Pythonインターフェース使用）
        
        Args:
            image: PIL Image
            
        Returns:
            OCR結果の辞書
        """
        try:
            # 一時ファイルに画像を保存
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                image.save(temp_file.name, format='PNG')
                temp_path = Path(temp_file.name)
                
            # DotsOCRで処理
            result = self._process_with_model(temp_path)
            
            # 一時ファイルを削除
            temp_path.unlink()
            
            return result
            
        except Exception as e:
            logger.error(f"画像処理エラー: {e}")
            raise
            
    def _process_with_model(self, image_path: Path) -> Dict[str, Any]:
        """
        モデルを使用して画像を処理（Pythonインターフェース）
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            処理結果
        """
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
            from qwen_vl_utils import process_vision_info
            
            # モデルとプロセッサーをロード
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                attn_implementation="flash_attention_2",
                torch_dtype=torch.bfloat16,
                device_map="auto" if self.use_gpu else "cpu",
                trust_remote_code=True
            )
            processor = AutoProcessor.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # プロンプトを作成
            prompt = self._create_prompt()
            
            # メッセージを作成
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": str(image_path)},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # プロセッサーで入力を準備
            text = processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            # 推論実行
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs.to(model.device),
                    max_new_tokens=8192
                )
                
            # 結果をデコード
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in 
                zip(inputs.input_ids, generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            # JSONとして解析
            result = json.loads(output_text)
            
            return self._format_result(result)
            
        except ImportError as e:
            logger.error(f"必要なライブラリが見つかりません: {e}")
            logger.info("コマンドラインインターフェースを使用してください")
            raise
            
    def _create_prompt(self) -> str:
        """DotsOCR用のプロンプトを作成"""
        return """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content. 
        
        Requirements:
        1. Use [x1, y1, x2, y2] format for bbox
        2. For formulas, use LaTeX format
        3. For tables, use HTML format
        4. For other text, use Markdown format
        5. Sort elements by reading order
        6. Output as a single JSON object
        
        Focus on extracting Japanese exam questions, including:
        - Question numbers and content
        - Answer choices
        - Source information (author, title)
        - Any tables or formulas"""
        
    def _parse_results(self, output_dir: Path, pdf_path: Path) -> Dict[str, Any]:
        """
        DotsOCRの出力結果を解析
        
        Args:
            output_dir: 出力ディレクトリ
            pdf_path: 元のPDFファイルパス
            
        Returns:
            解析結果
        """
        # JSONファイルを読み込み
        json_files = list(output_dir.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"JSONファイルが見つかりません: {output_dir}")
            
        results = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'pages': [],
            'full_text': '',
            'layout_elements': []
        }
        
        all_text = []
        
        for json_file in sorted(json_files):
            with open(json_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                
            # ページ情報を抽出
            page_result = self._extract_page_info(page_data)
            results['pages'].append(page_result)
            
            # テキストを結合
            all_text.append(page_result['text'])
            
            # レイアウト要素を追加
            results['layout_elements'].extend(page_result['elements'])
            
        results['full_text'] = '\n\n'.join(all_text)
        results['total_pages'] = len(results['pages'])
        
        # 入試問題特有の情報を抽出
        results['exam_structure'] = self._extract_exam_structure(results)
        
        return results
        
    def _extract_page_info(self, page_data: Dict) -> Dict[str, Any]:
        """
        ページデータから情報を抽出
        
        Args:
            page_data: DotsOCRの出力データ
            
        Returns:
            ページ情報
        """
        page_info = {
            'text': '',
            'elements': [],
            'tables': [],
            'formulas': []
        }
        
        text_parts = []
        
        # レイアウト要素を処理
        for element in page_data.get('layout_elements', []):
            element_type = element.get('category', '')
            content = element.get('text', '')
            bbox = element.get('bbox', [])
            
            element_info = {
                'type': element_type,
                'bbox': bbox,
                'content': content
            }
            
            page_info['elements'].append(element_info)
            
            # タイプ別に処理
            if element_type == 'Table':
                page_info['tables'].append(content)
            elif element_type == 'Formula':
                page_info['formulas'].append(content)
            else:
                text_parts.append(content)
                
        page_info['text'] = '\n'.join(text_parts)
        
        return page_info
        
    def _extract_exam_structure(self, results: Dict) -> Dict[str, Any]:
        """
        入試問題の構造を抽出
        
        Args:
            results: OCR結果
            
        Returns:
            入試問題構造
        """
        structure = {
            'has_multiple_sections': False,
            'sections': [],
            'question_count': 0,
            'has_answer_choices': False,
            'source_info': {},
            'themes': []
        }
        
        full_text = results['full_text']
        
        # 大問を検出
        import re
        section_pattern = r'[一二三四五六七八九十][\s、．]'
        sections = re.findall(section_pattern, full_text)
        if sections:
            structure['has_multiple_sections'] = True
            structure['sections'] = sections
            
        # 問題番号を検出
        question_patterns = [
            r'問[一二三四五六七八九十０-９]+',
            r'[（(][一二三四五六七八九十０-９]+[）)]',
            r'[①②③④⑤⑥⑦⑧⑨⑩]'
        ]
        
        for pattern in question_patterns:
            questions = re.findall(pattern, full_text)
            structure['question_count'] += len(questions)
            
        # 選択肢を検出
        choice_patterns = [
            r'[アイウエオ][\s、．]',
            r'[あいうえお][\s、．]',
            r'[ＡＢＣＤＥ][\s、．]'
        ]
        
        for pattern in choice_patterns:
            if re.search(pattern, full_text):
                structure['has_answer_choices'] = True
                break
                
        # 出典情報を抽出（表やフォーマット化されたテキストから）
        for element in results['layout_elements']:
            if element['type'] in ['Caption', 'Footnote']:
                content = element['content']
                if '著' in content or '作' in content:
                    structure['source_info']['author'] = content
                elif '『' in content and '』' in content:
                    structure['source_info']['title'] = content
                    
        return structure
        
    def _format_result(self, raw_result: Dict) -> Dict[str, Any]:
        """
        生の結果を整形
        
        Args:
            raw_result: 生のOCR結果
            
        Returns:
            整形された結果
        """
        formatted = {
            'layout_elements': raw_result.get('layout_elements', []),
            'text': '',
            'metadata': {
                'language': 'ja',
                'document_type': 'exam_paper'
            }
        }
        
        # テキストを抽出して結合
        text_parts = []
        for element in formatted['layout_elements']:
            if element.get('text'):
                text_parts.append(element['text'])
                
        formatted['text'] = '\n'.join(text_parts)
        
        return formatted