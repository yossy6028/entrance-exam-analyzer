#!/usr/bin/env python3
"""
DotsOCRを使ったPDF処理スクリプト
flash_attnを使わない設定で実行
"""
import sys
import os
from pathlib import Path
import json
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
import fitz  # PyMuPDF

def process_pdf_with_dots_ocr(pdf_path, output_dir="./output"):
    """
    DotsOCRでPDFを処理（flash_attnを使わない）
    
    Args:
        pdf_path: PDFファイルのパス
        output_dir: 出力ディレクトリ
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"処理開始: {pdf_path.name}")
    print("=" * 70)
    
    # モデルのロード（flash_attnを使わない設定）
    print("モデルをロード中...")
    model_path = "/Users/yoshiikatsuhiko/dots.ocr/weights/DotsOCR"
    
    try:
        # CPUでも動作するように設定を調整
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        # attn_implementationを指定しない（デフォルトを使用）
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
            # flash_attention_2を使わない
        )
        
        if device == "cpu":
            model = model.to(device)
            
        processor = AutoProcessor.from_pretrained(
            model_path, 
            trust_remote_code=True,
            use_fast=True
        )
        
        print("モデルのロード完了")
        
    except Exception as e:
        print(f"モデルロードエラー: {e}")
        print("\n代替方法: flash_attnをインストールするか、vLLMサーバーを使用してください")
        return
    
    # PDFを画像に変換
    print(f"\nPDFを処理中: {pdf_path.name}")
    pdf_document = fitz.open(str(pdf_path))
    
    all_results = []
    
    for page_num in range(len(pdf_document)):
        print(f"ページ {page_num + 1}/{len(pdf_document)} を処理中...")
        
        # ページを画像に変換
        page = pdf_document[page_num]
        mat = fitz.Matrix(150/72, 150/72)  # 150 DPI
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # PILイメージに変換
        import io
        image = Image.open(io.BytesIO(img_data))
        
        # 一時ファイルとして保存
        temp_image_path = output_dir / f"temp_page_{page_num + 1}.png"
        image.save(temp_image_path)
        
        # DotsOCR用のプロンプト
        prompt = """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content.

Requirements:
1. bbox format: [x1, y1, x2, y2]
2. For formulas, use LaTeX format
3. For tables, use HTML format
4. For other text, use Markdown format
5. Sort elements by reading order
6. Output as a single JSON object

Focus on extracting Japanese exam questions, including question numbers, answer choices, and source information."""
        
        # 推論実行
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": str(temp_image_path)},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        try:
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
            
            # デバイスに移動
            if device == "cpu":
                inputs = {k: v.to(device) if hasattr(v, 'to') else v for k, v in inputs.items()}
            
            # 推論
            print(f"  推論実行中...")
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=4096,
                    do_sample=False
                )
            
            # デコード
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in 
                zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            # 結果を保存
            try:
                result = json.loads(output_text)
                all_results.append({
                    "page": page_num + 1,
                    "layout_elements": result
                })
                print(f"  ✅ ページ {page_num + 1} 完了")
            except json.JSONDecodeError:
                print(f"  ⚠️ ページ {page_num + 1}: JSON解析エラー")
                all_results.append({
                    "page": page_num + 1,
                    "raw_text": output_text
                })
                
        except Exception as e:
            print(f"  ❌ ページ {page_num + 1} エラー: {e}")
            all_results.append({
                "page": page_num + 1,
                "error": str(e)
            })
        
        # 一時ファイルを削除
        temp_image_path.unlink(missing_ok=True)
    
    pdf_document.close()
    
    # 結果を保存
    output_file = output_dir / f"{pdf_path.stem}_dots_ocr.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print(f"処理完了: {output_file}")
    
    # テキストを抽出してMarkdownファイルに保存
    markdown_content = f"# {pdf_path.stem}\n\n"
    
    for page_result in all_results:
        markdown_content += f"## ページ {page_result['page']}\n\n"
        
        if "layout_elements" in page_result:
            elements = page_result["layout_elements"]
            if isinstance(elements, dict) and "layout_elements" in elements:
                elements = elements["layout_elements"]
            
            for element in elements if isinstance(elements, list) else []:
                if isinstance(element, dict) and "text" in element:
                    markdown_content += element["text"] + "\n\n"
        elif "raw_text" in page_result:
            markdown_content += page_result["raw_text"] + "\n\n"
    
    markdown_file = output_dir / f"{pdf_path.stem}_dots_ocr.md"
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Markdownファイル: {markdown_file}")
    
    return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DotsOCR PDF処理')
    parser.add_argument('pdf_path', help='処理するPDFファイルのパス')
    parser.add_argument('--output', default='./output', help='出力ディレクトリ')
    
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"エラー: ファイルが見つかりません: {args.pdf_path}")
        sys.exit(1)
    
    process_pdf_with_dots_ocr(args.pdf_path, args.output)