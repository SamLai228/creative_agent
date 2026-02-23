"""EDM 生成器 - 根據需求生成行銷 EDM"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from src.material_factory import MaterialFactory
from src.config import OUTPUT_DIR, ASSETS_DIR
from .material_selector import MaterialSelector
from .template_engine import TemplateEngine
from .layout_engine import LayoutEngine
from .output_handler import OutputHandler
from .copywriter import Copywriter


class EDMGenerator:
    """EDM 生成器 - 根據使用者需求生成行銷 EDM"""
    
    def __init__(self):
        self.material_factory = MaterialFactory()
        self.material_selector = MaterialSelector()
        self.template_engine = TemplateEngine()
        self.layout_engine = LayoutEngine(canvas_width=1200, canvas_height=800)
        self.output_handler = OutputHandler()
        self.copywriter = Copywriter()
        self.output_dir = OUTPUT_DIR / "edm"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        requirements: Dict,
        output_format: str = "png"
    ) -> Dict:
        """
        根據需求生成 EDM
        
        Args:
            requirements: 生成需求字典，包含：
                - title: 標題文字
                - description: 描述文字
                - category: 素材類型偏好
                - style: 風格偏好
                - scenario: 情境偏好
                - color_scheme: 色系偏好
                - mood: 氛圍偏好
                - keywords: 關鍵字偏好
                - layout: 版面配置（可選）
            output_format: 輸出格式（png/pdf）
            
        Returns:
            生成結果字典，包含：
                - output_path: 輸出檔案路徑
                - materials_used: 使用的素材列表
                - layout: 使用的版面配置
        """
        # 0. 如果沒有提供標題和內文，自動生成文案
        if not requirements.get("title") or not requirements.get("description"):
            print("正在生成文案...")
            try:
                copy_result = self.copywriter.generate_copy(
                    requirements=requirements,
                    product_info=requirements.get("product_info"),
                    target_audience=requirements.get("target_audience"),
                    tone=requirements.get("tone")
                )
                
                # 如果原本沒有提供，則使用生成的文案
                if not requirements.get("title"):
                    requirements["title"] = copy_result["title"]
                    print(f"  生成標題: {copy_result['title']}")
                if not requirements.get("description"):
                    requirements["description"] = copy_result["content"]
                    print(f"  生成內文: {copy_result['content']}")
                
                # 保存完整的文案結果，供後續使用（特別是 CTA 和結語）
                requirements["_copy_result"] = copy_result
            except Exception as e:
                print(f"警告: 文案生成失敗，使用預設文案: {str(e)}")
                if not requirements.get("title"):
                    requirements["title"] = "完善保障，守護未來"
                if not requirements.get("description"):
                    requirements["description"] = "立即了解保障方案，為您與家人規劃最適合的保險計畫"
        
        # 1. 選擇版面配置
        layout_name = requirements.get("layout", "centered")
        if layout_name not in self.template_engine.get_available_layouts():
            layout_name = "centered"
        
        layout = self.template_engine.load_layout(layout_name)
        
        # 2. 選擇素材
        background = self.material_selector.select_background(
            requirements,
            preferred_size=(self.layout_engine.canvas_width, self.layout_engine.canvas_height)
        )
        
        characters = self.material_selector.select_characters(
            requirements,
            count=1
        )
        
        decorations = self.material_selector.select_decorations(
            requirements,
            count=min(2, len(layout.get("decoration_positions", [])))
        )
        
        # 收集使用的素材
        materials_used = []
        if background:
            materials_used.append(background)
        materials_used.extend(characters)
        materials_used.extend(decorations)
        
        # 3. 建立畫布（優先使用 template，如果沒有則使用背景素材）
        template_path = requirements.get("template")
        template_config = None
        
        if template_path:
            # 使用 template 作為底圖（會自動更新 canvas 尺寸）
            canvas = self.layout_engine.create_canvas(template_path=template_path)
            
            # 載入 template 配置
            template_config = self.template_engine.load_template_config(template_path, auto_detect=True)
            
            if template_config:
                # 使用 template 區域放置文字
                canvas = self._place_text_in_template_regions(canvas, requirements, template_config)
            else:
                # 如果無法載入配置，回退到傳統 layout
                layout = self._scale_layout_to_canvas(layout, self.layout_engine.canvas_width, self.layout_engine.canvas_height)
                canvas = self._place_text_with_layout(canvas, requirements, layout)
        else:
            # 使用純色背景
            canvas = self.layout_engine.create_canvas(background_color=(255, 255, 255))
            
            # 4. 放置背景素材（如果沒有使用 template）
            if background:
                bg_path = background.get("file_path", "")
                canvas = self.layout_engine.place_background(canvas, bg_path, opacity=0.8)
            
            # 使用傳統 layout 放置文字
            canvas = self._place_text_with_layout(canvas, requirements, layout)
        
        # 6. 放置人物素材
        if characters and len(characters) > 0:
            char = characters[0]
            char_path = char.get("file_path", "")
            char_pos = tuple(layout.get("character_position", (600, 500)))
            char_anchor = layout.get("character_anchor", "center")
            char_size = tuple(layout.get("character_size", (300, 300)))
            canvas = self.layout_engine.place_image(
                canvas,
                char_path,
                char_pos,
                size=char_size,
                anchor=char_anchor
            )
        
        # 7. 放置裝飾素材（只有在沒有使用 template 區域時才放置）
        if not template_config:
            decoration_positions = layout.get("decoration_positions", [])
            decoration_sizes = layout.get("decoration_sizes", [])
            
            for i, decoration in enumerate(decorations[:len(decoration_positions)]):
                if i < len(decoration_positions):
                    dec_path = decoration.get("file_path", "")
                    dec_pos = tuple(decoration_positions[i])
                    dec_size = tuple(decoration_sizes[i]) if i < len(decoration_sizes) else (100, 100)
                    canvas = self.layout_engine.place_image(
                        canvas,
                        dec_path,
                        dec_pos,
                        size=dec_size,
                        anchor="lt"
                    )
        
        # 8. 儲存輸出
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format.lower() == "pdf":
            filename = f"edm_{timestamp}.pdf"
            output_path = self.output_handler.save_pdf(canvas, filename)
        else:
            filename = f"edm_{timestamp}.png"
            output_path = self.output_handler.save_image(canvas, filename, format="PNG")
        
        return {
            "output_path": str(output_path),
            "materials_used": [
                {
                    "file_path": m.get("file_path"),
                    "file_name": m.get("file_name"),
                    "category": m.get("category")
                }
                for m in materials_used
            ],
            "layout": layout_name,
            "canvas_size": (self.layout_engine.canvas_width, self.layout_engine.canvas_height)
        }
    
    def _place_text_in_template_regions(
        self,
        canvas,
        requirements: Dict,
        template_config: Dict
    ):
        """
        根據 template 區域配置放置文字
        
        Args:
            canvas: 畫布
            requirements: 生成需求（包含文案）
            template_config: Template 配置
            
        Returns:
            更新後的畫布
        """
        regions = template_config.get("regions", [])
        
        # 取得文案內容
        title = requirements.get("title", "")
        description = requirements.get("description", "")
        copy_result = requirements.get("_copy_result")  # 從自動生成的文案中取得
        
        # 映射文案到區域
        # 1. 標題區域
        title_region = None
        for region in regions:
            if region.get("type") == "title":
                title_region = region
                break
        
        if title_region and title:
            canvas = self.layout_engine.place_text_in_region(canvas, title, title_region)
        
        # 2. 內文區域
        content_region = None
        for region in regions:
            if region.get("type") == "content":
                content_region = region
                break
        
        if content_region and description:
            canvas = self.layout_engine.place_text_in_region(canvas, description, content_region)
        
        # 3. CTA 區域（可能有多個）
        cta_regions = [r for r in regions if r.get("type") == "cta"]
        cta_texts = []
        
        # 從 copy_result 或 requirements 中取得 CTA
        if copy_result and isinstance(copy_result.get("call_to_action"), list):
            cta_texts = copy_result["call_to_action"]
        elif requirements.get("call_to_action"):
            if isinstance(requirements["call_to_action"], list):
                cta_texts = requirements["call_to_action"]
            else:
                cta_texts = [requirements["call_to_action"]]
        
        # 放置 CTA（按順序對應到 CTA 區域）
        for i, cta_region in enumerate(cta_regions):
            if i < len(cta_texts) and cta_texts[i]:
                canvas = self.layout_engine.place_text_in_region(canvas, cta_texts[i], cta_region)
        
        # 4. 結語區域（可選）
        conclusion_region = None
        for region in regions:
            if region.get("type") == "conclusion":
                conclusion_region = region
                break
        
        if conclusion_region:
            conclusion_text = ""
            if copy_result and copy_result.get("conclusion"):
                conclusion_text = copy_result["conclusion"]
            elif requirements.get("conclusion"):
                conclusion_text = requirements["conclusion"]
            
            if conclusion_text:
                canvas = self.layout_engine.place_text_in_region(canvas, conclusion_text, conclusion_region)
        
        return canvas
    
    def _place_text_with_layout(
        self,
        canvas,
        requirements: Dict,
        layout: Dict
    ):
        """
        使用傳統 layout 配置放置文字
        
        Args:
            canvas: 畫布
            requirements: 生成需求
            layout: Layout 配置
            
        Returns:
            更新後的畫布
        """
        title = requirements.get("title", "")
        description = requirements.get("description", "")
        
        if title:
            title_pos = tuple(layout.get("title_position", (600, 200)))
            title_anchor = layout.get("title_anchor", "center")
            title_font_size = layout.get("title_font_size", 64)
            canvas = self.layout_engine.place_text(
                canvas,
                title,
                title_pos,
                font_size=title_font_size,
                color=(0, 0, 0),
                max_width=layout.get("description_max_width", 800)
            )
        
        if description:
            desc_pos = tuple(layout.get("description_position", (600, 300)))
            desc_anchor = layout.get("description_anchor", "center")
            desc_max_width = layout.get("description_max_width", 800)
            canvas = self.layout_engine.place_text(
                canvas,
                description,
                desc_pos,
                font_size=32,
                color=(50, 50, 50),
                max_width=desc_max_width
            )
        
        return canvas
    
    def _scale_layout_to_canvas(self, layout: Dict, actual_width: int, actual_height: int) -> Dict:
        """
        根據實際 canvas 尺寸調整 layout 位置和尺寸
        
        Args:
            layout: 原始 layout 配置（基於 1200x800）
            actual_width: 實際 canvas 寬度
            actual_height: 實際 canvas 高度
            
        Returns:
            調整後的 layout 配置
        """
        # 預設基準尺寸
        default_width = 1200
        default_height = 800
        
        # 計算縮放比例
        scale_x = actual_width / default_width
        scale_y = actual_height / default_height
        
        # 如果尺寸相同，不需要調整
        if scale_x == 1.0 and scale_y == 1.0:
            return layout
        
        # 複製 layout 以避免修改原始配置
        scaled_layout = layout.copy()
        
        # 調整位置（tuple 或 list）
        def scale_position(pos):
            if isinstance(pos, (tuple, list)) and len(pos) >= 2:
                return (int(pos[0] * scale_x), int(pos[1] * scale_y))
            return pos
        
        # 調整尺寸
        def scale_size(size):
            if isinstance(size, (tuple, list)) and len(size) >= 2:
                return (int(size[0] * scale_x), int(size[1] * scale_y))
            return size
        
        # 調整標題位置
        if "title_position" in scaled_layout:
            scaled_layout["title_position"] = scale_position(scaled_layout["title_position"])
        
        # 調整描述位置
        if "description_position" in scaled_layout:
            scaled_layout["description_position"] = scale_position(scaled_layout["description_position"])
        
        # 調整描述最大寬度
        if "description_max_width" in scaled_layout:
            scaled_layout["description_max_width"] = int(scaled_layout["description_max_width"] * scale_x)
        
        # 調整人物位置和尺寸
        if "character_position" in scaled_layout:
            scaled_layout["character_position"] = scale_position(scaled_layout["character_position"])
        if "character_size" in scaled_layout:
            scaled_layout["character_size"] = scale_size(scaled_layout["character_size"])
        
        # 調整裝飾位置和尺寸
        if "decoration_positions" in scaled_layout:
            scaled_layout["decoration_positions"] = [
                scale_position(pos) for pos in scaled_layout["decoration_positions"]
            ]
        if "decoration_sizes" in scaled_layout:
            scaled_layout["decoration_sizes"] = [
                scale_size(size) for size in scaled_layout["decoration_sizes"]
            ]
        
        # 調整字體大小（可選，使用較小的縮放比例以保持可讀性）
        if "title_font_size" in scaled_layout:
            # 字體大小使用平均縮放比例
            avg_scale = (scale_x + scale_y) / 2
            scaled_layout["title_font_size"] = int(scaled_layout["title_font_size"] * avg_scale)
        
        return scaled_layout
    
    def select_materials(self, requirements: Dict) -> List[Dict]:
        """
        根據需求選擇適合的素材
        
        Args:
            requirements: 生成需求字典
            
        Returns:
            選中的素材列表
        """
        # 使用素材工廠的搜尋功能
        materials = self.material_factory.search_materials(
            category=requirements.get("category"),
            style=requirements.get("style"),
            scenario=requirements.get("scenario"),
            color_scheme=requirements.get("color_scheme"),
            mood=requirements.get("mood"),
            keywords=requirements.get("keywords")
        )
        
        return materials
