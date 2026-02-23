"""EDM 生成相關 API 路由"""
from pathlib import Path
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from src.generator import EDMGenerator
from api.models import (
    GenerationRequest,
    GenerationResponse,
    GenerationHistoryResponse
)

router = APIRouter(prefix="/api/generation", tags=["generation"])
generator = EDMGenerator()


@router.post("/generate", response_model=GenerationResponse)
async def generate_edm(request: GenerationRequest):
    """
    根據需求生成 EDM
    
    Args:
        request: 生成請求，包含需求資訊
        
    Returns:
        生成結果
    """
    try:
        # 轉換請求為生成器需要的格式
        requirements = {
            "title": request.title,
            "description": request.description,
            # 文案生成相關
            "product_name": request.product_name,
            "promotion_type": request.promotion_type,
            "key_message": request.key_message,
            "call_to_action": request.call_to_action,
            "product_info": request.product_info,
            "target_audience": request.target_audience,
            "tone": request.tone,
            # 素材選擇相關
            "category": request.category,
            "style": request.style,
            "scenario": request.scenario,
            "color_scheme": request.color_scheme,
            "mood": request.mood,
            "keywords": request.keywords,
            "layout": request.layout,
            # Template 相關
            "template": request.template,
        }
        
        # 生成 EDM
        result = generator.generate(
            requirements=requirements,
            output_format=request.output_format or "png"
        )
        
        return GenerationResponse(
            output_path=str(result["output_path"]),
            materials_used=result.get("materials_used", []),
            layout=result.get("layout", "default"),
            message="EDM 生成成功"
        )
        
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail="生成功能尚未實作，請稍後再試"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成失敗: {str(e)}"
        )


@router.get("/layouts", response_model=List[str])
async def get_available_layouts():
    """
    取得可用的版面配置列表
    
    Returns:
        版面配置名稱列表
    """
    try:
        from src.generator.template_engine import TemplateEngine
        engine = TemplateEngine()
        return engine.get_available_layouts()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得版面配置失敗: {str(e)}"
        )


@router.get("/preview-materials")
async def preview_materials(
    category: Optional[str] = None,
    style: Optional[List[str]] = None,
    scenario: Optional[List[str]] = None,
    color_scheme: Optional[str] = None,
    mood: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None
):
    """
    預覽根據條件會選擇的素材（不實際生成）
    
    Returns:
        符合條件的素材列表
    """
    try:
        requirements = {
            "category": category,
            "style": style,
            "scenario": scenario,
            "color_scheme": color_scheme,
            "mood": mood,
            "keywords": keywords,
        }
        
        materials = generator.select_materials(requirements)
        return {
            "count": len(materials),
            "materials": materials
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"預覽素材失敗: {str(e)}"
        )


@router.post("/generate-copy")
async def generate_copy(request: Dict):
    """
    生成 EDM 文案（標題和內文）
    
    這個端點可以獨立使用，只生成文案而不生成完整的 EDM
    
    Args:
        request: 包含生成需求的字典，可包含：
            - product_name: 產品/服務名稱
            - promotion_type: 促銷類型
            - key_message: 主要訊息
            - call_to_action: 行動呼籲
            - product_info: 產品資訊
            - target_audience: 目標受眾
            - tone: 文案風格
    
    Returns:
        生成的文案（標題和內文）
    """
    try:
        from src.generator import Copywriter
        copywriter = Copywriter()
        
        result = copywriter.generate_copy(
            requirements=request,
            product_info=request.get("product_info"),
            target_audience=request.get("target_audience"),
            tone=request.get("tone")
        )
        
        return {
            "title": result["title"],
            "content": result["content"],
            "call_to_action": result.get("call_to_action", []),
            "tone": result.get("tone", ""),
            "key_points": result.get("key_points", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文案生成失敗: {str(e)}"
        )


@router.post("/detect-template-regions")
async def detect_template_regions(template_name: str = Query(..., description="Template 檔名")):
    """
    手動觸發 template 區域識別
    
    這個端點會使用 Vision API 分析 template 圖片，識別出所有文字區域
    （標題、內文、CTA 按鈕等），並保存配置檔案。
    
    Args:
        template_name: Template 檔名（例如：edm_template_01.jpeg）
        
    Returns:
        識別結果配置
    """
    try:
        from src.generator.template_engine import TemplateEngine
        engine = TemplateEngine()
        
        # 識別並保存區域配置
        config = engine.detect_and_save_regions(template_name)
        
        return {
            "template_name": config.get("template_name"),
            "template_image": config.get("template_image"),
            "canvas_size": config.get("canvas_size"),
            "regions_count": len(config.get("regions", [])),
            "regions": config.get("regions", []),
            "message": f"Template 區域識別完成，共識別 {len(config.get('regions', []))} 個區域"
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Template 圖片不存在: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"區域識別失敗: {str(e)}"
        )


@router.get("/template-regions")
async def get_template_regions(template_name: str = Query(..., description="Template 檔名")):
    """
    取得 template 的區域配置
    
    Args:
        template_name: Template 檔名
        
    Returns:
        Template 區域配置
    """
    try:
        from src.generator.template_engine import TemplateEngine
        engine = TemplateEngine()
        
        config = engine.load_template_config(template_name, auto_detect=False)
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Template 配置不存在: {template_name}。請先使用 /detect-template-regions 端點進行識別。"
            )
        
        return {
            "template_name": config.get("template_name"),
            "template_image": config.get("template_image"),
            "canvas_size": config.get("canvas_size"),
            "regions_count": len(config.get("regions", [])),
            "regions": config.get("regions", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得 template 配置失敗: {str(e)}"
        )
