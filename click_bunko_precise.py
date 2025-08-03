#!/usr/bin/env python3
"""
bunkoOCRの「ファイルから選択」を正確にクリック
"""
import subprocess
import time

def click_file_from_select():
    """AppleScriptで正確にクリック"""
    
    script = '''
    tell application "System Events"
        tell process "bunkoOCR"
            set frontmost to true
            delay 0.5
            
            -- ウィンドウ内のテーブルの3番目の行を探す
            tell window 1
                -- グループ内のスクロールエリア内のテーブルを探す
                set found to false
                set groupList to every group
                
                repeat with g in groupList
                    try
                        -- スクロールエリアを探す
                        set scrollAreas to every scroll area of g
                        repeat with sa in scrollAreas
                            try
                                -- テーブルを探す
                                set tables to every table of sa
                                repeat with t in tables
                                    -- 3番目の行をクリック
                                    tell row 3 of t
                                        perform action "AXPress"
                                        set found to true
                                        exit repeat
                                    end tell
                                end repeat
                                if found then exit repeat
                            end try
                        end repeat
                        if found then exit repeat
                    end try
                end repeat
                
                -- もし見つからなかった場合、直接的な方法を試す
                if not found then
                    -- 座標でクリック（bunkoOCRウィンドウ内の相対位置）
                    set {x, y} to position
                    set {w, h} to size
                    
                    -- ウィンドウの中央、上から約300-400ピクセルの位置
                    set clickX to x + (w / 2)
                    set clickY to y + 350  -- 3番目の項目の推定位置
                    
                    -- マウスクリックをシミュレート
                    do shell script "/usr/bin/python3 -c 'import Quartz; Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, (" & clickX & ", " & clickY & "), Quartz.kCGMouseButtonLeft); Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, (" & clickX & ", " & clickY & "), Quartz.kCGMouseButtonLeft)'"
                end if
            end tell
        end tell
    end tell
    '''
    
    print("bunkoOCRで「ファイルから選択」をクリックします...")
    
    # AppleScriptを実行
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print("クリックしました")
        
        print("\nファイルダイアログが開いたら：")
        print("1. デスクトップ → 01_仕事 (Work) → オンライン家庭教師資料 → 過去問 → 渋渋")
        print("2. 15渋渋.pdf を選択")
        print("3. 「開く」ボタンをクリック")
        
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")
        print("\n代替方法：")
        print("bunkoOCRウィンドウで手動で「ファイルから選択」をクリックしてください")

if __name__ == "__main__":
    click_file_from_select()
    
    # OCR処理を待つ
    print("\nファイルを選択したらOCR処理が開始されます（約30秒）")
    for i in range(30):
        print("■", end="", flush=True)
        time.sleep(1)
    print("\n処理完了！")