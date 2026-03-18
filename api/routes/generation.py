"""EDM 生成相關 API 路由"""
from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/generation", tags=["generation"])


@router.post("/generate-copy")
def generate_copy(request: Dict):
    """
    生成 EDM 文案（標題和內文）

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
        raise HTTPException(status_code=500, detail=f"文案生成失敗: {str(e)}")


@router.post("/generate-copy-for-template")
def generate_copy_for_template(request: Dict):
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
        raise HTTPException(status_code=500, detail=f"取得 template 配置失敗: {str(e)}")


class GenerateHTMLRequest(BaseModel):
    product_name: str = ""
    promotion_type: str = ""
    key_message: str = ""
    target_audience: str = ""
    tone: str = ""


@router.post("/generate-html")
def generate_html(request: GenerateHTMLRequest):
    """
    根據需求生成 HTML EDM，並自動儲存到 output/edm/。
    使用同步 def 讓 FastAPI 在 thread pool 執行，避免阻塞 event loop。

    Returns:
        { "html": "...", "saved_path": "output/edm/edm_YYYYMMDD_HHMMSS.html" }
    """
    try:
        from src.generator.html_generator import HTMLGenerator
        from src.config import OUTPUT_DIR
        from datetime import datetime

        generator = HTMLGenerator()
        html = generator.generate(request.dict())

        # 自動儲存到 output/edm/
        edm_dir = OUTPUT_DIR / "edm"
        edm_dir.mkdir(parents=True, exist_ok=True)
        filename = f"edm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        saved_path = edm_dir / filename
        saved_path.write_text(html, encoding="utf-8")
        print(f"[generate_html] 已儲存：{saved_path}")

        return {"html": html, "saved_path": str(saved_path.relative_to(OUTPUT_DIR.parent))}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML 生成失敗: {str(e)}")


class SavePNGRequest(BaseModel):
    image_data: str  # base64，不含 data:image/png;base64, 前綴
    filename: str = ""  # 可選，不填自動產生


@router.post("/save-png")
def save_png(request: SavePNGRequest):
    """
    接收前端截圖的 base64 PNG，儲存到 output/edm/。
    Returns: { "saved_path": "output/edm/edm_YYYYMMDD_HHMMSS.png" }
    """
    import base64
    from src.config import OUTPUT_DIR
    from datetime import datetime

    try:
        data = request.image_data
        if data.startswith("data:"):
            data = data.split(",", 1)[1]
        img_bytes = base64.b64decode(data)

        edm_dir = OUTPUT_DIR / "edm"
        edm_dir.mkdir(parents=True, exist_ok=True)
        stem = request.filename or f"edm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # 去掉副檔名，統一加 .png
        stem = stem.rsplit(".", 1)[0]
        saved_path = edm_dir / f"{stem}.png"
        saved_path.write_bytes(img_bytes)
        print(f"[save_png] 已儲存：{saved_path}")

        return {"saved_path": str(saved_path.relative_to(OUTPUT_DIR.parent))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PNG 儲存失敗: {str(e)}")


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
