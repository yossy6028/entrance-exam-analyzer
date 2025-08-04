#!/usr/bin/env python3
"""
bunkoOCR更新版ワークフロー
自動OCR処理に対応した効率的なスクリプト
"""
import subprocess
import time
from pathlib import Path
from datetime import datetime
import os


class BunkoOCRAutoWorkflow:
    """bunkoOCRの自動処理ワークフロー"""
    
    def __init__(self):
        self.results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.bunko_app = "/Applications/bunkoOCR.app"
        
    def process_pdf(self, pdf_path: str, wait_time: int = 120):
        """PDFを自動処理"""
        
        print("\n" + "="*60)
        print("bunkoOCR 自動処理ワークフロー")
        print("="*60)
        
        if not os.path.exists(pdf_path):
            print(f"❌ エラー: ファイルが見つかりません: {pdf_path}")
            return None
            
        print(f"\n📄 処理対象: {os.path.basename(pdf_path)}")
        print(f"📏 ファイルサイズ: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
        
        # 処理開始前の結果フォルダ数を記録
        before_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
        before_count = len(before_dirs)
        print(f"📁 既存の結果フォルダ数: {before_count}")
        
        # bunkoOCRでファイルを開く
        print("\n🚀 bunkoOCRを起動しています...")
        subprocess.run(["open", "-a", self.bunko_app, pdf_path])
        
        print("\n⏳ 自動OCR処理中...")
        print("   bunkoOCRが自動的にテキスト化を開始します")
        print("   処理時間の目安: 1-3分（ページ数による）")
        print(f"   最大待機時間: {wait_time}秒")
        
        # 新しい結果フォルダを監視
        start_time = time.time()
        check_interval = 5  # 5秒ごとにチェック
        dots = 0
        
        while time.time() - start_time < wait_time:
            current_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
            new_dirs = current_dirs - before_dirs
            
            if new_dirs:
                # 新しいフォルダが見つかった
                latest_dir = max(new_dirs, key=lambda x: x.stat().st_mtime)
                
                # テキストファイルが生成されるまで少し待つ
                print(f"\n✅ 新しい結果フォルダを検出: {latest_dir.name}")
                print("   テキストファイルの生成を待っています...")
                time.sleep(10)
                
                # テキストファイルの存在を確認
                text_files = list(latest_dir.glob("text*.txt"))
                if text_files:
                    print(f"   ✅ {len(text_files)}個のテキストファイルを確認")
                    return self.extract_and_save_results(latest_dir, pdf_path)
                else:
                    print("   ⏳ まだテキストファイルが生成されていません...")
            
            # 進捗表示
            dots = (dots + 1) % 4
            print(f"\r   処理中{'.' * dots}{' ' * (3 - dots)} ({int(time.time() - start_time)}秒経過)", end="", flush=True)
            
            time.sleep(check_interval)
        
        print(f"\n⏱️ タイムアウト ({wait_time}秒)")
        return None
        
    def extract_and_save_results(self, result_dir: Path, original_pdf: str):
        """結果を抽出して保存"""
        
        print(f"\n📤 結果を抽出中...")
        
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
        output_path = Path(output_filename)
        
        # テキストを保存
        final_text = '\n\n'.join(combined_text)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        print(f"\n✅ テキストファイルを保存しました")
        print(f"   ファイル: {output_path}")
        print(f"   総文字数: {total_chars:,} 文字")
        
        # 簡易分析
        self.analyze_content(final_text)
        
        return output_path
        
    def analyze_content(self, text: str):
        """内容を簡易分析"""
        
        print("\n📊 内容分析")
        
        # 設問の検出
        question_patterns = [
            '問一', '問二', '問三', '問四', '問五', '問六', '問七', '問八', '問九', '問十',
            '問１', '問２', '問３', '問４', '問５',
            '［一］', '［二］', '［三］', '［四］', '［五］',
            '【一】', '【二】', '【三】', '【四】', '【五】'
        ]
        
        detected_questions = []
        for pattern in question_patterns:
            if pattern in text:
                count = text.count(pattern)
                detected_questions.append(f"{pattern}({count})")
        
        if detected_questions:
            print(f"   検出された設問: {', '.join(detected_questions[:10])}")
        
        # 出典の検出（簡易）
        if '（' in text and '）' in text:
            # 文末近くの括弧を探す
            last_1000_chars = text[-1000:]
            import re
            sources = re.findall(r'（([^）]+)）', last_1000_chars)
            if sources:
                print(f"   可能性のある出典: {sources[-1][:50]}...")
                
    def show_ocr_results_location(self):
        """OCR結果の場所を案内"""
        
        print("\n📍 bunkoOCRでの結果確認方法:")
        print("1. bunkoOCRのメニューから「OCR結果」を選択")
        print("2. リストの最下部が最新の処理結果")
        print("3. テキストファイルとして保存可能")
        print("\n💡 ヒント: 自動保存されたファイルは以下の場所にあります:")
        print(f"   {self.results_dir}")
        
    def batch_process(self, pdf_files: list):
        """複数ファイルをバッチ処理"""
        
        print(f"\n📦 バッチ処理モード: {len(pdf_files)}ファイル")
        
        results = []
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n\n{'='*60}")
            print(f"ファイル {i}/{len(pdf_files)}")
            print(f"{'='*60}")
            
            result = self.process_pdf(pdf_path)
            results.append({
                'input': pdf_path,
                'output': result,
                'success': result is not None
            })
            
            if i < len(pdf_files):
                print("\n次のファイルを処理しますか？")
                print("続行: Enter / 中止: Ctrl+C")
                try:
                    input()
                except KeyboardInterrupt:
                    print("\n\nバッチ処理を中止しました")
                    break
                    
        # 結果サマリー
        self.show_batch_summary(results)
        
        return results
        
    def show_batch_summary(self, results: list):
        """バッチ処理の結果サマリーを表示"""
        
        print("\n\n" + "="*60)
        print("バッチ処理結果サマリー")
        print("="*60)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n成功: {success_count}/{len(results)} ファイル")
        
        print("\n詳細:")
        for i, r in enumerate(results, 1):
            status = "✅" if r['success'] else "❌"
            print(f"{i}. {status} {os.path.basename(r['input'])}")
            if r['output']:
                print(f"   → {r['output']}")


def main():
    """メイン実行"""
    
    workflow = BunkoOCRAutoWorkflow()
    
    # 渋渋15年度を処理
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    
    print("bunkoOCR 自動処理システム")
    print("\n【重要】bunkoOCRは自動的にOCR処理を開始します")
    print("手動でOCRボタンを押す必要はありません")
    
    # 単一ファイル処理
    result = workflow.process_pdf(pdf_path, wait_time=180)  # 3分待機
    
    if result:
        print("\n" + "="*60)
        print("✅ 処理完了!")
        print("="*60)
        
        # OCR結果の確認方法を案内
        workflow.show_ocr_results_location()
    else:
        print("\n自動検出できませんでした")
        print("bunkoOCRの「OCR結果」メニューから手動で確認してください")


if __name__ == "__main__":
    main()