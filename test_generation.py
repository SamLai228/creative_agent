"""EDM 生成功能測試腳本"""
from pathlib import Path
from src.generator import EDMGenerator
from src.config import OUTPUT_DIR


def test_case_1_life_insurance():
    """測試案例 1: 終身壽險推廣"""
    print("\n" + "=" * 60)
    print("測試案例 1: 終身壽險推廣")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "product_name": "終身壽險",
        "key_message": "終身保障，守護一生",
        "target_audience": "家庭",
        "tone": "溫馨",
        "style": ["現代", "簡約"],
        "mood": ["溫馨", "安心"],
        "color_scheme": "中性",
        "layout": "centered"
    }
    
    try:
        result = generator.generate(requirements, output_format="png")
        print(f"✓ 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        print(f"  使用版面: {result['layout']}")
        print(f"  使用素材數: {len(result['materials_used'])}")
        print(f"  素材列表:")
        for i, material in enumerate(result['materials_used'], 1):
            print(f"    {i}. {material.get('file_name')} ({material.get('category')})")
        return True
    except Exception as e:
        print(f"✗ 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_case_2_medical_insurance():
    """測試案例 2: 醫療險推廣"""
    print("\n" + "=" * 60)
    print("測試案例 2: 醫療險推廣")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "product_name": "實支實付醫療險",
        "key_message": "住院醫療費用全額給付",
        "target_audience": "一般消費者",
        "tone": "專業",
        "category": "人物",
        "scenario": ["家庭", "健康"],
        "mood": ["專業", "安心"],
        "style": ["現代", "專業"],
        "layout": "left-aligned"
    }
    
    try:
        result = generator.generate(requirements, output_format="png")
        print(f"✓ 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        print(f"  使用版面: {result['layout']}")
        print(f"  使用素材數: {len(result['materials_used'])}")
        return True
    except Exception as e:
        print(f"✗ 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_case_3_critical_illness():
    """測試案例 3: 重大疾病險推廣"""
    print("\n" + "=" * 60)
    print("測試案例 3: 重大疾病險推廣")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "product_name": "重大疾病險",
        "key_message": "確診即理賠，無需等待期",
        "target_audience": "中壯年",
        "tone": "專業",
        "style": ["現代", "專業"],
        "mood": ["專業", "安心"],
        "color_scheme": "中性",
        "scenario": ["健康"],
        "layout": "hero"
    }
    
    try:
        result = generator.generate(requirements, output_format="png")
        print(f"✓ 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        print(f"  使用版面: {result['layout']}")
        print(f"  使用素材數: {len(result['materials_used'])}")
        return True
    except Exception as e:
        print(f"✗ 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_case_4_accident_insurance():
    """測試案例 4: 意外險推廣"""
    print("\n" + "=" * 60)
    print("測試案例 4: 意外險推廣")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "product_name": "意外險",
        "key_message": "全天候保障，意外傷害立即理賠",
        "target_audience": "一般消費者",
        "tone": "安心",
        "scenario": ["生活"],
        "mood": ["安心", "專業"],
        "keywords": ["意外", "保障"],
        "layout": "grid"
    }
    
    try:
        result = generator.generate(requirements, output_format="png")
        print(f"✓ 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        print(f"  使用版面: {result['layout']}")
        print(f"  使用素材數: {len(result['materials_used'])}")
        return True
    except Exception as e:
        print(f"✗ 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_case_5_pdf_output():
    """測試案例 5: PDF 格式輸出"""
    print("\n" + "=" * 60)
    print("測試案例 5: PDF 格式輸出")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "title": "PDF 測試",
        "description": "測試 PDF 格式輸出功能",
        "layout": "centered"
    }
    
    try:
        result = generator.generate(requirements, output_format="pdf")
        print(f"✓ PDF 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        return True
    except Exception as e:
        print(f"✗ PDF 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_preview_materials():
    """測試素材預覽功能"""
    print("\n" + "=" * 60)
    print("測試: 素材預覽功能")
    print("=" * 60)
    
    generator = EDMGenerator()
    
    requirements = {
        "category": "人物",
        "mood": ["歡樂", "可愛"],
        "style": ["插畫"]
    }
    
    try:
        materials = generator.select_materials(requirements)
        print(f"✓ 找到 {len(materials)} 個符合條件的素材")
        for i, material in enumerate(materials[:5], 1):  # 只顯示前 5 個
            print(f"  {i}. {material.get('file_name')} - {material.get('category')}")
        return True
    except Exception as e:
        print(f"✗ 預覽失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_available_layouts():
    """測試取得可用版面配置"""
    print("\n" + "=" * 60)
    print("測試: 取得可用版面配置")
    print("=" * 60)
    
    from src.generator.template_engine import TemplateEngine
    
    try:
        engine = TemplateEngine()
        layouts = engine.get_available_layouts()
        print(f"✓ 可用版面配置: {', '.join(layouts)}")
        return True
    except Exception as e:
        print(f"✗ 取得版面配置失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """執行所有測試案例"""
    print("\n" + "=" * 60)
    print("EDM 生成功能測試")
    print("=" * 60)
    
    results = []
    
    # 測試 1: 取得可用版面
    results.append(("取得版面配置", test_available_layouts()))
    
    # 測試 2: 素材預覽
    results.append(("素材預覽", test_preview_materials()))
    
    # 測試 3-6: 生成測試
    results.append(("終身壽險", test_case_1_life_insurance()))
    results.append(("醫療險", test_case_2_medical_insurance()))
    results.append(("重大疾病險", test_case_3_critical_illness()))
    results.append(("意外險", test_case_4_accident_insurance()))
    results.append(("PDF 輸出", test_case_5_pdf_output()))
    
    # 顯示測試結果摘要
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n總計: {passed} 個通過, {failed} 個失敗")
    print(f"\n生成的檔案位置: {OUTPUT_DIR / 'edm'}")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
