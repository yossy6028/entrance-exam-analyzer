#!/usr/bin/env python3
"""
Excel保存エラーの修正を検証するためのテストスクリプト
"""

from modules.excel_manager import ExcelManager
from models import AnalysisResult, Section, Question, ExamSource, ExcelExportConfig
from pathlib import Path
import tempfile
import os


def test_none_section_text():
    """section.textがNoneの場合のテスト"""
    print("🧪 Excel保存エラー修正のテスト開始")
    
    # 一時ファイルを作成
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        temp_path = Path(tmp.name)
    
    try:
        # ExcelManagerを作成
        config = ExcelExportConfig(db_filename=str(temp_path))
        excel_manager = ExcelManager(config)
        
        # section.text が None の Section を作成（これがエラーの原因だった）
        section_with_none_text = Section(
            number=1,
            title="大問1",
            content="テスト内容",
            question_count=2,
            text=None  # ← これが None でエラーが発生していた
        )
        
        # 通常のSectionも作成
        normal_section = Section(
            number=2,
            title="大問2",
            content="通常のテスト内容",
            question_count=1,
            text="これは通常のテキストです。"
        )
        
        # Question と ExamSource も作成
        questions = [
            Question(number=1, text="問題1", type="記述", section=1),
            Question(number=2, text="問題2", type="選択", section=1),
            Question(number=3, text="問題3", type="記述", section=2)
        ]
        
        sources = [
            ExamSource(author="作者1", title="作品1"),
            ExamSource(author="作者2", title="作品2")
        ]
        
        # AnalysisResult を作成
        result = AnalysisResult(
            school_name="開成中学校",
            year="2025",
            total_characters=1500,
            sections=[section_with_none_text, normal_section],
            questions=questions,
            question_types={"記述": 2, "選択": 1},
            sources=sources,
            theme="テストテーマ",
            genre="テストジャンル"
        )
        
        # Excel保存を実行（修正前はここでエラーが発生していた）
        success = excel_manager.save_analysis_result(result)
        
        if success:
            print("✅ 成功: section.text が None でも Excel 保存が正常に完了しました")
            print(f"   保存先: {temp_path}")
            
            # ファイルが実際に作成されたかチェック
            if temp_path.exists() and temp_path.stat().st_size > 0:
                print("✅ 成功: Excel ファイルが正常に作成されました")
                return True
            else:
                print("❌ エラー: Excel ファイルが作成されませんでした")
                return False
        else:
            print("❌ エラー: Excel 保存に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    
    finally:
        # 一時ファイルを削除
        if temp_path.exists():
            os.unlink(temp_path)


def test_plugins_fix():
    """プラグインの修正をテスト"""
    print("\n🧪 プラグインの修正テスト開始")
    
    try:
        # section.text が None の Section を作成
        section = Section(
            number=1,
            title="テスト大問",
            text=None  # ← None の場合
        )
        
        # base.py の修正をテスト（インポートして正常動作を確認）
        from plugins.base import BasePlugin
        from plugins.musashi_plugin import MusashiPlugin
        
        print("✅ 成功: プラグインのインポートが正常に完了しました")
        
        # MusashiPluginの修正をテスト
        plugin = MusashiPlugin()
        
        # filter_sections を呼び出してエラーが発生しないかテスト
        sections = [section]
        try:
            filtered = plugin.filter_sections(sections)
            print("✅ 成功: MusashiPlugin.filter_sections が正常に動作しました")
            return True
        except Exception as e:
            print(f"❌ エラー: MusashiPlugin.filter_sections でエラー: {e}")
            return False
            
    except Exception as e:
        print(f"❌ プラグインテストでエラー: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Excel 保存エラー修正の検証テスト")
    print("=" * 50)
    
    test1_result = test_none_section_text()
    test2_result = test_plugins_fix()
    
    print("\n" + "=" * 50)
    print("テスト結果")
    print("=" * 50)
    print(f"Excel保存テスト: {'✅ 成功' if test1_result else '❌ 失敗'}")
    print(f"プラグインテスト: {'✅ 成功' if test2_result else '❌ 失敗'}")
    
    if test1_result and test2_result:
        print("\n🎉 すべてのテストが成功しました！修正が完了しています。")
    else:
        print("\n⚠️  一部のテストが失敗しました。追加の修正が必要です。")