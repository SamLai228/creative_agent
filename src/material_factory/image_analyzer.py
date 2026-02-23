"""圖片分析模組 - 提取圖片基本資訊"""
import base64
from pathlib import Path
from PIL import Image
from typing import Dict, Optional


class ImageAnalyzer:
    """圖片分析器，用於提取圖片的基本視覺資訊"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    def analyze(self, image_path: Path) -> Dict:
        """
        分析圖片並返回基本資訊
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            包含圖片基本資訊的字典
        """
        if not image_path.exists():
            raise FileNotFoundError(f"圖片不存在: {image_path}")
        
        if image_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"不支援的圖片格式: {image_path.suffix}")
        
        try:
            with Image.open(image_path) as img:
                # 轉換為 RGB（如果是 RGBA 或其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 提取基本資訊
                width, height = img.size
                format_name = img.format or image_path.suffix[1:].upper()
                
                # 計算主要顏色（簡化版 - 取平均色）
                colors = img.getcolors(maxcolors=256*256*256)
                if colors:
                    # 計算加權平均色
                    total_pixels = sum(count for count, _ in colors)
                    r_sum = g_sum = b_sum = 0
                    for count, (r, g, b) in colors:
                        r_sum += r * count
                        g_sum += g * count
                        b_sum += b * count
                    
                    avg_r = int(r_sum / total_pixels)
                    avg_g = int(g_sum / total_pixels)
                    avg_b = int(b_sum / total_pixels)
                    dominant_color = (avg_r, avg_g, avg_b)
                else:
                    dominant_color = (128, 128, 128)
                
                return {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": img.mode,
                    "aspect_ratio": round(width / height, 2) if height > 0 else 0,
                    "dominant_color": dominant_color,
                    "file_size": image_path.stat().st_size,
                }
        except Exception as e:
            raise ValueError(f"無法讀取圖片: {str(e)}")
    
    def encode_image_base64(self, image_path: Path) -> str:
        """
        將圖片編碼為 base64 字串（用於 API 呼叫）
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            base64 編碼的字串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_mime_type(self, image_path: Path) -> str:
        """根據副檔名返回 MIME 類型"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
        }
        return mime_types.get(image_path.suffix.lower(), 'image/jpeg')
