#!/usr/bin/env python3
"""
bunkoOCR設定画面の分析と最適設定の提案
"""

def analyze_bunko_ocr_settings():
    """bunkoOCRの設定項目を分析"""
    
    print("=== bunkoOCR 設定分析 ===\n")
    
    print("【オプション設定】")
    print("1. タイルの重なり: 0.25")
    print("   - OCR処理時の画像タイル分割の重複率")
    print("   - 高い値で文字の分断を防ぐ")
    print()
    
    print("2. 2pass OCR: ON")
    print("   - 2回のOCR処理で精度向上")
    print("   - 1回目で全体構造を把握、2回目で詳細認識")
    print()
    
    print("3. 2passの縮小率: x 0.20")
    print("   - 1回目のパスでの画像縮小率")
    print("   - 高速な全体構造把握")
    print()
    
    print("4. PDF dpi: 300.0 dpi")
    print("   - PDFラスタライズ時の解像度")
    print("   - 300dpiは印刷品質相当で最適")
    print()
    
    print("5. Transformer設定:")
    print("   - アーカイブ内名前でソート: ON")
    print("   - ファイル追加時名前でソート: ON")
    print("   - Transformerによる無補正: ON")
    print("   - decoder pad: 10")
    print("   → 最新のTransformerモデルで高精度認識")
    
    print("\n【処理環境設定】")
    print("- 見開き2ページとして処理: ON")
    print("  → 入試問題の見開きページに最適")
    print("- ブロックの字下げを適用: OFF")
    print("  → 縦書きテキストの正確な保持")
    
    print("\n【検出閾値設定】")
    settings = {
        "文字検出閾値": 0.350,
        "空白検出閾値": 10,
        "ゴミと文字の閾値": 0.00,
        "ルビ閾値": 0.250,
        "親文字閾値": 0.750,
        "傍点閾値": 0.250,
        "文字空け閾値": 0.250,
        "領域IOU閾値": 0.50,
        "領域重複閾値": 0.50,
        "数式詞の閾値": 0.60
    }
    
    for key, value in settings.items():
        print(f"- {key}: {value}")
    
    print("\n【文の検索設定】")
    print("- 行の検出閾値: 0.400")
    print("- 行の切断検出閾値: 0.100 x 3")
    print("- 連結する行間隔: 1.50文字")
    print("- 連結する行の許容文字サイズ差: x 0.50")
    
    print("\n【読み上げ設定】")
    print("- 読み上げ音声: Kyoko（日本語）")
    print("- playbackで再生: ON")
    
    print("\n【除外オプション】")
    print("- 日本語の前の空白を半角から全角に変換: ON")
    print("- EM DASH/HORIZONTAL BARに揃える: ON")
    print("- 句点（。）の後の空白を除去: ON")
    print("- 読点（、）の後の空白を除去: ON")
    print("- カギ括弧の前後の空白を除去: ON")
    print("- 二重カギ括弧の前後の空白を除去: ON")
    print("- 半角と全角の混ざった英数字を修正: ON")
    print("- 全角文字に揃える: ON")
    print("- 漢数字に混ざった〇を零に修正: ON")


def recommend_optimal_settings():
    """入試問題分析に最適な設定を提案"""
    
    print("\n\n=== 入試問題分析に最適な設定 ===\n")
    
    print("【推奨設定】")
    
    print("\n1. 基本設定:")
    print("   - 2pass OCR: ON（必須）")
    print("   - PDF dpi: 300以上")
    print("   - Transformerによる無補正: ON")
    
    print("\n2. 縦書き対応:")
    print("   - 見開き2ページとして処理: ON")
    print("   - ブロックの字下げを適用: OFF")
    print("   - 文字検出閾値: 0.350（デフォルト）")
    
    print("\n3. 出力形式:")
    print("   - JSONファイル編集のボタンを表示: ON")
    print("   - 用紙解析ボタンを表示: ON")
    print("   - 全ページ表示をデフォルト: ON")
    
    print("\n4. 後処理:")
    print("   - すべての除外オプション: ON")
    print("   - 特に重要:")
    print("     * 日本語の前の空白を半角から全角に変換")
    print("     * カギ括弧の前後の空白を除去")
    print("     * 全角文字に揃える")


