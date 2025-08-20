#!/usr/bin/env python3
"""PDF処理からExcel出力までのテストスクリプト"""

import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from core.application import EntranceExamAnalyzer

# PDFファイル
pdf_file = "/Users/yoshiikatsuhiko/Desktop/01_仕事 (Work)/オンライン家庭教師資料/過去問/早稲田実業学校中等部中学校/2015年早稲田実業学校中等部中学校問題_国語.pdf"

if not Path(pdf_file).exists():
    print(f"❌ PDFファイルが見つかりません: {pdf_file}")
    sys.exit(1)

print(f"📄 PDFファイル: {Path(pdf_file).name}")

# アプリケーションを初期化
app = EntranceExamAnalyzer()

# PDFを処理
try:
    # ファイル選択を模擬
    from models import FileSelectionResult
    file_result = FileSelectionResult(
        selected_file=Path(pdf_file),
        cancelled=False,
        selection_method="direct"
    )
    
    print("\n📖 ファイル読み込み中...")
    document = app._load_document(file_result.selected_file)
    
    if document:
        print(f"✅ 学校名: {document.school_name}")
        print(f"✅ 年度: {', '.join(document.years)}")
        
        # 年度ごとに分析
        print("\n📊 分析実行中...")
        results = app._analyze_by_years(document)
        
        if results:
            print(f"✅ 分析結果: {len(results)}件")
            
            # 結果を保存
            print("\n💾 Excel保存中...")
            app._save_results(results)
            
            # Excelファイルの存在確認
            excel_path = app.excel_manager.db_path
            if excel_path.exists():
                print(f"✅ Excelファイル作成成功: {excel_path}")
                print(f"   ファイルサイズ: {excel_path.stat().st_size:,} bytes")
            else:
                print(f"❌ Excelファイルが作成されませんでした")
        else:
            print("❌ 分析結果が空です")
    else:
        print("❌ ドキュメントの読み込みに失敗しました")
        
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()