"""測試 EDM 生成 API 端點"""
import requests
import json


API_BASE_URL = "http://localhost:8000"


def test_get_layouts():
    """測試取得可用版面配置"""
    print("\n測試: GET /api/generation/layouts")
    print("-" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/generation/layouts")
        response.raise_for_status()
        layouts = response.json()
        print(f"✓ 成功取得 {len(layouts)} 個版面配置:")
        for layout in layouts:
            print(f"  - {layout}")
        return True
    except Exception as e:
        print(f"✗ 失敗: {str(e)}")
        return False


def test_preview_materials():
    """測試預覽素材"""
    print("\n測試: GET /api/generation/preview-materials")
    print("-" * 60)
    
    try:
        params = {
            "category": "人物",
            "mood": ["歡樂", "可愛"]
        }
        response = requests.get(
            f"{API_BASE_URL}/api/generation/preview-materials",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ 找到 {data['count']} 個符合條件的素材")
        for i, material in enumerate(data['materials'][:3], 1):
            print(f"  {i}. {material.get('file_name')}")
        return True
    except Exception as e:
        print(f"✗ 失敗: {str(e)}")
        return False


def test_generate_edm():
    """測試生成 EDM"""
    print("\n測試: POST /api/generation/generate")
    print("-" * 60)
    
    request_data = {
        "title": "春季特賣",
        "description": "全館商品 8 折優惠，限時一週！",
        "style": ["現代", "簡約"],
        "mood": ["活力", "歡樂"],
        "color_scheme": "鮮豔",
        "layout": "centered",
        "output_format": "png"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generation/generate",
            json=request_data
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 生成成功！")
        print(f"  輸出路徑: {result['output_path']}")
        print(f"  使用版面: {result['layout']}")
        print(f"  使用素材數: {len(result['materials_used'])}")
        print(f"  訊息: {result['message']}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP 錯誤: {e.response.status_code}")
        print(f"  錯誤訊息: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ 失敗: {str(e)}")
        return False


def main():
    """執行所有 API 測試"""
    print("\n" + "=" * 60)
    print("EDM 生成 API 測試")
    print("=" * 60)
    print(f"\n請確保後端服務正在運行: {API_BASE_URL}")
    print("如果服務未運行，請先執行: uvicorn api.main:app --reload --port 8000")
    
    # 檢查服務是否運行
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ 後端服務未正常運行，請先啟動服務")
            return False
    except requests.exceptions.RequestException:
        print("\n✗ 無法連接到後端服務，請先啟動服務")
        print("  啟動命令: uvicorn api.main:app --reload --port 8000")
        return False
    
    print("✓ 後端服務連接成功\n")
    
    results = []
    results.append(("取得版面配置", test_get_layouts()))
    results.append(("預覽素材", test_preview_materials()))
    results.append(("生成 EDM", test_generate_edm()))
    
    # 顯示測試結果摘要
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{status}: {test_name}")
    
    print(f"\n總計: {passed} 個通過, {failed} 個失敗")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n測試中斷")
        sys.exit(1)
