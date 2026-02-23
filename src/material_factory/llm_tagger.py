"""LLM 標籤生成器 - 使用 LLM API 為素材貼標"""
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL
from .image_analyzer import ImageAnalyzer


class LLMTagger:
    """使用 LLM API 為圖片素材生成語義標籤"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("請在 .env 檔案中設定 OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.image_analyzer = ImageAnalyzer()
    
    def generate_tags(self, image_path: Path, image_info: Optional[Dict] = None) -> Dict:
        """
        使用 LLM 為圖片生成語義標籤
        
        Args:
            image_path: 圖片檔案路徑
            image_info: 圖片基本資訊（可選，如果不提供會自動分析）
            
        Returns:
            包含標籤的字典
        """
        # 如果沒有提供圖片資訊，先分析圖片
        if image_info is None:
            image_info = self.image_analyzer.analyze(image_path)
        
        # 編碼圖片為 base64
        base64_image = self.image_analyzer.encode_image_base64(image_path)
        mime_type = self.image_analyzer.get_mime_type(image_path)
        
        # 建立提示詞
        prompt = self._build_prompt(image_info)
        
        try:
            # 呼叫 OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專業的設計素材分析師，專門為行銷 EDM 素材進行語義標籤。請仔細分析圖片內容，並提供結構化的標籤資訊。"
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
                temperature=0.3,
            )
            
            # 解析回應
            content = response.choices[0].message.content
            tags = json.loads(content)
            
            # 驗證和標準化標籤
            return self._validate_and_normalize_tags(tags, image_path)
            
        except Exception as e:
            raise RuntimeError(f"LLM API 呼叫失敗: {str(e)}")
    
    def _build_prompt(self, image_info: Dict) -> str:
        """建立提示詞"""
        return f"""請分析這張圖片，並提供以下結構化的 JSON 標籤資訊：

圖片基本資訊：
- 尺寸: {image_info.get('width')}x{image_info.get('height')}
- 長寬比: {image_info.get('aspect_ratio')}
- 主要色調: RGB({image_info.get('dominant_color')[0]}, {image_info.get('dominant_color')[1]}, {image_info.get('dominant_color')[2]})

請提供以下標籤（請用繁體中文）：

1. **類型** (category): 選擇一個主要類型
   - 人物 (character)
   - 背景 (background)
   - 裝飾 (decoration)
   - 物件 (object)
   - 文字 (text)
   - 其他 (other)

2. **風格** (style): 可多選，用陣列表示
   - 插畫 (illustration)
   - 扁平 (flat)
   - 寫實 (realistic)
   - 手繪 (hand-drawn)
   - 3D (3d)
   - 簡約 (minimalist)
   - 復古 (vintage)
   - 現代 (modern)

3. **情境** (scenario): 可多選，用陣列表示
   - 通勤 (commute)
   - 家庭 (family)
   - 旅行 (travel)
   - 工作 (work)
   - 購物 (shopping)
   - 休閒 (leisure)
   - 節慶 (festival)
   - 商業 (business)
   - 教育 (education)
   - 其他 (other)

4. **色系** (color_scheme): 描述主要色系
   - 暖色 (warm)
   - 冷色 (cool)
   - 中性 (neutral)
   - 鮮豔 (vibrant)
   - 柔和 (soft)
   - 單色 (monochrome)

5. **氛圍** (mood): 可多選，用陣列表示
   - 歡樂 (joyful)
   - 專業 (professional)
   - 溫馨 (cozy)
   - 活力 (energetic)
   - 平靜 (calm)
   - 神秘 (mysterious)
   - 優雅 (elegant)
   - 可愛 (cute)

6. **可用範圍** (usage_scope): 描述這個素材適合用在哪些場景
   - 描述文字（繁體中文）

7. **關鍵字** (keywords): 提供 3-5 個相關關鍵字（繁體中文陣列）

請以 JSON 格式回覆，格式如下：
{{
  "category": "類型",
  "style": ["風格1", "風格2"],
  "scenario": ["情境1", "情境2"],
  "color_scheme": "色系",
  "mood": ["氛圍1", "氛圍2"],
  "usage_scope": "可用範圍描述",
  "keywords": ["關鍵字1", "關鍵字2", "關鍵字3"]
}}"""
    
    def _validate_and_normalize_tags(self, tags: Dict, image_path: Path) -> Dict:
        """驗證和標準化標籤"""
        # 確保必要欄位存在
        normalized = {
            "file_path": str(image_path),
            "file_name": image_path.name,
            "category": tags.get("category", "other"),
            "style": tags.get("style", []),
            "scenario": tags.get("scenario", []),
            "color_scheme": tags.get("color_scheme", "neutral"),
            "mood": tags.get("mood", []),
            "usage_scope": tags.get("usage_scope", ""),
            "keywords": tags.get("keywords", []),
        }
        
        # 確保陣列欄位是列表
        for field in ["style", "scenario", "mood", "keywords"]:
            if not isinstance(normalized[field], list):
                normalized[field] = [normalized[field]] if normalized[field] else []
        
        return normalized
