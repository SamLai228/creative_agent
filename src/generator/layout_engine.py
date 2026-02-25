"""版面配置引擎 - 處理 EDM 版面設計"""
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import platform
from PIL import Image, ImageDraw, ImageFont
from src.config import BASE_DIR, ASSETS_DIR, TEMPLATE_IMAGES_DIR


class LayoutEngine:
    """版面配置引擎 - 處理 EDM 的視覺版面"""
    
    def __init__(self, canvas_width: int = 1200, canvas_height: int = 800):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.chinese_font_path = self._find_chinese_font()
    
    def _find_chinese_font(self) -> Optional[str]:
        """
        尋找系統中可用的中文字體
        
        Returns:
            字體檔案路徑，如果找不到則返回 None
        """
        system = platform.system()
        
        # macOS 常見中文字體路徑
        if system == "Darwin":
            font_paths = [
                "/System/Library/Fonts/Supplemental/PingFang.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/Library/Fonts/Microsoft/msjh.ttf",  # 微軟正黑體（如果安裝）
                "/System/Library/Fonts/STHeiti Light.ttc",  # 華文黑體
                "/System/Library/Fonts/STHeiti Medium.ttc",
            ]
        # Linux 常見中文字體路徑
        elif system == "Linux":
            font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
            ]
        # Windows 常見中文字體路徑
        else:  # Windows
            font_paths = [
                "C:/Windows/Fonts/msjh.ttc",  # 微軟正黑體
                "C:/Windows/Fonts/simsun.ttc",  # 新細明體
                "C:/Windows/Fonts/simhei.ttf",  # 黑體
            ]
        
        # 嘗試找到第一個存在的字體
        for font_path in font_paths:
            if Path(font_path).exists():
                return font_path
        
        return None
    
    def create_canvas(
        self,
        background_color: Tuple[int, int, int] = (255, 255, 255),
        template_path: Optional[str] = None
    ) -> Image.Image:
        """
        建立畫布
        
        Args:
            background_color: 背景顏色 RGB（當沒有 template 時使用）
            template_path: EDM template 圖片路徑（可選）
            
        Returns:
            PIL Image 物件（如果使用 template，會更新 canvas 尺寸為 template 的尺寸）
        """
        # 如果有提供 template，使用 template 作為底圖
        if template_path:
            try:
                # 解析 template 路徑
                template = Path(template_path)
                if not template.exists():
                    # 嘗試在 TEMPLATE_IMAGES_DIR 中尋找
                    if not template.is_absolute():
                        template = TEMPLATE_IMAGES_DIR / template
                    else:
                        template = Path(template_path)
                
                if template.exists():
                    # 載入 template 圖片
                    template_img = Image.open(template)
                    
                    # 轉換為 RGB（如果需要）
                    if template_img.mode != 'RGB':
                        template_img = template_img.convert('RGB')
                    
                    # 使用 template 的原始尺寸，更新 canvas 尺寸
                    self.canvas_width = template_img.width
                    self.canvas_height = template_img.height
                    
                    print(f"使用 Template 尺寸: {self.canvas_width} x {self.canvas_height}")
                    
                    return template_img
                else:
                    print(f"警告: Template 圖片不存在: {template_path}，使用預設背景色")
            except Exception as e:
                print(f"警告: 無法載入 Template 圖片: {str(e)}，使用預設背景色")
        
        # 如果沒有 template 或載入失敗，使用純色背景
        return Image.new('RGB', (self.canvas_width, self.canvas_height), background_color)
    
    def place_background(
        self,
        canvas: Image.Image,
        background_image_path: str,
        opacity: float = 1.0
    ) -> Image.Image:
        """
        放置背景圖片
        
        Args:
            canvas: 畫布
            background_image_path: 背景圖片路徑
            opacity: 透明度 (0.0-1.0)
            
        Returns:
            更新後的畫布
        """
        try:
            # 解析路徑
            bg_path = Path(background_image_path)
            if not bg_path.exists():
                # 嘗試相對路徑
                if bg_path.is_absolute():
                    bg_path = Path(background_image_path)
                else:
                    bg_path = BASE_DIR / bg_path
                    if not bg_path.exists():
                        bg_path = ASSETS_DIR / Path(background_image_path).name
            
            if not bg_path.exists():
                return canvas
            
            # 載入背景圖片
            bg_image = Image.open(bg_path)
            
            # 轉換為 RGB（如果需要）
            if bg_image.mode != 'RGB':
                bg_image = bg_image.convert('RGB')
            
            # 調整尺寸以符合畫布
            bg_image = bg_image.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
            
            # 如果透明度小於 1.0，需要混合
            if opacity < 1.0:
                # 創建一個臨時畫布來混合
                temp_canvas = Image.new('RGB', (self.canvas_width, self.canvas_height), (255, 255, 255))
                temp_canvas.paste(bg_image, (0, 0))
                
                # 使用 alpha 混合
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(temp_canvas)
                bg_image = enhancer.enhance(opacity)
                
                # 混合到原畫布
                canvas = Image.blend(canvas, bg_image, opacity)
            else:
                canvas.paste(bg_image, (0, 0))
            
            return canvas
        except Exception as e:
            print(f"警告: 無法載入背景圖片 {background_image_path}: {str(e)}")
            return canvas
    
    def place_text(
        self,
        canvas: Image.Image,
        text: str,
        position: Tuple[int, int],
        font_size: int = 48,
        color: Tuple[int, int, int] = (0, 0, 0),
        font_path: Optional[str] = None,
        max_width: Optional[int] = None,
        bold: bool = False
    ) -> Image.Image:
        """
        放置文字
        
        Args:
            canvas: 畫布
            text: 文字內容
            position: 位置 (x, y)
            font_size: 字體大小
            color: 文字顏色 RGB
            font_path: 字體路徑（可選）
            max_width: 最大寬度（自動換行）
            
        Returns:
            更新後的畫布
        """
        try:
            draw = ImageDraw.Draw(canvas)
            
            # 嘗試載入字體
            try:
                if font_path and Path(font_path).exists():
                    font = ImageFont.truetype(font_path, font_size)
                elif self.chinese_font_path:
                    # 使用找到的中文字體；bold=True 嘗試 Semibold (index=4) 再 Medium (index=1)
                    if bold:
                        try:
                            font = ImageFont.truetype(self.chinese_font_path, font_size, index=4)
                        except Exception:
                            try:
                                font = ImageFont.truetype(self.chinese_font_path, font_size, index=1)
                            except Exception:
                                font = ImageFont.truetype(self.chinese_font_path, font_size)
                    else:
                        font = ImageFont.truetype(self.chinese_font_path, font_size)
                else:
                    # 嘗試使用系統預設中文字體
                    try:
                        # macOS 的 PingFang
                        if platform.system() == "Darwin":
                            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/PingFang.ttc", font_size)
                        else:
                            font = ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
            except Exception as e:
                print(f"警告: 無法載入字體，使用預設字體: {str(e)}")
                font = ImageFont.load_default()
            
            # 如果需要自動換行（支援中文與顯式 \n）
            if max_width:
                lines = []
                current_line = ""

                for char in text:
                    # 遇到顯式換行符，強制斷行
                    if char == "\n":
                        lines.append(current_line)
                        current_line = ""
                        continue

                    test_line = current_line + char
                    try:
                        bbox = draw.textbbox((0, 0), test_line, font=font)
                        text_width = bbox[2] - bbox[0]
                    except:
                        try:
                            text_width = draw.textlength(test_line, font=font)
                        except:
                            text_width = len(test_line) * (font_size // 2)

                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = char

                if current_line:
                    lines.append(current_line)
                
                # 繪製多行文字
                y_offset = 0
                line_height = font_size + 10
                for line in lines:
                    draw.text((position[0], position[1] + y_offset), line, fill=color, font=font)
                    y_offset += line_height
            else:
                draw.text(position, text, fill=color, font=font)
            
            return canvas
        except Exception as e:
            print(f"警告: 無法放置文字: {str(e)}")
            return canvas
    
    def place_image(
        self,
        canvas: Image.Image,
        image_path: str,
        position: Tuple[int, int],
        size: Optional[Tuple[int, int]] = None,
        anchor: str = "lt"  # lt (left-top), center, etc.
    ) -> Image.Image:
        """
        放置圖片素材
        
        Args:
            canvas: 畫布
            image_path: 圖片路徑
            position: 位置 (x, y)
            size: 尺寸 (width, height)，如果為 None 則使用原始尺寸
            anchor: 錨點位置 (lt=左上, center=中心)
            
        Returns:
            更新後的畫布
        """
        try:
            # 解析路徑
            img_path = Path(image_path)
            if not img_path.exists():
                # 嘗試相對路徑
                if img_path.is_absolute():
                    img_path = Path(image_path)
                else:
                    img_path = BASE_DIR / img_path
                    if not img_path.exists():
                        img_path = ASSETS_DIR / Path(image_path).name
            
            if not img_path.exists():
                print(f"警告: 圖片不存在: {image_path}")
                return canvas
            
            # 載入圖片
            img = Image.open(img_path)
            
            # 轉換為 RGBA 以支援透明度
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 調整尺寸
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # 計算實際位置（根據錨點）
            x, y = position
            if anchor == "center":
                x -= img.width // 2
                y -= img.height // 2
            elif anchor == "rt":  # right-top
                x -= img.width
            elif anchor == "lb":  # left-bottom
                y -= img.height
            elif anchor == "rb":  # right-bottom
                x -= img.width
                y -= img.height
            
            # 確保位置在畫布範圍內
            x = max(0, min(x, canvas.width - img.width))
            y = max(0, min(y, canvas.height - img.height))
            
            # 貼上圖片（支援透明度）
            if img.mode == 'RGBA':
                canvas.paste(img, (x, y), img)
            else:
                canvas.paste(img, (x, y))
            
            return canvas
        except Exception as e:
            print(f"警告: 無法放置圖片 {image_path}: {str(e)}")
            return canvas
    
    def place_text_in_region(
        self,
        canvas: Image.Image,
        text: str,
        region: Dict
    ) -> Image.Image:
        """
        在指定區域內放置文字
        
        Args:
            canvas: 畫布
            text: 文字內容
            region: 區域配置字典，包含：
                - bbox: [x, y, width, height] 邊界框
                - anchor: 對齊方式（lt/center/rt）
                - font_size: 字體大小
                - color: 文字顏色 [R, G, B]
                - max_width: 最大寬度（可選）
                
        Returns:
            更新後的畫布
        """
        try:
            # 解析區域配置
            bbox = region.get("bbox", [0, 0, 100, 100])
            if len(bbox) != 4:
                print(f"警告: 無效的 bbox: {bbox}")
                return canvas
            
            x, y, width, height = bbox
            anchor = region.get("anchor", "lt")
            font_size = region.get("font_size", 32)
            bold = region.get("bold", False)
            color = tuple(region.get("color", [0, 0, 0]))
            max_width = region.get("max_width", width)
            
            # 計算文字位置（根據 anchor）
            if anchor == "center":
                # 居中對齊：先計算換行後的實際行數，用於正確垂直置中
                center_x = x + width // 2
                center_y = y + height // 2
                try:
                    _draw = ImageDraw.Draw(canvas)
                    try:
                        if self.chinese_font_path:
                            _font = ImageFont.truetype(self.chinese_font_path, font_size)
                        else:
                            _font = ImageFont.load_default()
                    except Exception:
                        _font = ImageFont.load_default()

                    # 計算換行後的實際行數（與 place_text 的換行邏輯一致）
                    n_lines = 1
                    if max_width:
                        current_line = ""
                        line_count = 0
                        for char in text:
                            if char == "\n":
                                line_count += 1
                                current_line = ""
                                continue
                            test_line = current_line + char
                            try:
                                tb = _draw.textbbox((0, 0), test_line, font=_font)
                                tw = tb[2] - tb[0]
                            except Exception:
                                tw = len(test_line) * (font_size // 2)
                            if tw <= max_width:
                                current_line = test_line
                            else:
                                line_count += 1
                                current_line = char
                        line_count += 1  # 最後一行
                        n_lines = max(1, line_count)

                    total_text_h = (n_lines - 1) * (font_size + 10) + font_size
                    text_bbox = _draw.textbbox((0, 0), text, font=_font)
                    text_w = text_bbox[2] - text_bbox[0]
                    if max_width:
                        text_w = min(text_w, max_width)
                    text_x = center_x - text_w // 2
                    text_y = center_y - total_text_h // 2
                except Exception:
                    text_x = center_x
                    text_y = center_y
            elif anchor == "rt":
                # 右對齊：從區域右側開始
                text_x = x + width
                text_y = y
            else:
                # 左對齊（預設）
                text_x = x
                text_y = y

            # 使用現有的 place_text 方法
            return self.place_text(
                canvas,
                text,
                (text_x, text_y),
                font_size=font_size,
                color=color,
                max_width=max_width,
                bold=bold
            )
            
        except Exception as e:
            print(f"警告: 無法在區域內放置文字: {str(e)}")
            return canvas
