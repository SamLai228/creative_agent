"""使用範例"""
from pathlib import Path
from src.material_factory import MaterialFactory
from src.config import ASSETS_DIR

# 建立素材工廠實例
factory = MaterialFactory()

# 範例 1: 為單一素材貼標
print("範例 1: 為單一素材貼標")
print("=" * 50)
image_path = ASSETS_DIR / "example.jpg"  # 替換為實際的圖片路徑
if image_path.exists():
    tags = factory.tag_single_material(image_path)
    print(f"\n標籤結果:")
    print(f"  類型: {tags.get('category')}")
    print(f"  風格: {tags.get('style')}")
    print(f"  情境: {tags.get('scenario')}")
    print(f"  色系: {tags.get('color_scheme')}")
    print(f"  氛圍: {tags.get('mood')}")
    print(f"  關鍵字: {tags.get('keywords')}")
else:
    print(f"請先將圖片放到 {ASSETS_DIR} 目錄")

# 範例 2: 批次為素材貼標
print("\n\n範例 2: 批次為素材貼標")
print("=" * 50)
results = factory.tag_batch_materials(ASSETS_DIR)

# 範例 3: 搜尋素材
print("\n\n範例 3: 搜尋素材")
print("=" * 50)
# 搜尋「人物」類型的「插畫」風格素材
results = factory.search_materials(
    category="人物",
    style=["插畫"]
)
print(f"找到 {len(results)} 個符合條件的素材")

# 範例 4: 查看統計資訊
print("\n\n範例 4: 查看統計資訊")
print("=" * 50)
stats = factory.get_material_stats()
print(f"總素材數: {stats['total_materials']}")
print(f"按類型分類: {stats['by_category']}")
