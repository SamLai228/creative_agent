"""Template 區域識別器 - 使用 Vision API 識別 template 上的文字區域"""
import json
import base64
import platform
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
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
    
    def detect_regions_from_reference(
        self,
        reference_path: str,
        template_path: str
    ) -> Dict:
        """
        從含文字的完稿 EDM 提取文字區域，並等比例換算到空白 template 座標系

        Args:
            reference_path: 含文字的完稿 EDM 圖片路徑
            template_path: 空白 template 圖片路徑（用於取得目標尺寸）

        Returns:
            包含區域資訊的字典
        """
        # 解析 reference 路徑
        reference = Path(reference_path)
        if not reference.exists():
            if not reference.is_absolute():
                # 嘗試在 templates/references/ 目錄下尋找
                references_dir = TEMPLATE_IMAGES_DIR.parent / "references"
                reference = references_dir / reference
        if not reference.exists():
            raise FileNotFoundError(f"Reference 圖片不存在: {reference_path}")

        # 解析 template 路徑
        template = Path(template_path)
        if not template.exists():
            if not template.is_absolute():
                template = TEMPLATE_IMAGES_DIR / template
        if not template.exists():
            raise FileNotFoundError(f"Template 圖片不存在: {template_path}")

        # 取得兩張圖片的尺寸
        ref_w, ref_h = self._get_image_size(reference)
        template_w, template_h = self._get_image_size(template)

        # 計算縮放比例
        scale_x = template_w / ref_w
        scale_y = template_h / ref_h

        # 在 reference 圖片上疊加座標網格，提升 LLM 座標精度
        with Image.open(reference) as ref_img:
            gridded_img = self._add_coordinate_grid(ref_img)

        # 將網格圖存到暫存檔並編碼
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        gridded_img.save(tmp_path, format="PNG")
        base64_image = self._encode_image_base64(tmp_path)
        tmp_path.unlink(missing_ok=True)
        mime_type = "image/png"

        # 建立提示詞
        prompt = self._build_reference_detection_prompt(ref_w, ref_h)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專業的 EDM 設計分析師，專門從完稿 EDM 圖片中精確識別每段文字的位置和尺寸。請仔細分析圖片中實際存在的文字，以 JSON 格式回傳精確的邊界框座標。"
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
                temperature=0.1,
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # 將 bbox 座標從 reference 座標系換算到 template 座標系
            if "regions" in result and isinstance(result["regions"], list):
                for region in result["regions"]:
                    if "bbox" in region and isinstance(region["bbox"], list) and len(region["bbox"]) == 4:
                        rx, ry, rw, rh = region["bbox"]
                        region["bbox"] = [
                            round(rx * scale_x),
                            round(ry * scale_y),
                            round(rw * scale_x),
                            round(rh * scale_y),
                        ]
                        # 換算 max_width 如果存在
                        if "max_width" in region:
                            region["max_width"] = round(region["max_width"] * scale_x)
                    # 換算 font_size
                    if "font_size" in region:
                        region["suggested_font_size"] = round(region["font_size"] * scale_y)
                    elif "suggested_font_size" in region:
                        region["suggested_font_size"] = round(region["suggested_font_size"] * scale_y)

            # 後處理：切割高度超過單行 1.5 倍的 bbox
            result["regions"] = self._split_tall_regions(result.get("regions", []))
            # 後處理：對齊同一區塊的 title / content x 座標
            result["regions"] = self._align_title_blocks(result["regions"])
            result["regions"] = self._align_content_blocks(result["regions"])

            # 驗證和標準化，使用 template 的尺寸
            return self._validate_and_normalize_regions(result, template_w, template_h, Path(template_path).name)

        except Exception as e:
            raise RuntimeError(f"從 reference 識別區域失敗: {str(e)}")

    def _align_title_blocks(self, regions: list) -> list:
        """
        將同一標題區塊（連續 title 且 y 間距在 3× font_size 內）的 x 座標對齊到中位數。
        解決 LLM 對同一段落不同行估算出不同 x 偏移的問題。
        """
        if not regions:
            return regions

        result = [dict(r) for r in regions]
        i = 0
        while i < len(result):
            if result[i].get("type") != "title":
                i += 1
                continue
            # 找出連續 title 群組
            j = i + 1
            while j < len(result):
                if result[j].get("type") != "title":
                    break
                # 只有 y 間距不超過 3× font_size 才算同一區塊
                prev_bbox = result[j - 1]["bbox"]
                cur_bbox = result[j]["bbox"]
                font_size = result[j].get("font_size", 30)
                y_gap = cur_bbox[1] - (prev_bbox[1] + prev_bbox[3])
                if y_gap > font_size * 3:
                    break
                j += 1

            group = result[i:j]
            if len(group) > 1:
                # 取 x 中位數對齊（避免被單一誤差值拉偏）
                xs = sorted(r["bbox"][0] for r in group)
                median_x = xs[len(xs) // 2]
                for r in group:
                    r["bbox"][0] = median_x
                    r["max_width"] = r["bbox"][2]  # max_width 跟著 x 調整無需變

            i = j

        return result

    def _align_content_blocks(self, regions: list) -> list:
        """
        將同一內文區塊（連續 content 且 y 間距在 3× font_size 內）的 x 座標
        對齊到中位數，修正 LLM 對同一段落不同行的微小 x 估算偏差。
        僅在群組內 x 偏差 ≤ 50px 時修正（保留真正的縮排設計）。
        """
        if not regions:
            return regions

        result = [dict(r) for r in regions]
        i = 0
        while i < len(result):
            if result[i].get("type") != "content":
                i += 1
                continue
            j = i + 1
            while j < len(result):
                if result[j].get("type") != "content":
                    break
                prev_bbox = result[j - 1]["bbox"]
                cur_bbox = result[j]["bbox"]
                font_size = result[j].get("font_size", 30)
                y_gap = cur_bbox[1] - (prev_bbox[1] + prev_bbox[3])
                if y_gap > font_size * 3:
                    break
                j += 1

            group = result[i:j]
            if len(group) > 1:
                xs = sorted(r["bbox"][0] for r in group)
                # 只在 x 偏差 ≤ 50px 時修正（避免誤改真正的縮排）
                if xs[-1] - xs[0] <= 50:
                    median_x = xs[len(xs) // 2]
                    for r in group:
                        r["bbox"][0] = median_x
            i = j

        return result

    def _split_tall_regions(self, regions: list) -> list:
        """
        將高度超過單行 1.5 倍的 bbox 自動切割成多個單行 region。
        這是防止 LLM 合併多行的保護層。

        單行高度估算：font_size + 10（與 layout_engine 的 line_height 一致）
        """
        result = []
        for region in regions:
            bbox = region.get("bbox")
            if not bbox or len(bbox) != 4:
                result.append(region)
                continue

            x, y, w, h = bbox
            font_size = region.get("suggested_font_size") or region.get("font_size") or 26
            line_height = font_size + 10
            single_line_max = line_height * 1.5  # 超過這個高度才切

            if h <= single_line_max:
                result.append(region)
                continue

            # 計算切幾行
            n_lines = max(2, round(h / line_height))
            slice_h = round(h / n_lines)

            for i in range(n_lines):
                sliced = dict(region)
                sliced["bbox"] = [x, y + i * slice_h, w, slice_h]
                result.append(sliced)

        return result

    def _add_coordinate_grid(self, img: Image.Image) -> Image.Image:
        """
        在圖片上疊加座標網格，提升 LLM 座標估算精度。
        垂直線每 10%（標示 x 像素值），水平線每 5%（標示 y 像素值）。
        """
        gridded = img.copy().convert("RGBA")
        overlay = Image.new("RGBA", gridded.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        w, h = img.size

        # 嘗試載入數字字體
        label_font = None
        try:
            if platform.system() == "Darwin":
                for fp in [
                    "/System/Library/Fonts/Supplemental/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]:
                    if Path(fp).exists():
                        label_font = ImageFont.truetype(fp, 13)
                        break
            if label_font is None:
                label_font = ImageFont.load_default()
        except Exception:
            label_font = ImageFont.load_default()

        # 垂直線：每 5% 寬度（標示 x 座標，major 每 10%、minor 每 5%）
        for i in range(21):
            x = round(i / 20 * w)
            is_major = i % 2 == 0
            alpha = 150 if is_major else 60
            draw.line([(x, 0), (x, h)], fill=(220, 30, 30, alpha), width=1)
            if is_major:
                draw.text((x + 1, 3), str(x), fill=(220, 30, 30, 255), font=label_font)
            else:
                draw.text((x + 1, 3), str(x), fill=(220, 30, 30, 180), font=label_font)

        # 水平線：每 5% 高度（標示 y 座標）
        for i in range(21):
            y = round(i / 20 * h)
            draw.line([(0, y), (w, y)], fill=(30, 30, 210, 90), width=1)
            draw.text((2, y + 1), str(y), fill=(30, 30, 210, 240), font=label_font)

        result = Image.alpha_composite(gridded, overlay)
        return result.convert("RGB")

    def _build_reference_detection_prompt(self, image_width: int, image_height: int) -> str:
        """建立從完稿 EDM 識別文字區域的提示詞（逐行偵測版，含網格輔助說明）"""
        return f"""請仔細分析這張完稿 EDM 圖片，逐行找出所有實際存在的文字，每一行文字必須單獨列出。

圖片尺寸：{image_width} x {image_height} 像素

## 如何使用圖片上的座標網格（非常重要）
圖片上疊加了一組座標參考線：
- **紅色垂直線**：每隔 5% 寬度一條（major line 每 10%），線旁標示 x 像素座標
  - 格線間距約 {round(image_width*0.05)}px，可精確到 ±{round(image_width*0.025)}px
- **藍色水平線**：每隔 5% 高度一條，線旁標示 y 像素座標
  - 格線間距約 {round(image_height*0.05)}px，可精確到 ±{round(image_height*0.025)}px
- **請直接讀取格線標籤數字**作為座標，不要靠目測估算
- 文字左邊緣接近哪條紅線 → 讀那條紅線的 x 值（可估算兩線之間的內插值）
- 文字上邊緣接近哪條藍線 → 讀那條藍線的 y 值（可估算兩線之間的內插值）
- 寬度 = 文字右邊緣 x 值 − 左邊緣 x 值
- 高度 = 單行文字高度（≈ font_size + 8px），不是整個段落
- **同一段落的多行文字，x 座標應相同或非常接近，請確保一致性**

## 最重要的規則（必須遵守）
- **每一行文字 = 一個獨立的 region**
- **絕對禁止**將多行文字合併成一個大 bbox
- 如果看到 3 行文字，就回傳 3 個 region（分別對應 3 個不同的 y 座標）
- bbox 的 height 只能是「單行文字高度」，等於字體大小加上少許間距（≈ font_size + 8px）
- bbox 要緊貼文字邊緣，不要留太多空白

## 文字類型分類
- **title**：主標題、大字標語（通常是最大字體、最顯眼的文字）
- **content**：內文、說明文字、每行條列
- **cta**：所有行動呼籲元素，包含：
  - 有背景色的按鈕（例如：立即申請、了解更多）
  - 帶有箭頭符號的文字連結（例如：立即閱讀完整文章▶、點此了解→）
  - 有底線或特殊樣式的可點擊文字
  - 被邊框、圓角框包圍的段落標題（例如：「一個人手術前該準備什麼？」圓圈框）
- **conclusion**：結語、頁尾小字

## 每個 region 需要提供的欄位
- **type**: title / content / cta / conclusion
- **text**: 該行文字的實際內容（原文）
- **bbox**: [x, y, width, height]（請對照網格標籤讀取精確像素值）
  - x, y: 該行文字左上角座標
  - width: 該行文字的寬度
  - height: 單行文字高度（≈ font_size + 8，不是整個段落高度）
- **font_size**: 估計的字體大小（像素）
- **suggested_color**: 文字顏色 [R, G, B]
- **alignment**: left / center / right
- **max_width**: 等於 width

## 正確範例（3 行內文 → 3 個 region）
如果圖中有連續 3 行內文，字體大小約 26px，行距約 10px：
{{
  "regions": [
    {{"type": "content", "text": "第一行文字內容", "bbox": [80, 200, 400, 34], "font_size": 26, "suggested_color": [60, 60, 60], "alignment": "left", "max_width": 400}},
    {{"type": "content", "text": "第二行文字內容", "bbox": [80, 244, 420, 34], "font_size": 26, "suggested_color": [60, 60, 60], "alignment": "left", "max_width": 420}},
    {{"type": "content", "text": "第三行文字內容", "bbox": [80, 288, 380, 34], "font_size": 26, "suggested_color": [60, 60, 60], "alignment": "left", "max_width": 380}}
  ]
}}

## 錯誤範例（不可以這樣做）
{{"type": "content", "bbox": [80, 200, 420, 120]}}  ← 高度 120 包含了多行，這是錯的！

請按照從上到下的順序列出所有 region，所有座標在圖片範圍內（0 <= x < {image_width}, 0 <= y < {image_height}）。"""

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

            # 過濾明顯錯誤的 region（height 過小 = LLM 估算失誤）
            if height < 12:
                continue
            
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
