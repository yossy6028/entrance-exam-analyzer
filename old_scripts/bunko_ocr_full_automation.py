#!/usr/bin/env python3
"""
bunkoOCRの完全自動化スクリプト
AppleScript、キーボード操作、URLスキームなど複数の方法を試す
"""
import subprocess
import time
import os
from pathlib import Path
import json
import sys


class BunkoOCRFullAutomation:
    """bunkoOCRの完全自動化クラス"""
    
    def __init__(self):
        self.results_dir = Path.home() / "Library/Mobile Documents/iCloud~info~lithium03~bunkoOCR/Documents/Results"
        self.bunko_app = "/Applications/bunkoOCR.app"
        
    def method1_applescript(self, pdf_path: str):
        """方法1: AppleScriptを使用した自動化"""
        
        print("\n=== 方法1: AppleScript自動化 ===")
        
        applescript = f'''
        tell application "bunkoOCR"
            activate
            delay 1
            
            -- ファイルを開く
            open POSIX file "{pdf_path}"
            delay 2
            
            -- OCR処理を開始（キーボードショートカットやメニュー操作）
            tell application "System Events"
                tell process "bunkoOCR"
                    -- OCRボタンをクリック（座標は調整が必要）
                    -- click at {{500, 700}}
                    
                    -- またはキーボードショートカット
                    keystroke "o" using command down
                end tell
            end tell
        end tell
        '''
        
        try:
            # AppleScriptを実行
            process = subprocess.Popen(['osascript', '-e', applescript], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if stderr:
                print(f"AppleScriptエラー: {stderr.decode()}")
            else:
                print("AppleScriptが実行されました")
                return True
                
        except Exception as e:
            print(f"AppleScript実行エラー: {e}")
            
        return False
    
    def method2_url_scheme(self, pdf_path: str):
        """方法2: URLスキームを使用"""
        
        print("\n=== 方法2: URLスキーム ===")
        
        # bunkoOCRのURLスキームを試す
        url_schemes = [
            f"bunkoOCR://open?file={pdf_path}",
            f"bunkoOCR://process?file={pdf_path}",
            f"bunkoOCR://{pdf_path}"
        ]
        
        for scheme in url_schemes:
            print(f"試行中: {scheme}")
            try:
                subprocess.run(["open", scheme], check=True)
                time.sleep(2)
                return True
            except subprocess.CalledProcessError:
                print(f"  → 失敗")
                
        return False
    
    def method3_accessibility_api(self, pdf_path: str):
        """方法3: Accessibility APIを使用（要権限）"""
        
        print("\n=== 方法3: Accessibility API ===")
        
        # Pythonスクリプトでアクセシビリティ操作
        python_script = f'''
import subprocess
import time

# アプリを起動してファイルを開く
subprocess.run(["open", "-a", "bunkoOCR", "{pdf_path}"])
time.sleep(3)

# PyAutoGUIを使用した操作
try:
    import pyautogui
    
    # OCRボタンの位置を探す（画像認識）
    # button_location = pyautogui.locateOnScreen('ocr_button.png')
    # if button_location:
    #     pyautogui.click(button_location)
    
    # またはキーボードショートカット
    pyautogui.hotkey('cmd', 'o')
    
except ImportError:
    print("pyautoguiがインストールされていません")
    print("pip install pyautogui")
'''
        
        print("Accessibility APIの使用にはシステム環境設定での許可が必要です")
        print("システム環境設定 > セキュリティとプライバシー > アクセシビリティ")
        
        return False
    
    def method4_cli_interface(self, pdf_path: str):
        """方法4: CLIインターフェースを探す"""
        
        print("\n=== 方法4: CLIインターフェース ===")
        
        # bunkoOCRの実行ファイルを直接呼び出す
        bunko_binary = "/Applications/bunkoOCR.app/Contents/MacOS/bunkoOCR"
        
        # 可能なCLIオプションを試す
        cli_options = [
            [bunko_binary, pdf_path],
            [bunko_binary, "--process", pdf_path],
            [bunko_binary, "-f", pdf_path],
            [bunko_binary, "--file", pdf_path],
            [bunko_binary, "--ocr", pdf_path]
        ]
        
        for options in cli_options:
            print(f"試行中: {' '.join(options)}")
            try:
                result = subprocess.run(options, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("  → 成功")
                    return True
                else:
                    print(f"  → 失敗 (exit code: {result.returncode})")
            except subprocess.TimeoutExpired:
                print("  → タイムアウト")
            except Exception as e:
                print(f"  → エラー: {e}")
                
        return False
    
    def create_automation_shortcut(self):
        """ショートカットアプリ用の自動化を作成"""
        
        print("\n=== ショートカットアプリ用スクリプト ===")
        
        shortcut_script = '''
// macOS ショートカットアプリで使用
// 1. 新規ショートカットを作成
// 2. 以下のアクションを追加:

1. "ファイルを取得" アクション
   - 入力からファイルを取得

2. "アプリケーションを開く" アクション
   - bunkoOCRを選択
   - ファイルを開く

3. "待機" アクション
   - 3秒待機

4. "キーストロークを送信" アクション（要アクセシビリティ権限）
   - Command + O を送信

5. "通知を表示" アクション
   - "OCR処理を開始しました"
'''
        
        print(shortcut_script)
        
        # ショートカットファイルを生成
        shortcut_path = "bunkoOCR_automation.shortcut"
        print(f"\nショートカットファイルのパス: {shortcut_path}")
        
    def monitor_and_extract_results(self, timeout: int = 300):
        """結果を監視して抽出"""
        
        print(f"\nbunkoOCRの処理結果を監視中（最大{timeout}秒）...")
        
        # 処理前の結果フォルダ
        before_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
        
        start_time = time.time()
        check_interval = 2
        
        while time.time() - start_time < timeout:
            current_dirs = set(self.results_dir.iterdir()) if self.results_dir.exists() else set()
            new_dirs = current_dirs - before_dirs
            
            if new_dirs:
                latest_dir = max(new_dirs, key=lambda x: x.stat().st_mtime)
                print(f"\n✅ 新しい結果を検出: {latest_dir.name}")
                
                # テキストファイルが生成されるまで少し待つ
                time.sleep(5)
                
                # 結果を抽出
                return self.extract_results(latest_dir)
            
            # プログレス表示
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                print(f"  経過時間: {elapsed}秒", end='\r')
            
            time.sleep(check_interval)
        
        print("\n⏱️ タイムアウト: 結果が検出されませんでした")
        return None
    
    def extract_results(self, result_dir: Path) -> dict:
        """結果フォルダからデータを抽出"""
        
        # テキストファイルを結合
        text_files = sorted(result_dir.glob("text*.txt"))
        combined_text = []
        
        for text_file in text_files:
            with open(text_file, 'r', encoding='utf-8') as f:
                combined_text.append(f.read())
        
        # JSON構造データ
        json_files = sorted(result_dir.glob("result*.json"))
        structure_data = []
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                structure_data.append(json.load(f))
        
        return {
            'text': '\n'.join(combined_text),
            'structure': structure_data,
            'result_dir': str(result_dir),
            'text_files': len(text_files),
            'total_chars': sum(len(t) for t in combined_text)
        }
    
    def full_automation_process(self, pdf_path: str):
        """完全自動化プロセス"""
        
        print(f"\n{'='*60}")
        print(f"bunkoOCR 完全自動化プロセス")
        print(f"対象ファイル: {os.path.basename(pdf_path)}")
        print(f"{'='*60}")
        
        # 各方法を順番に試す
        methods = [
            ("AppleScript", self.method1_applescript),
            ("URLスキーム", self.method2_url_scheme),
            ("CLIインターフェース", self.method4_cli_interface)
        ]
        
        for method_name, method_func in methods:
            print(f"\n{method_name}を試行中...")
            if method_func(pdf_path):
                print(f"✅ {method_name}で起動成功")
                
                # 結果を監視
                result = self.monitor_and_extract_results()
                
                if result:
                    # 結果を保存
                    output_path = f"{Path(pdf_path).stem}_bunko_auto.txt"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result['text'])
                    
                    print(f"\n✅ 処理完了!")
                    print(f"出力ファイル: {output_path}")
                    print(f"総文字数: {result['total_chars']:,}文字")
                    print(f"ページ数: {result['text_files']}")
                    
                    return result
                    
        print("\n❌ 自動化に失敗しました")
        print("\n【手動操作が必要です】")
        print("1. bunkoOCRアプリが起動したら")
        print("2. OCR処理ボタンをクリック")
        print("3. 処理完了を待つ")
        
        # 手動操作後の結果を監視
        return self.monitor_and_extract_results(timeout=600)


def main():
    """メイン実行"""
    
    automation = BunkoOCRFullAutomation()
    
    # テスト用PDF
    pdf_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/渋渋/15渋渋.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        return
    
    # 完全自動化を試行
    result = automation.full_automation_process(pdf_path)
    
    if result:
        print("\n🎉 bunkoOCRの自動処理が完了しました!")
    else:
        print("\n手動操作で処理を完了してください")
    
    # ショートカットアプリ用のスクリプトも生成
    print("\n" + "="*60)
    automation.create_automation_shortcut()


if __name__ == "__main__":
    main()