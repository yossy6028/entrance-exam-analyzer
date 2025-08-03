# 🎉 bunkoOCR完全攻略マニュアル（最終決定版）

## 📌 重要な発見事項
1. **Enterキーは効かない → スペースキーを使う！**
2. **上矢印は8回必要（5回では足りない場合がある）**
3. **ファイル選択時は必ずbunkoOCRにフォーカスを戻す**
4. **検索機能は使えない → 下矢印で確実に移動**
5. **スクリーンショットで現在位置を確認できる**

## 🚀 完全なワークフロー

### 1️⃣ bunkoOCRを起動してアクティブ化
```python
subprocess.run(["osascript", "-e", 'tell application "bunkoOCR" to activate'])
time.sleep(2)
```

### 2️⃣ 「ファイルから選択」を選択
```python
# Tab → 上8回 → 下2回
pyautogui.press('tab')
time.sleep(0.5)

# 上8回（重要：5回では足りない！）
for i in range(8):
    pyautogui.press('up')
    time.sleep(0.2)

# 下2回で「ファイルから選択」
pyautogui.press('down')
time.sleep(0.5)
pyautogui.press('down')
time.sleep(0.5)
```

### 3️⃣ 🔥 スペースキーでファイルダイアログを開く
```python
# 超重要：Enterではない！スペースキー！
pyautogui.press('space')
time.sleep(2)
```

### 4️⃣ 過去問フォルダに移動
```python
folder_path = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問"
pyperclip.copy(folder_path)

pyautogui.hotkey('cmd', 'shift', 'g')
time.sleep(0.5)
pyautogui.hotkey('cmd', 'v')
time.sleep(0.5)
pyautogui.press('return')
time.sleep(2)
```

### 5️⃣ 開成フォルダを検索して開く
```python
pyautogui.hotkey('cmd', 'f')
time.sleep(0.5)
pyautogui.typewrite('開成')
time.sleep(1)

pyautogui.press('down')
time.sleep(0.5)
pyautogui.press('return')  # フォルダを開く
time.sleep(2)
```

### 6️⃣ 右矢印でファイルリストへ移動
```python
pyautogui.press('right')
time.sleep(0.5)
```

### 7️⃣ ファイルを選択（位置ベース）
```python
# 開成フォルダ内のファイル順序（固定）
# 1. 15開成.pdf
# 2. 16開成.pdf
# 3. 17開成.pdf
# 4. 18開成.pdf
# 5. 19開成.pdf
# 6. 20開成.pdf
# 7. 21開成.pdf
# 8. 22開成.pdf
# 9. 23開成.pdf
# 10. 24開成.pdf
# 11. 25開成.pdf

# 例：25開成.pdfを選択（最初から10回下）
for i in range(10):
    pyautogui.press('down')
    time.sleep(0.3)
```

### 8️⃣ ファイルを開く
```python
pyautogui.press('return')  # ファイル選択
time.sleep(0.5)
pyautogui.press('return')  # 開くボタン
```

## 🔍 デバッグ方法

### スクリーンショットで確認
```python
screenshot = pyautogui.screenshot()
screenshot.save(f"bunko_debug_{timestamp}.png")
```

### 現在位置から目標ファイルへの移動
```python
# 例：19開成.pdfから25開成.pdfへ
# 19(5番目) → 25(11番目) = 6つ下
for i in range(6):
    pyautogui.press('down')
    time.sleep(0.3)
```

## ❌ 失敗する方法（使うな！）
- Enterキーでファイルダイアログを開く → スペースキーを使え！
- 上矢印5回 → 8回必要！
- 座標クリック → キーボード操作のみ！
- 検索機能 → 動作しない！

## 📝 メモ
- OCR処理には2-3分かかる
- 処理完了後: `python check_latest_bunko_result.py`
- ターミナルに入力されてしまう場合は、bunkoOCRを再度アクティブ化

## 🎯 これで絶対に成功する！