def create_automation_script():
    """bunkoOCR連携の自動化スクリプト"""
    
    print("\n\n=== bunkoOCR自動化スクリプト ===\n")
    
    print("""
import subprocess
import time
import os
from pathlib import Path
import json

class BunkoOCRAutomation:
    '''bunkoOCRとの連携を自動化'''
    
    def __init__(self):
        self.results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.bunko_app = "/Applications/bunkoOCR.app"
    
    def process_pdf(self, pdf_path: str, wait_time: int = 60):
        '''PDFをbunkoOCRで処理'''
        
        # 処理前の結果フォルダをチェック
        before_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
        
        # bunkoOCRでPDFを開く
        print(f"bunkoOCRでPDFを開いています: {pdf_path}")
        subprocess.run(["open", "-a", self.bunko_app, pdf_path])
        
        print("bunkoOCRが起動しました。以下を実行してください:")
        print("1. OCR処理を開始（画面下のボタン）")
        print("2. 処理完了まで待機")
        print(f"\\n{wait_time}秒間、処理完了を待ちます...")
        
        # 新しい結果フォルダを監視
        start_time = time.time()
        while time.time() - start_time < wait_time:
            current_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
            new_dirs = current_dirs - before_dirs
            
            if new_dirs:
                # 最新の結果フォルダ
                latest_dir = max(new_dirs, key=lambda x: x.stat().st_mtime)
                print(f"\\n新しい結果が見つかりました: {latest_dir.name}")
                return self.extract_text_from_result(latest_dir)
            
            time.sleep(2)
        
        print("\\nタイムアウト: 結果が見つかりませんでした")
        return None
    
    def extract_text_from_result(self, result_dir: Path) -> str:
        '''結果フォルダからテキストを抽出'''
        
        # text*.txtファイルを番号順に読み込み
        text_files = sorted(result_dir.glob("text*.txt"), 
                          key=lambda x: int(x.stem.replace('text', '')))
        
        combined_text = []
        for text_file in text_files:
            with open(text_file, 'r', encoding='utf-8') as f:
                combined_text.append(f.read())
        
        # result*.jsonから構造情報も取得
        json_files = sorted(result_dir.glob("result*.json"))
        structure_info = []
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                structure_info.append(data)
        
        return {
            'text': '\\n'.join(combined_text),
            'structure': structure_info,
            'result_dir': str(result_dir)
        }
    
    def analyze_entrance_exam(self, pdf_path: str):
        '''入試問題を分析'''
        
        # bunkoOCRで処理
        result = self.process_pdf(pdf_path, wait_time=120)
        
        if result:
            # テキストを保存
            output_path = f"{Path(pdf_path).stem}_bunko.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            print(f"\\nOCR結果を保存しました: {output_path}")
            print(f"文字数: {len(result['text'])}文字")
            
            # 構造情報から縦書き判定
            if result['structure']:
                vertical_blocks = 0
                total_blocks = 0
                
                for page_data in result['structure']:
                    if 'block' in page_data:
                        for block in page_data['block']:
                            total_blocks += 1
                            if block.get('vertical', 0) == 1:
                                vertical_blocks += 1
                
                if total_blocks > 0:
                    vertical_ratio = vertical_blocks / total_blocks
                    print(f"\\n縦書きブロック率: {vertical_ratio:.1%}")
                    
                    if vertical_ratio > 0.5:
                        print("→ 縦書き文書として検出されました")
            
            return result
        
        return None


# 使用例
if __name__ == "__main__":
    automation = BunkoOCRAutomation()
    
    # 渋渋15年度を処理
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    result = automation.analyze_entrance_exam(pdf_path)
""")


def main():
    """メイン実行"""
    
    analyze_bunko_ocr_settings()
    recommend_optimal_settings()
    create_automation_script()
    
    print("\n\n【まとめ】")
    print("bunkoOCRは以下の特徴を持つ高度なOCRアプリです:")
    print("1. Transformerベースの最新AI技術")
    print("2. 日本語縦書きに特化した設定")
    print("3. 2pass処理による高精度認識")
    print("4. 詳細な閾値調整が可能")
    print("5. JSON形式での構造化データ出力")
    
    print("\n入試問題分析には最適なツールです。")
    print("上記の自動化スクリプトで効率的な処理が可能です。")


if __name__ == "__main__":
    main()