"""Template 區域識別器 - 使用 Vision API 識別 template 上的文字區域"""
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, TEMPLATE_IMAGES_DIR


class TemplateRegionDetector:
    """使用 Vision API 識別 template 圖片上的文字區域"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("請在 .env 檔案中設定 OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def _encode_image_base64(self, image_path: Path) -> str:
        """將圖片編碼為 base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_mime_type(self, image_path: Path) -> str:
        """取得圖片的 MIME 類型"""
        ext = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def _get_image_size(self, image_path: Path) -> tuple:
        """取得圖片尺寸"""
        with Image.open(image_path) as img:
            return img.size
    
    def detect_regions(self, template_path: str) -> Dict:
        """
        使用 Vision API 識別 template 上的文字區域
        
        Args:
            template_path: Template 圖片路徑（檔名或完整路徑）
            
        Returns:
            包含區域資訊的字典
        """
        # 解析路徑
        template = Path(template_path)
        if not template.exists():
            # 嘗試在 TEMPLATE_IMAGES_DIR 中尋找
            if not template.is_absolute():
                template = TEMPLATE_IMAGES_DIR / template
            else:
                template = Path(template_path)
        
        if not template.exists():
            raise FileNotFoundError(f"Template 圖片不存在: {template_path}")
        
        # 取得圖片尺寸
        image_width, image_height = self._get_image_size(template)
        
        # 編碼圖片
        base64_image = self._encode_image_base64(template)
        mime_type = self._get_mime_type(template)
        
        # 建立提示詞
        prompt = self._build_detection_prompt(image_width, image_height)
        
        try:
            # 呼叫 OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專業的 EDM 設計分析師，專門分析 EDM template 圖片並識別文字放置區域。請仔細分析圖片，識別出所有可以放置文字的區域，包括標題、內文、CTA 按鈕等。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,  # 降低溫度以獲得更穩定的結果
            )
            
            # 解析回應
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # 驗證和標準化結果
            return self._validate_and_normalize_regions(result, image_width, image_height, template.name)
            
        except Exception as e:
            raise RuntimeError(f"區域識別失敗: {str(e)}")
    
    def _build_detection_prompt(self, image_width: int, image_height: int) -> str:
        """建立區域識別的提示詞"""
        return f"""請仔細分析這張 EDM template 圖片，識別出所有可以放置文字的區域。

圖片尺寸：{image_width} x {image_height} 像素

請識別以下類型的區域：
1. **標題區域 (title)**：用於放置 EDM 主標題的區域
2. **內文區域 (content)**：用於放置 EDM 內文描述的區域
3. **CTA 按鈕區域 (cta)**：用於放置行動呼籲按鈕的區域（可能有多個）
4. **結語區域 (conclusion)**：用於放置結語的區域（可選）

對於每個識別出的區域，請提供以下資訊：
- **type**: 區域類型（title/content/cta/conclusion）
- **bbox**: 邊界框座標 [x, y, width, height]，其中：
  - x: 區域左上角的 X 座標
  - y: 區域左上角的 Y 座標
  - width: 區域寬度
  - height: 區域高度
- **suggested_font_size**: 建議的字體大小（像素）
- **suggested_color**: 建議的文字顏色 [R, G, B]，例如 [0, 0, 0] 表示黑色
- **alignment**: 文字對齊方式（left/center/right）
- **max_width**: 文字最大寬度（像素，用於自動換行）

請以 JSON 格式返回結果，格式如下：
{{
  "regions": [
    {{
      "type": "title",
      "bbox": [100, 50, 800, 100],
      "suggested_font_size": 64,
      "suggested_color": [0, 0, 0],
      "alignment": "left",
      "max_width": 800
    }},
    {{
      "type": "content",
      "bbox": [100, 200, 900, 400],
      "suggested_font_size": 32,
      "suggested_color": [50, 50, 50],
      "alignment": "left",
      "max_width": 900
    }},
    {{
      "type": "cta",
      "bbox": [100, 650, 200, 50],
      "suggested_font_size": 24,
      "suggested_color": [255, 255, 255],
      "alignment": "center",
      "max_width": 200
    }}
  ]
}}

請確保：
1. 所有座標都在圖片範圍內（0 <= x < {image_width}, 0 <= y < {image_height}）
2. bbox 的格式是 [x, y, width, height]
3. 如果有多個相同類型的區域（如多個 CTA），請分別列出
4. 根據區域的視覺特徵判斷類型（例如：按鈕形狀的區域通常是 CTA）"""
    
    def _validate_and_normalize_regions(
        self, 
        result: Dict, 
        image_width: int, 
        image_height: int,
        template_name: str
    ) -> Dict:
        """驗證和標準化識別結果"""
        if "regions" not in result:
            raise ValueError("識別結果中缺少 'regions' 欄位")
        
        regions = result["regions"]
        if not isinstance(regions, list):
            raise ValueError("'regions' 必須是一個列表")
        
        normalized_regions = []
        region_ids = {}  # 用於生成唯一 ID
        
        for i, region in enumerate(regions):
            # 驗證必要欄位
            if "type" not in region:
                continue
            
            region_type = region["type"]
            if region_type not in ["title", "content", "cta", "conclusion"]:
                continue
            
            # 生成唯一 ID
            if region_type in region_ids:
                region_ids[region_type] += 1
            else:
                region_ids[region_type] = 1
            
            region_id = f"{region_type}_{region_ids[region_type]}" if region_ids[region_type] > 1 else region_type
            
            # 驗證和標準化 bbox
            if "bbox" not in region or not isinstance(region["bbox"], list) or len(region["bbox"]) != 4:
                continue
            
            x, y, width, height = region["bbox"]
            
            # 確保座標在有效範圍內
            x = max(0, min(int(x), image_width - 1))
            y = max(0, min(int(y), image_height - 1))
            width = max(10, min(int(width), image_width - x))
            height = max(10, min(int(height), image_height - y))
            
            # 標準化區域配置
            normalized_region = {
                "id": region_id,
                "type": region_type,
                "bbox": [x, y, width, height],
                "anchor": "lt",  # 預設左上角對齊
                "font_size": int(region.get("suggested_font_size", 32)),
                "color": region.get("suggested_color", [0, 0, 0]),
                "max_width": int(region.get("max_width", width)),
            }
            
            # 根據對齊方式設定 anchor
            alignment = region.get("alignment", "left")
            if alignment == "center":
                normalized_region["anchor"] = "center"
            elif alignment == "right":
                normalized_region["anchor"] = "rt"
            
            normalized_regions.append(normalized_region)
        
        # 構建最終結果
        return {
            "template_name": Path(template_name).stem,
            "template_image": template_name,
            "canvas_size": [image_width, image_height],
            "regions": normalized_regions
        }
