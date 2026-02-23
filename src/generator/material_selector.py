"""素材選擇器 - 根據需求智能選擇素材"""
from pathlib import Path
from typing import Dict, List, Optional
from src.material_factory import MaterialFactory
from src.material_factory.image_analyzer import ImageAnalyzer


class MaterialSelector:
    """根據 EDM 需求智能選擇適合的素材"""
    
    def __init__(self):
        self.material_factory = MaterialFactory()
        self.image_analyzer = ImageAnalyzer()
    
    def select_background(
        self,
        requirements: Dict,
        preferred_size: Optional[tuple] = None
    ) -> Optional[Dict]:
        """
        選擇背景素材
        
        Args:
            requirements: 生成需求
            preferred_size: 偏好尺寸 (width, height)
            
        Returns:
            選中的背景素材，如果沒有則返回 None
        """
        # 搜尋背景類型的素材
        materials = self.material_factory.search_materials(
            category="背景",
            style=requirements.get("style"),
            color_scheme=requirements.get("color_scheme"),
            mood=requirements.get("mood")
        )
        
        if not materials:
            # 如果沒有背景，嘗試搜尋其他類型
            materials = self.material_factory.search_materials(
                style=requirements.get("style"),
                color_scheme=requirements.get("color_scheme"),
                mood=requirements.get("mood")
            )
        
        if not materials:
            return None
        
        # 如果有偏好尺寸，選擇最接近的
        if preferred_size:
            best_match = None
            min_diff = float('inf')
            pref_width, pref_height = preferred_size
            
            for material in materials:
                try:
                    file_path = Path(material.get("file_path", ""))
                    if not file_path.exists():
                        # 嘗試相對路徑
                        from src.config import BASE_DIR
                        file_path = BASE_DIR / file_path
                    
                    if file_path.exists():
                        image_info = self.image_analyzer.analyze(file_path)
                        width, height = image_info['width'], image_info['height']
                        
                        # 計算尺寸差異（考慮長寬比）
                        aspect_diff = abs((width / height) - (pref_width / pref_height))
                        size_diff = abs(width - pref_width) + abs(height - pref_height)
                        total_diff = aspect_diff * 1000 + size_diff
                        
                        if total_diff < min_diff:
                            min_diff = total_diff
                            best_match = material
                except Exception:
                    continue
            
            return best_match if best_match else materials[0]
        
        return materials[0]
    
    def select_characters(
        self,
        requirements: Dict,
        count: int = 1
    ) -> List[Dict]:
        """
        選擇人物素材
        
        Args:
            requirements: 生成需求
            count: 需要的人物數量
            
        Returns:
            選中的人物素材列表
        """
        materials = self.material_factory.search_materials(
            category="人物",
            style=requirements.get("style"),
            scenario=requirements.get("scenario"),
            mood=requirements.get("mood")
        )
        
        # 如果沒有足夠的人物素材，嘗試放寬條件
        if len(materials) < count:
            # 只根據風格和氛圍搜尋
            additional = self.material_factory.search_materials(
                category="人物",
                style=requirements.get("style"),
                mood=requirements.get("mood")
            )
            # 去重
            seen_paths = {m.get("file_path") for m in materials}
            for m in additional:
                if m.get("file_path") not in seen_paths:
                    materials.append(m)
                    seen_paths.add(m.get("file_path"))
        
        return materials[:count]
    
    def select_decorations(
        self,
        requirements: Dict,
        count: int = 2
    ) -> List[Dict]:
        """
        選擇裝飾素材
        
        Args:
            requirements: 生成需求
            count: 需要的裝飾數量
            
        Returns:
            選中的裝飾素材列表
        """
        materials = self.material_factory.search_materials(
            category="裝飾",
            style=requirements.get("style"),
            color_scheme=requirements.get("color_scheme")
        )
        
        return materials[:count]
