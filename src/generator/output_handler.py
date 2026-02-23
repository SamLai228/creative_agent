"""輸出處理器 - 處理 EDM 輸出格式"""
from pathlib import Path
from typing import Optional
from PIL import Image
from src.config import OUTPUT_DIR


class OutputHandler:
    """處理 EDM 輸出"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR / "edm"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_image(
        self,
        image: Image.Image,
        filename: str,
        format: str = "PNG"
    ) -> Path:
        """
        儲存圖片
        
        Args:
            image: PIL Image 物件
            filename: 檔案名稱
            format: 圖片格式 (PNG/JPEG)
            
        Returns:
            輸出檔案路徑
        """
        output_path = self.output_dir / filename
        image.save(output_path, format=format)
        return output_path
    
    def save_pdf(
        self,
        image: Image.Image,
        filename: str
    ) -> Path:
        """
        儲存為 PDF
        
        Args:
            image: PIL Image 物件
            filename: 檔案名稱
            
        Returns:
            輸出檔案路徑
        """
        output_path = self.output_dir / filename
        # 轉換為 RGB 模式（PDF 需要）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(output_path, format='PDF')
        return output_path
