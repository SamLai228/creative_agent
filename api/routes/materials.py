"""素材相關 API 路由"""
import urllib.parse
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from src.material_factory import MaterialFactory
from src.config import ASSETS_DIR
from api.models import (
    MaterialTagResponse,
    MaterialUploadResponse,
    SearchRequest,
    StatsResponse
)
from api.utils import save_uploaded_file, get_relative_path

router = APIRouter(prefix="/api/materials", tags=["materials"])
factory = MaterialFactory()


@router.post("/upload", response_model=MaterialUploadResponse)
async def upload_material(file: UploadFile = File(...)):
    """
    上傳圖片素材
    
    Args:
        file: 上傳的圖片檔案
        
    Returns:
        上傳結果
    """
    # 檢查檔案類型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支援的檔案格式: {file_ext}。支援的格式: {', '.join(allowed_extensions)}"
        )
    
    try:
        # 儲存檔案
        file_path = await save_uploaded_file(file)
        relative_path = get_relative_path(file_path)
        
        return MaterialUploadResponse(
            file_path=relative_path,
            file_name=file_path.name,
            message="檔案上傳成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.post("/tag", response_model=MaterialTagResponse)
async def tag_material(
    file_path: str = Query(..., description="素材檔案路徑（相對於專案根目錄）"),
    force_update: bool = Query(False, description="是否強制更新已存在的標籤")
):
    """
    為素材貼標
    
    Args:
        file_path: 素材檔案路徑
        force_update: 是否強制更新
        
    Returns:
        標籤資訊
    """
    try:
        # URL 解碼
        file_path = urllib.parse.unquote(file_path)
        
        # 構建完整路徑
        # file_path 可能是 "assets/filename.jpg" 或 "filename.jpg"
        if file_path.startswith('assets/'):
            full_path = ASSETS_DIR.parent / file_path
        else:
            # 如果沒有前綴，假設在 assets 目錄下
            full_path = ASSETS_DIR / file_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail=f"檔案不存在: {file_path}")
        
        # 執行貼標
        tags = factory.tag_single_material(full_path, force_update)
        
        return MaterialTagResponse(**tags)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"貼標失敗: {str(e)}")


@router.get("/", response_model=List[MaterialTagResponse])
async def get_all_materials():
    """
    取得所有已貼標素材
    
    Returns:
        素材列表
    """
    try:
        all_tags = factory.tag_db.get_all_tags()
        if not all_tags:
            return []
        
        materials = []
        for file_path, tags in all_tags.items():
            try:
                # 確保 file_path 欄位存在
                if 'file_path' not in tags:
                    tags['file_path'] = file_path
                # 確保 file_name 欄位存在
                if 'file_name' not in tags:
                    tags['file_name'] = Path(file_path).name
                
                material = MaterialTagResponse(**tags)
                materials.append(material)
            except Exception as e:
                # 記錄錯誤但繼續處理其他素材
                print(f"警告: 無法解析素材 {file_path}: {str(e)}")
                continue
        
        return materials
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得素材列表失敗: {str(e)}")


