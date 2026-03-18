"""素材工廠 - 主要工作流程管理"""
from pathlib import Path
from typing import List, Dict, Optional
from src.config import ASSETS_DIR
from .image_analyzer import ImageAnalyzer
from .llm_tagger import LLMTagger
from .tag_database import TagDatabase
from .bg_remover import remove_background


class MaterialFactory:
    """素材工廠 - 管理素材貼標流程"""
    
    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.llm_tagger = LLMTagger()
        self.tag_db = TagDatabase()
    
    def _run_bg_removal(self, image_path: Path) -> Optional[str]:
        """
        對單張圖片執行去背，回傳去背檔案的相對路徑（相對於專案根目錄）。
        失敗時印出警告並回傳 None。
        """
        try:
            nobg_path = remove_background(image_path)
            return str(nobg_path.relative_to(ASSETS_DIR.parent))
        except Exception as e:
            print(f"  - 去背失敗，略過：{e}")
            return None

    def tag_single_material(self, image_path: Path, force_update: bool = False) -> Dict:
        """
        為單一素材貼標（含自動去背）。

        流程：
        1. 去背（若 _nobg.png 已存在則跳過）
        2. 若已有標籤且非 force_update：補上 nobg_path 後直接回傳
        3. 否則用 LLM 生成標籤，一併存入 nobg_path

        Args:
            image_path: 圖片路徑
            force_update: 是否強制重新貼標

        Returns:
            標籤資訊字典
        """
        # Step 1：去背（無論是否已有標籤都執行，確保 _nobg.png 存在）
        nobg_rel = self._run_bg_removal(image_path)

        # 統一用相對路徑作為 DB key，避免絕對路徑/相對路徑不一致
        try:
            db_key = str(image_path.relative_to(ASSETS_DIR.parent))
        except ValueError:
            db_key = str(image_path)

        # Step 2：若已有標籤且不強制更新，補上 nobg_path 後回傳
        if not force_update:
            existing_tags = self.tag_db.get_tags(db_key)
            if existing_tags:
                if nobg_rel and existing_tags.get("nobg_path") != nobg_rel:
                    existing_tags["nobg_path"] = nobg_rel
                    self.tag_db.add_tags(db_key, existing_tags)
                print(f"素材已有標籤，跳過: {image_path.name}")
                return existing_tags

        print(f"正在分析素材: {image_path.name}")

        # 分析圖片（使用原圖，保留完整內容供 LLM 理解）
        image_info = self.image_analyzer.analyze(image_path)
        print(f"  - 尺寸: {image_info['width']}x{image_info['height']}")
        print(f"  - 長寬比: {image_info['aspect_ratio']}")

        # 使用 LLM 生成標籤
        print(f"  - 正在呼叫 LLM API 生成標籤...")
        tags = self.llm_tagger.generate_tags(image_path, image_info)

        if nobg_rel:
            tags["nobg_path"] = nobg_rel
            # file_path / file_name 直接指向去背版本，供後續選圖使用
            tags["file_path"] = nobg_rel
            tags["file_name"] = Path(nobg_rel).name

        # 儲存標籤（用相對路徑 key）
        self.tag_db.add_tags(db_key, tags)
        print(f"  ✓ 標籤已儲存")

        return tags

    def remove_bg_all(self, directory: Optional[Path] = None) -> int:
        """
        批次對現有素材去背，並將 nobg_path 寫入 tag DB。
        已有去背檔案的素材會跳過處理，只補上 nobg_path 欄位。

        Returns:
            成功處理的數量
        """
        if directory is None:
            directory = ASSETS_DIR

        all_tags = self.tag_db.get_all_tags()
        # 只處理有標籤的原始素材（排除 _nobg.png 本身）
        targets = [
            Path(ASSETS_DIR.parent / fp)
            for fp in all_tags
            if "_nobg" not in fp
        ]

        print(f"找到 {len(targets)} 個素材，開始批次去背...")
        success = 0
        for i, image_path in enumerate(targets, 1):
            print(f"\n[{i}/{len(targets)}] {image_path.name}")
            if not image_path.exists():
                print(f"  - 檔案不存在，跳過")
                continue
            nobg_rel = self._run_bg_removal(image_path)
            if nobg_rel:
                key = str(image_path.relative_to(ASSETS_DIR.parent))
                tags = all_tags.get(key)
                if tags is None:
                    print(f"  - 無標籤記錄，跳過 DB 更新")
                    success += 1
                    continue
                if tags.get("nobg_path") != nobg_rel:
                    tags["nobg_path"] = nobg_rel
                    self.tag_db.add_tags(key, tags)
                success += 1

        print(f"\n完成！成功去背 {success}/{len(targets)} 個素材")
        return success
    
    def tag_batch_materials(
        self,
        directory: Optional[Path] = None,
        extensions: Optional[List[str]] = None,
        force_update: bool = False
    ) -> List[Dict]:
        """
        批次為素材貼標
        
        Args:
            directory: 素材目錄（預設為 ASSETS_DIR）
            extensions: 支援的檔案副檔名列表
            force_update: 是否強制更新已存在的標籤
            
        Returns:
            標籤資訊列表
        """
        if directory is None:
            directory = ASSETS_DIR
        
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        # 找出所有圖片檔案
        image_files = []
        for ext in extensions:
            image_files.extend(directory.glob(f"*{ext}"))
            image_files.extend(directory.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"在 {directory} 中找不到圖片檔案")
            return []
        
        print(f"找到 {len(image_files)} 個素材檔案")
        print("=" * 50)
        
        results = []
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]")
            try:
                tags = self.tag_single_material(image_path, force_update)
                results.append(tags)
            except Exception as e:
                print(f"  ✗ 處理失敗: {str(e)}")
                continue
        
        print("\n" + "=" * 50)
        print(f"完成！成功處理 {len(results)}/{len(image_files)} 個素材")
        
        return results
    
    def search_materials(
        self,
        category: Optional[str] = None,
        style: Optional[List[str]] = None,
        scenario: Optional[List[str]] = None,
        color_scheme: Optional[str] = None,
        mood: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        根據標籤搜尋素材
        
        Args:
            category: 類型
            style: 風格列表
            scenario: 情境列表
            color_scheme: 色系
            mood: 氛圍列表
            keywords: 關鍵字列表
            
        Returns:
            符合條件的素材列表
        """
        return self.tag_db.search_by_tags(
            category=category,
            style=style,
            scenario=scenario,
            color_scheme=color_scheme,
            mood=mood,
            keywords=keywords
        )
    
    def get_material_stats(self) -> Dict:
        """取得素材統計資訊"""
        all_tags = self.tag_db.get_all_tags()
        
        stats = {
            "total_materials": len(all_tags),
            "by_category": {},
            "by_style": {},
            "by_scenario": {},
            "by_color_scheme": {},
        }
        
        for tags in all_tags.values():
            # 統計類型
            category = tags.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # 統計風格
            for style in tags.get("style", []):
                stats["by_style"][style] = stats["by_style"].get(style, 0) + 1
            
            # 統計情境
            for scenario in tags.get("scenario", []):
                stats["by_scenario"][scenario] = stats["by_scenario"].get(scenario, 0) + 1
            
            # 統計色系
            color_scheme = tags.get("color_scheme", "unknown")
            stats["by_color_scheme"][color_scheme] = stats["by_color_scheme"].get(color_scheme, 0) + 1
        
        return stats
