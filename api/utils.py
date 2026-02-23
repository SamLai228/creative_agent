"""API 工具函數"""
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from src.config import ASSETS_DIR


async def save_uploaded_file(file: UploadFile, filename: Optional[str] = None) -> Path:
    """
    儲存上傳的檔案
    
    Args:
        file: 上傳的檔案
        filename: 自訂檔名（可選）
        
    Returns:
        儲存的檔案路徑
    """
    if filename is None:
        filename = file.filename
    
    # 確保檔名安全
    filename = Path(filename).name
    
    # 儲存檔案
    file_path = ASSETS_DIR / filename
    
    # 如果檔案已存在，加上數字後綴
    counter = 1
    original_path = file_path
    while file_path.exists():
        stem = original_path.stem
        suffix = original_path.suffix
        file_path = ASSETS_DIR / f"{stem}_{counter}{suffix}"
        counter += 1
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path


def get_relative_path(file_path: Path) -> str:
    """取得相對路徑字串（相對於專案根目錄）"""
    try:
        # 嘗試相對於 ASSETS_DIR 的父目錄（專案根目錄）
        return str(file_path.relative_to(ASSETS_DIR.parent))
    except ValueError:
        # 如果失敗，返回相對於 ASSETS_DIR 的路徑
        try:
            return str(file_path.relative_to(ASSETS_DIR))
        except ValueError:
            # 如果還是失敗，返回檔案名稱
            return file_path.name
