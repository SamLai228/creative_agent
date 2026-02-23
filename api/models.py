"""Pydantic 資料模型"""
from typing import List, Optional, Dict
from pydantic import BaseModel


class MaterialTagResponse(BaseModel):
    """素材標籤回應模型"""
    file_path: str
    file_name: str
    category: str
    style: List[str]
    scenario: List[str]
    color_scheme: str
    mood: List[str]
    usage_scope: str
    keywords: List[str]
    updated_at: Optional[str] = None


class MaterialUploadResponse(BaseModel):
    """上傳回應模型"""
    file_path: str
    file_name: str
    message: str


class SearchRequest(BaseModel):
    """搜尋請求模型"""
    category: Optional[str] = None
    style: Optional[List[str]] = None
    scenario: Optional[List[str]] = None
    color_scheme: Optional[str] = None
    mood: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class StatsResponse(BaseModel):
    """統計回應模型"""
    total_materials: int
    by_category: dict
    by_style: dict
    by_scenario: dict
    by_color_scheme: dict


class GenerationRequest(BaseModel):
    """EDM 生成請求模型"""
    title: Optional[str] = None  # 改為可選，如果沒有則自動生成
    description: Optional[str] = None  # 改為可選，如果沒有則自動生成
    
    # 文案生成相關欄位（可選）
    product_name: Optional[str] = None
    promotion_type: Optional[str] = None
    key_message: Optional[str] = None
    call_to_action: Optional[str] = None
    product_info: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    
    # 素材選擇相關欄位
    category: Optional[str] = None
    style: Optional[List[str]] = None
    scenario: Optional[List[str]] = None
    color_scheme: Optional[str] = None
    mood: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    layout: Optional[str] = None
    template: Optional[str] = None  # EDM template 圖片檔名（放在 templates/images/ 目錄下）
    output_format: Optional[str] = "png"  # png 或 pdf


class GenerationResponse(BaseModel):
    """EDM 生成回應模型"""
    output_path: str
    materials_used: List[Dict]
    layout: str
    message: str


class GenerationHistoryResponse(BaseModel):
    """生成歷史回應模型"""
    id: str
    created_at: str
    requirements: Dict
    output_path: str