@router.get("/image/{file_path:path}")
async def get_material_image(file_path: str):
    """
    取得素材圖片檔案
    
    Args:
        file_path: 素材檔案路徑
        
    Returns:
        圖片檔案
    """
    try:
        # URL 解碼
        file_path = urllib.parse.unquote(file_path)
        
        # 構建完整路徑
        # file_path 可能是 "assets/filename.jpg" 或 "filename.jpg"
        if file_path.startswith('assets/'):
            full_path = ASSETS_DIR.parent / file_path
        else:
            # 如果沒有前綴，假設在 assets 目錄下
            full_path = ASSETS_DIR / file_path
        
        if not full_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"圖片不存在: {file_path} (嘗試路徑: {full_path})"
            )
        
        # 根據副檔名判斷 MIME 類型
        from pathlib import Path
        ext = Path(full_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
        }
        media_type = mime_types.get(ext, 'image/jpeg')
        
        return FileResponse(
            path=str(full_path),
            media_type=media_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得圖片失敗: {str(e)}")


@router.get("/{file_path:path}", response_model=MaterialTagResponse)
async def get_material_tags(file_path: str):
    """
    取得單一素材的標籤
    
    Args:
        file_path: 素材檔案路徑
        
    Returns:
        標籤資訊
    """
    try:
        # URL 解碼
        file_path = urllib.parse.unquote(file_path)
        
        # 直接使用 file_path 查詢資料庫（資料庫中儲存的是相對路徑）
        tags = factory.tag_db.get_tags(file_path)
        
        if tags is None:
            raise HTTPException(status_code=404, detail="素材標籤不存在")
        
        return MaterialTagResponse(**tags)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得標籤失敗: {str(e)}")


@router.post("/search", response_model=List[MaterialTagResponse])
async def search_materials(search_request: SearchRequest):
    """
    搜尋素材
    
    Args:
        search_request: 搜尋條件
        
    Returns:
        符合條件的素材列表
    """
    try:
        results = factory.search_materials(
            category=search_request.category,
            style=search_request.style,
            scenario=search_request.scenario,
            color_scheme=search_request.color_scheme,
            mood=search_request.mood,
            keywords=search_request.keywords
        )
        
        return [MaterialTagResponse(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜尋失敗: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    取得素材統計資訊
    
    Returns:
        統計資訊
    """
    try:
        stats = factory.get_material_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得統計失敗: {str(e)}")


@router.delete("/{file_path:path}")
async def delete_material(file_path: str):
    """
    刪除素材（檔案和標籤）
    
    Args:
        file_path: 素材檔案路徑
        
    Returns:
        刪除結果
    """
    try:
        # URL 解碼
        file_path = urllib.parse.unquote(file_path)
        
        # 構建完整路徑
        if file_path.startswith('assets/'):
            full_path = ASSETS_DIR.parent / file_path
        else:
            # 如果沒有前綴，假設在 assets 目錄下
            full_path = ASSETS_DIR / file_path
        
        # 檢查檔案是否存在
        file_exists = full_path.exists()
        
        # 從資料庫刪除標籤
        # 資料庫中可能有多種路徑格式，需要嘗試多種匹配方式
        all_tags = factory.tag_db.get_all_tags()
        tag_deleted = False
        deleted_keys = []
        
        # 取得檔案名稱用於匹配
        file_name = Path(file_path).name
        
        # 嘗試匹配多種路徑格式
        possible_keys = [
            file_path,  # 原始路徑
            f"assets/{file_path}",  # 加上 assets/ 前綴
            str(full_path),  # 絕對路徑
        ]
        
        # 如果檔案存在，也加入相對路徑
        if file_exists:
            try:
                rel_path = str(full_path.relative_to(ASSETS_DIR.parent))
                possible_keys.append(rel_path)
            except ValueError:
                pass
        
        # 在資料庫中查找匹配的鍵
        for key in all_tags.keys():
            key_path = Path(key)
            key_name = key_path.name
            
            # 檢查是否匹配任何可能的路徑格式
            if key in possible_keys:
                deleted_keys.append(key)
            # 也檢查檔案名稱是否匹配（處理路徑格式不一致的情況）
            elif key_name == file_name:
                deleted_keys.append(key)
            # 檢查是否為同一個檔案的絕對路徑
            elif str(key_path) == str(full_path):
                deleted_keys.append(key)
        
        # 刪除所有匹配的標籤記錄
        for key in deleted_keys:
            if factory.tag_db.delete_tags(key):
                tag_deleted = True
        
        # 如果沒有找到匹配的鍵，嘗試更寬鬆的匹配
        if not tag_deleted and not deleted_keys:
            # 再次檢查所有標籤，使用更寬鬆的匹配邏輯
            all_tags_again = factory.tag_db.get_all_tags()
            for key in all_tags_again.keys():
                key_path = Path(key)
                # 檢查檔案名稱是否完全匹配
                if key_path.name == Path(file_path).name:
                    if factory.tag_db.delete_tags(key):
                        tag_deleted = True
                        deleted_keys.append(key)
                        break
        
        # 如果檔案存在，刪除檔案
        if file_exists:
            try:
                full_path.unlink()
            except Exception as e:
                # 如果檔案刪除失敗，但標籤已刪除，仍然返回成功
                pass
        
        # 即使檔案不存在，只要標籤被刪除就視為成功
        # 或者檔案被刪除但標籤沒找到，也視為成功（可能標籤已經不存在）
        if not file_exists and not tag_deleted:
            # 最後嘗試：檢查是否真的不存在
            all_tags_final = factory.tag_db.get_all_tags()
            found_in_db = False
            for key in all_tags_final.keys():
                if Path(key).name == Path(file_path).name:
                    found_in_db = True
                    break
            
            if found_in_db:
                raise HTTPException(status_code=500, detail="無法刪除標籤記錄，請檢查資料庫")
            else:
                # 標籤和檔案都不存在，視為已刪除
                tag_deleted = True
        
        return {
            "message": "素材已刪除",
            "file_path": file_path,
            "file_deleted": file_exists,
            "tag_deleted": tag_deleted,
            "deleted_keys": deleted_keys
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")
