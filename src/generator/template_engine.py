"""模板引擎 - 處理 EDM 模板和版面配置"""
from pathlib import Path
from typing import Dict, List, Optional
import json
from src.config import TEMPLATE_DIR, TEMPLATE_CONFIGS_DIR, TEMPLATE_IMAGES_DIR


class TemplateEngine:
    """EDM 模板引擎"""

    def __init__(self):
        self.template_dir = TEMPLATE_DIR
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.layouts_dir = self.template_dir / "layouts"
        self.layouts_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir = TEMPLATE_CONFIGS_DIR
        self.configs_dir.mkdir(parents=True, exist_ok=True)

        # 初始化預設版面配置
        self._init_default_layouts()

    def _init_default_layouts(self):
        """初始化預設版面配置"""
        default_layouts = {
            "centered": {
                "name": "置中版面",
                "title_position": (600, 200),
                "title_anchor": "center",
                "description_position": (600, 300),
                "description_anchor": "center",
                "description_max_width": 800,
                "character_position": (600, 500),
                "character_anchor": "center",
                "character_size": (300, 300),
                "decoration_positions": [
                    (200, 150),
                    (1000, 150)
                ],
                "decoration_sizes": [
                    (100, 100),
                    (100, 100)
                ]
            },
            "left-aligned": {
                "name": "左對齊版面",
                "title_position": (100, 150),
                "title_anchor": "lt",
                "description_position": (100, 250),
                "description_anchor": "lt",
                "description_max_width": 500,
                "character_position": (700, 400),
                "character_anchor": "center",
                "character_size": (400, 400),
                "decoration_positions": [
                    (50, 50),
                    (1100, 50)
                ],
                "decoration_sizes": [
                    (80, 80),
                    (80, 80)
                ]
            },
            "hero": {
                "name": "英雄版面",
                "title_position": (600, 250),
                "title_anchor": "center",
                "title_font_size": 72,
                "description_position": (600, 350),
                "description_anchor": "center",
                "description_max_width": 900,
                "character_position": (600, 550),
                "character_anchor": "center",
                "character_size": (400, 400),
                "decoration_positions": [],
                "decoration_sizes": []
            },
            "grid": {
                "name": "網格版面",
                "title_position": (300, 100),
                "title_anchor": "lt",
                "description_position": (300, 200),
                "description_anchor": "lt",
                "description_max_width": 400,
                "character_position": (900, 400),
                "character_anchor": "center",
                "character_size": (300, 300),
                "decoration_positions": [
                    (100, 500),
                    (500, 500),
                    (1100, 500)
                ],
                "decoration_sizes": [
                    (150, 150),
                    (150, 150),
                    (150, 150)
                ]
            }
        }
        
        # 儲存預設版面配置
        for layout_name, layout_config in default_layouts.items():
            layout_file = self.layouts_dir / f"{layout_name}.json"
            if not layout_file.exists():
                with open(layout_file, 'w', encoding='utf-8') as f:
                    json.dump(layout_config, f, ensure_ascii=False, indent=2)
    
    def get_available_layouts(self) -> List[str]:
        """
        取得可用的版面配置列表
        
        Returns:
            版面配置名稱列表
        """
        layouts = []
        for layout_file in self.layouts_dir.glob("*.json"):
            layouts.append(layout_file.stem)
        return layouts if layouts else ["centered", "left-aligned", "grid", "hero"]
    
    def load_layout(self, layout_name: str) -> Dict:
        """
        載入指定的版面配置
        
        Args:
            layout_name: 版面配置名稱
            
        Returns:
            版面配置字典
        """
        layout_file = self.layouts_dir / f"{layout_name}.json"
        
        if not layout_file.exists():
            # 如果檔案不存在，返回預設的置中版面
            layout_file = self.layouts_dir / "centered.json"
            if not layout_file.exists():
                self._init_default_layouts()
                layout_file = self.layouts_dir / "centered.json"
        
        try:
            with open(layout_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 無法載入版面配置 {layout_name}: {str(e)}")
            # 返回基本配置
            return {
                "name": layout_name,
                "title_position": (600, 200),
                "title_anchor": "center",
                "description_position": (600, 300),
                "description_anchor": "center",
                "description_max_width": 800,
            }
    
    def apply_layout(
        self,
        layout: Dict,
        materials: List[Dict],
        text_content: Dict
    ) -> Dict:
        """
        將素材和文字套用到版面配置
        
        Args:
            layout: 版面配置
            materials: 素材列表
            text_content: 文字內容字典
            
        Returns:
            組合後的配置字典
        """
        result = {
            "layout": layout,
            "text_content": text_content,
            "materials": {
                "background": None,
                "characters": [],
                "decorations": []
            }
        }
        
        # 分類素材
        for material in materials:
            category = material.get("category", "")
            if category == "背景":
                result["materials"]["background"] = material
            elif category == "人物":
                result["materials"]["characters"].append(material)
            elif category == "裝飾":
                result["materials"]["decorations"].append(material)
        
        return result
    
    def load_template_config(self, template_name: str) -> Optional[Dict]:
        """
        載入 template 的區域配置

        Args:
            template_name: Template 檔名（例如：edm_template_01.jpeg）

        Returns:
            Template 配置字典，如果不存在則返回 None
        """
        template_stem = Path(template_name).stem
        config_file = self.configs_dir / f"{template_stem}.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 無法載入 template 配置 {template_stem}: {str(e)}")

        return None
    
    def get_template_regions(self, template_name: str) -> List[Dict]:
        """
        取得 template 的文字區域列表
        
        Args:
            template_name: Template 檔名
            
        Returns:
            區域列表
        """
        config = self.load_template_config(template_name)
        if config and "regions" in config:
            return config["regions"]
        return []
    
    def get_region_by_type(self, template_name: str, region_type: str) -> Optional[Dict]:
        """
        根據類型取得區域（如果有多個，返回第一個）
        
        Args:
            template_name: Template 檔名
            region_type: 區域類型（title/content/cta/conclusion）
            
        Returns:
            區域配置字典，如果不存在則返回 None
        """
        regions = self.get_template_regions(template_name)
        for region in regions:
            if region.get("type") == region_type:
                return region
        return None
    
    def get_regions_by_type(self, template_name: str, region_type: str) -> List[Dict]:
        """
        根據類型取得所有匹配的區域
        
        Args:
            template_name: Template 檔名
            region_type: 區域類型（title/content/cta/conclusion）
            
        Returns:
            區域配置列表
        """
        regions = self.get_template_regions(template_name)
        return [r for r in regions if r.get("type") == region_type]