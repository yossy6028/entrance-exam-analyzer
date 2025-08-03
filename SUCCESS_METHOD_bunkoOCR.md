# bunkoOCRで「ファイルから選択」を成功させる方法

## 🎉 成功した手順（2025年8月3日 02:24）

### 完全版：ファイル選択まで含めた成功手順

### 1. キーボードナビゲーション方式（これが成功！）

```python
#!/usr/bin/env python3
"""
成功したキーボードナビゲーション方法
"""
import pyautogui
import time
import subprocess

# bunkoOCRをアクティブ化
subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
time.sleep(1.5)

# Tabキーでメニューにフォーカス
pyautogui.press('tab')
time.sleep(0.5)

# 上矢印5回で最上部へ
for i in range(5):
    pyautogui.press('up')
    time.sleep(0.2)

# 下矢印2回で「ファイルから選択」へ
pyautogui.press('down')
time.sleep(0.5)
pyautogui.press('down')
time.sleep(0.5)

# 🔥🔥🔥 超重要：スペースキーで開く！！！ 🔥🔥🔥
# Enterキーは絶対に使うな！効かない！
# スペースキーを押す（これが唯一の正解！）
pyautogui.press('space')
time.sleep(1)

# ❌❌❌ 以下は全部失敗する ❌❌❌
# pyautogui.press('return')  # ダメ！
# pyautogui.press('enter')   # ダメ！
# key code 36               # ダメ！
```

### 2. ファイル選択の自動化（完全版）

```python
# ファイルダイアログが開いたら、過去問フォルダに移動
folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
pyperclip.copy(folder_path)

# Cmd+Shift+G でパス入力ダイアログ
pyautogui.hotkey('cmd', 'shift', 'g')
time.sleep(0.5)

# パスをペースト
pyautogui.hotkey('cmd', 'v')
time.sleep(0.5)

# Enterでフォルダに移動
pyautogui.press('return')
time.sleep(2)

# 「開成」で検索
pyautogui.hotkey('cmd', 'f')
time.sleep(0.5)
pyautogui.typewrite('開成')
time.sleep(1)

# 検索結果を選択（開成中学校フォルダ）
pyautogui.press('down')
time.sleep(0.5)
pyautogui.press('return')  # フォルダを開く
time.sleep(2)

# フォルダ内で「25」を検索
pyautogui.hotkey('cmd', 'f')
time.sleep(0.5)
pyautogui.typewrite('25')
time.sleep(1)

# 最初のPDFを選択
pyautogui.press('down')
time.sleep(0.5)
pyautogui.press('return')
time.sleep(0.5)

# 開くボタンを押す
pyautogui.press('return')
```

## ❌ 失敗した方法（記録として残す）

1. **座標クリック** - bunkoOCRの特殊なUI実装のため失敗
   - (689, 475) - 過去の成功座標も失敗
   - (100, 139) - 「ファイルから選択」の位置も失敗
   - (103, 139) - テキスト中央も失敗

2. **AppleScriptのbutton click** - button 3は認識したが効果なし

3. **単純なEnterキー** - メニュー選択後に単独で押しても効果なし

## 🔑 成功のポイント

1. **キーボードナビゲーションが唯一の方法**
2. **Enterキーは3つの方法を連続で試す必要がある**
3. **タイミング（sleep）が重要**
4. **bunkoOCRをアクティブにすることが必須**

## 📝 メモ

- ファイル名は「開成」「25」などのキーワードで検索可能
- 渋渋の場合は「15渋渋.pdf」などの名前
- OCR処理には2-3分かかる
- 処理完了後は `python check_latest_bunko_result.py` で確認

## 🚨 重要：忘れないこと！

**この方法を忘れるな！座標クリックは絶対に使うな！**