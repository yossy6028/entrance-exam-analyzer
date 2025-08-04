#!/usr/bin/env python3
"""
macOSファイルダイアログの自動選択方法をテスト
"""
import pyautogui
import time
import subprocess
import pyperclip

def method1_paste_full_path():
    """方法1: フルパスを直接ペーストする"""
    print("\n🔧 方法1: フルパスを直接ペースト")
    print("-" * 40)
    
    full_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/2023過去問/23女子学院/kokugo-mondai (1).pdf"
    
    # フルパスをクリップボードにコピー
    pyperclip.copy(full_path)
    
    # Cmd+Shift+Gでパス入力ダイアログを開く
    pyautogui.hotkey('cmd', 'shift', 'g')
    time.sleep(0.5)
    
    # パスをペースト
    pyautogui.hotkey('cmd', 'v')
    time.sleep(0.5)
    
    # Enterで移動
    pyautogui.press('return')
    time.sleep(1)
    
    print("✅ フルパスで直接ファイルを開く")

def method2_applescript():
    """方法2: AppleScriptを使用"""
    print("\n🔧 方法2: AppleScriptを使用")
    print("-" * 40)
    
    applescript = '''
    tell application "System Events"
        tell process "bunkoOCR"
            set frontmost to true
            delay 0.5
            
            -- ファイルダイアログのテキストフィールドを探す
            tell window 1
                -- 検索フィールドにフォーカス
                set focused of text field 1 to true
                delay 0.5
                
                -- 検索文字を入力
                keystroke "kokugo"
                delay 1
            end tell
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', applescript])
    print("✅ AppleScriptで検索フィールドに入力")

def method3_list_navigation():
    """方法3: リスト内を矢印キーで移動"""
    print("\n🔧 方法3: リスト内を矢印キーで移動")
    print("-" * 40)
    
    # ファイルリストの最初に移動
    pyautogui.hotkey('cmd', 'up')  # リストの最初へ
    time.sleep(0.5)
    
    # 下矢印でkokugoファイルまで移動
    # 通常、kokugoファイルはアルファベット順で中間あたり
    for i in range(10):
        pyautogui.press('down')
        time.sleep(0.1)
        print(f"  ↓ {i+1}回目の移動")
    
    print("✅ 矢印キーでファイルを選択")

def method4_filename_quicktype():
    """方法4: ファイル名を素早く入力"""
    print("\n🔧 方法4: ファイル名を素早く入力")
    print("-" * 40)
    
    # BunkoOCRをアクティブ化
    subprocess.run(['osascript', '-e', 'tell application "bunkoOCR" to activate'])
    time.sleep(1)
    
    # ファイルリストにフォーカスがあることを確認
    # 一度クリックしてフォーカスを確実にする
    pyautogui.click(x=500, y=400)  # ファイルリストの中央あたり
    time.sleep(0.5)
    
    # 素早く連続で文字を入力
    pyautogui.typewrite('kok', interval=0.05)
    time.sleep(0.5)
    
    print("✅ ファイル名の先頭文字を素早く入力")

def method5_accessibility_api():
    """方法5: macOSのアクセシビリティAPIを使用"""
    print("\n🔧 方法5: アクセシビリティAPIを使用")
    print("-" * 40)
    
    # AXUIElementを使用してファイルダイアログを操作
    applescript = '''
    tell application "System Events"
        tell process "bunkoOCR"
            set frontmost to true
            
            -- ファイルダイアログのアウトラインを探す
            tell window 1
                tell outline 1 of scroll area 1
                    -- kokugoを含む行を探す
                    repeat with i from 1 to count of rows
                        if value of static text 1 of row i contains "kokugo" then
                            select row i
                            exit repeat
                        end if
                    end repeat
                end tell
            end tell
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', applescript])
    print("✅ アクセシビリティAPIでファイルを選択")

def test_all_methods():
    """すべての方法をテスト"""
    print("🧪 macOSファイルダイアログ自動選択テスト")
    print("=" * 60)
    
    methods = [
        ("1", "フルパスペースト", method1_paste_full_path),
        ("2", "AppleScript", method2_applescript),
        ("3", "矢印キー移動", method3_list_navigation),
        ("4", "高速文字入力", method4_filename_quicktype),
        ("5", "アクセシビリティAPI", method5_accessibility_api),
    ]
    
    print("\nテスト方法を選択してください:")
    for num, name, _ in methods:
        print(f"{num}. {name}")
    print("a. すべて順番にテスト")
    print("q. 終了")
    
    choice = input("\n選択 (1-5/a/q): ")
    
    if choice == 'q':
        return
    elif choice == 'a':
        for num, name, method in methods:
            print(f"\n{'='*60}")
            method()
            input("\n次の方法をテストするにはEnterキーを押してください...")
    else:
        for num, name, method in methods:
            if num == choice:
                method()
                break

if __name__ == "__main__":
    print("⚠️  注意: BunkoOCRのファイルダイアログが開いている状態で実行してください")
    test_all_methods()