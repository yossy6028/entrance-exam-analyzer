#!/usr/bin/env python3
"""
bunkoOCR実用ワークフロー
手動操作と自動化を組み合わせた効率的な処理
"""
import subprocess
import time
import os
from pathlib import Path
import json
from datetime import datetime
import shutil


class BunkoOCRWorkflow:
    """bunkoOCRの実用的なワークフロー"""
    
    def __init__(self):
        self.results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.bunko_app = "/Applications/bunkoOCR.app"
        self.output_dir = Path("bunko_ocr_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def step1_launch_with_file(self, pdf_path: str):
        """ステップ1: bunkoOCRでファイルを開く"""
        
        print("\n" + "="*60)
        print("bunkoOCR ワークフロー開始")
        print("="*60)
        
        if not os.path.exists(pdf_path):
            print(f"❌ エラー: ファイルが見つかりません: {pdf_path}")
            return False
            
        print(f"\n📄 処理対象: {os.path.basename(pdf_path)}")
        print(f"📏 ファイルサイズ: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
        
        # 現在の結果フォルダ数を記録
        before_count = len(list(self.results_dir.iterdir())) if self.results_dir.exists() else 0
        print(f"📁 既存の結果フォルダ数: {before_count}")
        
        # bunkoOCRでファイルを開く
        print("\n🚀 bunkoOCRを起動しています...")
        subprocess.run(["open", "-a", self.bunko_app, pdf_path])
        
        print("\n" + "📝 手動操作ガイド " + "="*40)
        print("1. bunkoOCRが起動します")
        print("2. ファイルが自動的に読み込まれます")
        print("3. 画面下部のOCRボタンをクリック")
        print("4. 処理が完了するまで待ちます")
        print("5. 完了後、このスクリプトに戻ってEnterキーを押してください")
        print("="*60)
        
        return True
        
    def step2_wait_for_completion(self):
        """ステップ2: 処理完了を待つ"""
        
        print("\n⏳ OCR処理中...")
        input("処理が完了したらEnterキーを押してください: ")
        
        return True
        
    def step3_find_latest_result(self) -> Path:
        """ステップ3: 最新の結果フォルダを見つける"""
        
        print("\n🔍 処理結果を検索中...")
        
        if not self.results_dir.exists():
            print("❌ 結果フォルダが見つかりません")
            return None
            
        # 全ての結果フォルダを取得
        result_dirs = [d for d in self.results_dir.iterdir() if d.is_dir()]
        
        if not result_dirs:
            print("❌ 結果が見つかりません")
            return None
            
        # 最新のフォルダを特定
        latest_dir = max(result_dirs, key=lambda x: x.stat().st_mtime)
        
        # 作成時刻を確認
        mtime = datetime.fromtimestamp(latest_dir.stat().st_mtime)
        time_diff = (datetime.now() - mtime).total_seconds()
        
        if time_diff < 600:  # 10分以内
            print(f"✅ 最新の結果を発見: {latest_dir.name}")
            print(f"   作成時刻: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            return latest_dir
        else:
            print(f"⚠️  最新のフォルダが古い可能性があります")
            print(f"   フォルダ: {latest_dir.name}")
            print(f"   作成時刻: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            confirm = input("このフォルダを使用しますか？ (y/n): ")
            if confirm.lower() == 'y':
                return latest_dir
            else:
                return None
                
    def step4_extract_and_save(self, result_dir: Path, original_pdf: str):
        """ステップ4: テキストを抽出して保存"""
        
        print(f"\n📤 結果を抽出中: {result_dir.name}")
        
        # テキストファイルを読み込み
        text_files = sorted(result_dir.glob("text*.txt"), 
                          key=lambda x: int(x.stem.replace('text', '')))
        
        if not text_files:
            print("❌ テキストファイルが見つかりません")
            return None
            
        print(f"📄 テキストファイル数: {len(text_files)}")
        
        # テキストを結合
        combined_text = []
        total_chars = 0
        
        for i, text_file in enumerate(text_files):
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_text.append(f"===== ページ {i+1} =====\n{content}")
                total_chars += len(content)
                print(f"   ページ {i+1}: {len(content):,} 文字")
        
        # 出力ファイル名を生成
        base_name = Path(original_pdf).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_name}_bunko_{timestamp}.txt"
        output_path = self.output_dir / output_filename
        
        # テキストを保存
        final_text = '\n\n'.join(combined_text)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        print(f"\n✅ テキストファイルを保存しました")
        print(f"   ファイル: {output_path}")
        print(f"   総文字数: {total_chars:,} 文字")
        
        # JSON構造情報も保存
        json_files = list(result_dir.glob("result*.json"))
        if json_files:
            json_output = self.output_dir / f"{base_name}_bunko_{timestamp}.json"
            
            all_json_data = []
            for json_file in sorted(json_files):
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_json_data.append(json.load(f))
            
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(all_json_data, f, ensure_ascii=False, indent=2)
            
            print(f"   構造情報: {json_output}")
        
        return output_path
        
    def analyze_ocr_quality(self, text_path: Path):
        """OCR品質を分析"""
        
        print("\n📊 OCR品質分析")
        
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 基本統計
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        print(f"   総行数: {len(lines):,}")
        print(f"   非空行数: {len(non_empty_lines):,}")
        print(f"   平均行長: {sum(len(line) for line in non_empty_lines) / len(non_empty_lines):.1f} 文字")
        
        # 縦書き判定（簡易）
        vertical_indicators = ['。', '、', '」', '』']
        vertical_count = sum(text.count(char) for char in vertical_indicators)
        
        if vertical_count > len(text) / 50:
            print("   文書タイプ: 縦書き日本語文書と推定")
        else:
            print("   文書タイプ: 横書きまたは混在")
        
        # 問題検出（入試問題用）
        question_patterns = [
            '問一', '問二', '問三', '問四', '問五',
            '問１', '問２', '問３', '問４', '問５',
            '［一］', '［二］', '［三］', '［四］', '［五］'
        ]
        
        detected_questions = []
        for pattern in question_patterns:
            if pattern in text:
                detected_questions.append(pattern)
        
        if detected_questions:
            print(f"   検出された設問: {', '.join(detected_questions[:10])}")
        
    def run_complete_workflow(self, pdf_path: str):
        """完全なワークフローを実行"""
        
        # ステップ1: ファイルを開く
        if not self.step1_launch_with_file(pdf_path):
            return None
            
        # ステップ2: 処理完了を待つ
        self.step2_wait_for_completion()
        
        # ステップ3: 結果を見つける
        result_dir = self.step3_find_latest_result()
        if not result_dir:
            print("\n❌ 結果が見つかりませんでした")
            return None
            
        # ステップ4: 抽出して保存
        output_path = self.step4_extract_and_save(result_dir, pdf_path)
        
        if output_path:
            # 品質分析
            self.analyze_ocr_quality(output_path)
            
            print("\n" + "="*60)
            print("✅ bunkoOCRワークフロー完了!")
            print("="*60)
            
            return output_path
            
        return None
        
    def batch_process(self, pdf_files: list):
        """複数ファイルのバッチ処理"""
        
        print(f"\n📦 バッチ処理モード: {len(pdf_files)}ファイル")
        
        results = []
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n\n{'='*60}")
            print(f"ファイル {i}/{len(pdf_files)}")
            print(f"{'='*60}")
            
            result = self.run_complete_workflow(pdf_path)
            results.append({
                'input': pdf_path,
                'output': result,
                'success': result is not None
            })
            
            if i < len(pdf_files):
                print("\n次のファイルに進みますか？")
                if input("続行する場合はEnterキーを押してください (中止: n): ").lower() == 'n':
                    break
                    
        # 結果サマリー
        print("\n\n" + "="*60)
        print("バッチ処理結果")
        print("="*60)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"成功: {success_count}/{len(results)}")
        
        for r in results:
            status = "✅" if r['success'] else "❌"
            print(f"{status} {os.path.basename(r['input'])}")
            if r['output']:
                print(f"   → {r['output']}")
                
        return results


def main():
    """メイン実行"""
    
    workflow = BunkoOCRWorkflow()
    
    # 単一ファイル処理
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    
    print("bunkoOCR 実用ワークフロー")
    print("\n選択してください:")
    print("1. 単一ファイル処理")
    print("2. バッチ処理（複数ファイル）")
    
    choice = input("\n選択 (1/2): ").strip()
    
    if choice == "2":
        # バッチ処理
        pdf_dir = Path("/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋")
        pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # 最初の3ファイル
        
        if pdf_files:
            print(f"\n見つかったPDFファイル:")
            for f in pdf_files:
                print(f"  - {f.name}")
            
            workflow.batch_process([str(f) for f in pdf_files])
        else:
            print("PDFファイルが見つかりません")
    else:
        # 単一ファイル処理
        workflow.run_complete_workflow(pdf_path)


if __name__ == "__main__":
    main()