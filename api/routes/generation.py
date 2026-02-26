"""EDM 生成相關 API 路由"""
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
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




@router.post("/generate-copy-for-template")
async def generate_copy_for_template(request: Dict):
    """
    根據 template 的 region 配置生成文案，每個 region 各自有精確字數上限。

    Args:
        request: 包含以下欄位：
            - template_name: Template 檔名（例：edm_template_01.jpeg），必填
            - product_name: 產品/服務名稱
            - promotion_type: 促銷類型
            - key_message: 主要訊息
            - target_audience: 目標受眾
            - tone: 文案風格

    Returns:
        dict: { region_id: text } — 每個 region 對應一段獨立文案
    """
    template_name = request.get("template_name")
    if not template_name:
        raise HTTPException(status_code=422, detail="缺少必填欄位：template_name")

    try:
        from src.generator.template_engine import TemplateEngine
        from src.generator.copywriter import Copywriter

        # 載入 template region 配置（若不存在會拋 404）
        engine = TemplateEngine()
        config = engine.load_template_config(template_name)
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 template 配置：{template_name}。請先呼叫 /detect-template-regions 或 /detect-regions-from-reference。",
            )

        requirements = {k: v for k, v in request.items() if k != "template_name"}

        copywriter = Copywriter()
        copy_map = copywriter.generate_copy_for_template(config, requirements)

        return {
            "template_name": config.get("template_name"),
            "regions_count": len(copy_map),
            "copy": copy_map,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template 文案生成失敗: {str(e)}")


@router.post("/detect-regions-from-reference")
async def detect_regions_from_reference(
    template_name: str = Query(..., description="空白 template 檔名（例：edm_template_01.jpeg）"),
    reference_name: str = Query(..., description="含文字的完稿 EDM 檔名（例：edm_full_01.png）"),
):
    """
    從含文字的完稿 EDM 提取文字區域，換算到空白 template 座標系後保存配置

    比直接分析空白 template 更精準，因為可以看到真實的文字位置。

    Args:
        template_name: 空白 template 檔名
        reference_name: 含文字完稿 EDM 檔名（放在 templates/references/ 目錄下）

    Returns:
        識別結果配置（同 /detect-template-regions）
    """
    try:
        from src.generator.template_region_detector import TemplateRegionDetector
        from src.generator.template_engine import TemplateEngine
        from src.config import TEMPLATE_IMAGES_DIR

        # 建立 reference 路徑（放在 templates/references/）
        references_dir = TEMPLATE_IMAGES_DIR.parent / "references"
        reference_path = str(references_dir / reference_name)
        template_path = str(TEMPLATE_IMAGES_DIR / template_name)

        detector = TemplateRegionDetector()
        config = detector.detect_regions_from_reference(
            reference_path=reference_path,
            template_path=template_path,
        )

        # 保存配置（複用 TemplateEngine 的儲存邏輯）
        import json
        from pathlib import Path
        from src.config import TEMPLATE_CONFIGS_DIR

        template_stem = Path(template_name).stem
        config_file = TEMPLATE_CONFIGS_DIR / f"{template_stem}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "template_name": config.get("template_name"),
            "template_image": config.get("template_image"),
            "canvas_size": config.get("canvas_size"),
            "regions_count": len(config.get("regions", [])),
            "regions": config.get("regions", []),
            "message": f"從 reference 識別完成，共識別 {len(config.get('regions', []))} 個區域，已保存至 {config_file.name}",
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"從 reference 識別區域失敗: {str(e)}")


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
        
        config = engine.load_template_config(template_name)

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


@router.get("/templates")
async def list_templates():
    """
    列出所有可用的 EDM template 圖片

    Returns:
        [{name, stem, url}] — template 檔名、stem 和靜態圖片 URL
    """
    from src.config import TEMPLATE_IMAGES_DIR
    image_extensions = {".jpeg", ".jpg", ".png", ".webp"}
    templates = []
    for f in sorted(TEMPLATE_IMAGES_DIR.iterdir()):
        if f.suffix.lower() in image_extensions:
            templates.append({
                "name": f.name,
                "stem": f.stem,
                "url": f"/templates/{f.name}",
            })
    return templates


class RenderRegion(BaseModel):
    id: str
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: int = 32
    bold: bool = False
    color: List[int] = [255, 255, 255]
    anchor: str = "lt"
    max_width: Optional[float] = None


class RenderRequest(BaseModel):
    template_name: str
    regions: List[RenderRegion]


@router.post("/render-with-copy")
async def render_with_copy(request: RenderRequest):
    """
    將文字疊加到 template 上並匯出 PNG

    Args:
        request.template_name: Template 檔名
        request.regions: 每個文字區域的位置、內容、樣式

    Returns:
        {url: "/output/edm/{filename}.png"}
    """
    from PIL import Image
    from src.generator.layout_engine import LayoutEngine
    from src.config import TEMPLATE_IMAGES_DIR, OUTPUT_DIR

    template_path = TEMPLATE_IMAGES_DIR / request.template_name
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template 不存在: {request.template_name}")

    try:
        engine = LayoutEngine()
        canvas = engine.create_canvas(template_path=str(template_path))

        for region in request.regions:
            region_dict = {
                "bbox": [region.x, region.y, region.width, region.height],
                "anchor": region.anchor,
                "font_size": region.font_size,
                "bold": region.bold,
                "color": region.color,
                "max_width": region.max_width if region.max_width is not None else region.width,
            }
            canvas = engine.place_text_in_region(canvas, region.text, region_dict)

        # 儲存到 output/edm/
        edm_dir = OUTPUT_DIR / "edm"
        edm_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        uid = str(uuid.uuid4())[:8]
        stem = Path(request.template_name).stem
        filename = f"{stem}_{ts}_{uid}.png"
        out_path = edm_dir / filename

        canvas.save(str(out_path), "PNG")

        return {"url": f"/output/edm/{filename}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"渲染失敗: {str(e)}")
