"""文案生成器 - 使用 LLM 生成 EDM 標題和內文"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, TEMPLATE_DIR


class Copywriter:
    """文案生成器 - 根據需求生成 EDM 標題和內文"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("請在 .env 檔案中設定 OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.examples_dir = TEMPLATE_DIR / "copywriting_examples"
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        self.examples_file = self.examples_dir / "examples.json"
    
    def load_examples(self) -> List[Dict]:
        """
        載入公司文案範例
        
        Returns:
            範例列表
        """
        if not self.examples_file.exists():
            return []
        
        try:
            with open(self.examples_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("examples", [])
        except Exception as e:
            print(f"警告: 無法載入文案範例: {str(e)}")
            return []
    
    def generate_copy(
        self,
        requirements: Dict,
        product_info: Optional[str] = None,
        target_audience: Optional[str] = None,
        tone: Optional[str] = None
    ) -> Dict:
        """
        生成 EDM 文案（標題和內文）
        
        Args:
            requirements: 生成需求，包含：
                - product_name: 產品/服務名稱（可選）
                - promotion_type: 促銷類型（可選）
                - key_message: 主要訊息（可選）
                - call_to_action: 行動呼籲（可選）
            product_info: 產品資訊（可選）
            target_audience: 目標受眾（可選）
            tone: 文案風格（可選）
            
        Returns:
            包含標題和內文的字典
        """
        # 載入範例
        examples = self.load_examples()
        
        # 建立提示詞
        prompt = self._build_prompt(requirements, examples, product_info, target_audience, tone)
        
        try:
            # 呼叫 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專業的壽險行銷文案撰寫師，專門為壽險公司的 EDM（電子郵件行銷）撰寫吸引人的標題和內文。請根據提供的需求和範例，生成符合壽險產業特色且能有效吸引目標受眾的文案。文案要傳達保障、安心、專業的價值，使用繁體中文。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,  # 文案需要創意，溫度稍高
            )
            
            # 解析回應
            content = response.choices[0].message.content
            copy = json.loads(content)
            
            # 驗證和標準化
            return self._validate_and_normalize_copy(copy)
            
        except Exception as e:
            raise RuntimeError(f"文案生成失敗: {str(e)}")
    
    def _build_prompt(
        self,
        requirements: Dict,
        examples: List[Dict],
        product_info: Optional[str],
        target_audience: Optional[str],
        tone: Optional[str]
    ) -> str:
        """建立提示詞"""
        
        # 建立需求描述
        requirements_text = []
        if requirements.get("product_name"):
            requirements_text.append(f"產品/服務名稱: {requirements['product_name']}")
        if requirements.get("promotion_type"):
            requirements_text.append(f"促銷類型: {requirements['promotion_type']}")
        if requirements.get("key_message"):
            requirements_text.append(f"主要訊息: {requirements['key_message']}")
        if requirements.get("call_to_action"):
            requirements_text.append(f"行動呼籲: {requirements['call_to_action']}")
        if product_info:
            requirements_text.append(f"產品資訊: {product_info}")
        if target_audience:
            requirements_text.append(f"目標受眾: {target_audience}")
        if tone:
            requirements_text.append(f"文案風格: {tone}")
        
        # 建立範例文字
        examples_text = ""
        if examples:
            examples_text = "\n\n參考範例：\n"
            for i, example in enumerate(examples[:5], 1):  # 最多 5 個範例
                examples_text += f"\n範例 {i}:\n"
                if example.get('subject'):
                    examples_text += f"信件主旨: {example.get('subject')}\n"
                examples_text += f"標題: {example.get('title', '')}\n"
                examples_text += f"內文: {example.get('content', '')}\n"
                if example.get('tone'):
                    examples_text += f"風格: {example.get('tone')}\n"
                if example.get('call_to_action'):
                    cta = example.get('call_to_action')
                    if isinstance(cta, list):
                        examples_text += f"CTA（行動呼籲）: {', '.join(cta)}\n"
                    else:
                        examples_text += f"CTA（行動呼籲）: {cta}\n"
                if example.get('conclusion'):
                    examples_text += f"結語: {example.get('conclusion')}\n"
        
        prompt = f"""請為壽險公司 EDM 生成吸引人的標題和內文。

需求資訊：
{chr(10).join(requirements_text) if requirements_text else "（未提供具體需求，請根據壽險行銷原則生成）"}

要求：
1. **標題**：簡潔有力，8-15 個字，能立即吸引注意力，傳達保障、安心、專業的價值
2. **內文**：30-80 個字，說明險種特色、保障內容或優惠方案，並引導行動，適合疊在圖片上顯示
3. **CTA（行動呼籲）**：必須包含 1-3 個行動呼籲，例如「立即了解」、「立即規劃」、「點我諮詢」等，用陣列格式提供
4. 使用繁體中文
5. 符合壽險產業的專業風格和語氣（溫馨、專業、安心、關懷）
6. 避免過於冗長或複雜的句子
7. 標題要能引起對保障需求的重視或傳達險種特色
8. 內文要包含具體的保障內容、險種特色或優惠資訊
9. 強調保障價值、安心感、專業服務等壽險核心價值
10. 避免過度銷售話術，以關懷和專業為主
11. **重要**：必須包含 CTA（行動呼籲），參考範例中的 CTA 格式{examples_text}

請以 JSON 格式回覆：
{{
  "title": "標題文字",
  "content": "內文內容",
  "call_to_action": ["CTA1", "CTA2", "CTA3"],
  "tone": "文案風格描述",
  "key_points": ["重點1", "重點2", "重點3"]
}}"""
        
        return prompt
    
    def generate_copy_for_template(
        self,
        template_config: Dict,
        requirements: Dict,
    ) -> Dict[str, str]:
        """
        根據 template 的 region 配置生成文案，每個 region 各自有字數上限。

        Args:
            template_config: 由 TemplateRegionDetector 產生的 region config
            requirements: 生成需求（product_name、key_message、target_audience、tone 等）

        Returns:
            dict: region_id → 對應文字（已截斷至字數上限）
        """
        regions = template_config.get("regions", [])

        # 計算每個 region 的字數上限
        slots = []
        for r in regions:
            bbox = r.get("bbox", [0, 0, 100, 100])
            fs = r.get("font_size", 26)
            cpl = max(1, int(bbox[2] / fs))               # chars per line (PingFang CJK ≈ 0.95× fs)
            lines = max(1, int(bbox[3] / (fs + 10)))      # max lines
            slots.append({
                "id": r["id"],
                "type": r["type"],
                "max_chars": cpl * lines,
                "chars_per_line": cpl,
                "max_lines": lines,
            })

        prompt = self._build_template_copy_prompt(slots, requirements)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一個專業的壽險 EDM 文案撰寫師。"
                            "請嚴格遵守每個欄位的字數上限，不可超過。"
                            "每個欄位的文字必須獨立完整，不能延續到下一欄。"
                            "使用繁體中文，語氣溫暖專業。"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            raw = json.loads(response.choices[0].message.content)

            # 截斷超出字數的文字，清除空白
            result: Dict[str, str] = {}
            for slot in slots:
                rid = slot["id"]
                text = str(raw.get(rid, "")).strip()
                if len(text) > slot["max_chars"]:
                    cutoff = slot["max_chars"]
                    # 優先在標點符號處斷句，至少保留 70% 字數
                    for punct in "。！？，、":
                        idx = text.rfind(punct, 0, cutoff)
                        if idx >= int(cutoff * 0.7):
                            cutoff = idx + 1  # 保留標點
                            break
                    text = text[:cutoff]
                result[rid] = text

            return result

        except Exception as e:
            raise RuntimeError(f"Template 文案生成失敗: {str(e)}")

    def _build_template_copy_prompt(self, slots: List[Dict], requirements: Dict) -> str:
        """建立 template-aware 文案提示詞"""
        req_parts = []
        if requirements.get("product_name"):
            req_parts.append(f"產品名稱：{requirements['product_name']}")
        if requirements.get("promotion_type"):
            req_parts.append(f"促銷類型：{requirements['promotion_type']}")
        if requirements.get("key_message"):
            req_parts.append(f"主要訊息：{requirements['key_message']}")
        if requirements.get("target_audience"):
            req_parts.append(f"目標受眾：{requirements['target_audience']}")
        if requirements.get("tone"):
            req_parts.append(f"文案風格：{requirements['tone']}")
        req_text = "\n".join(req_parts) if req_parts else "壽險保障推廣"

        type_labels = {
            "title": "標題（簡潔有力）",
            "content": "內文說明",
            "cta": "行動呼籲按鈕（短促有力）",
            "conclusion": "結語（完整一句話，必須盡量用滿字數上限）",
        }

        slot_lines = []
        for s in slots:
            label = type_labels.get(s["type"], s["type"])
            min_chars = max(1, int(s["max_chars"] * 0.8))
            slot_lines.append(
                f'  "{s["id"]}": {label}'
                f'，目標 {s["max_chars"]} 字（不可少於 {min_chars} 字，不可超過 {s["max_chars"]} 字）'
                f'，每行約 {s["chars_per_line"]} 字，共 {s["max_lines"]} 行'
            )

        # 空殼 JSON 給 LLM 知道要填哪些 key
        skeleton = json.dumps(
            {s["id"]: "" for s in slots}, ensure_ascii=False, indent=2
        )

        return f"""請為壽險公司 EDM 生成完整的多段文案，每個欄位對應版面中的一個文字區域。

## 需求資訊
{req_text}

## 欄位說明（嚴格遵守字數上限）
{chr(10).join(slot_lines)}

## 重要規則
1. 每個欄位的文字**獨立完整**，不可在下一欄延續句子
2. **嚴格不超過**各欄位的字數上限（超過會被截斷）
3. **字數必須達到目標的 80% 以上**，版面有多少空間就要填多少文字
4. 文案邏輯順序：標題 → 介紹說明 → 特色亮點 → 行動呼籲 → 結語
5. title 類型：精煉的標題或副標題，必須用到目標字數的 80% 以上
6. content 類型：依 EDM 版面位置填入完整段落內容，每行要有完整意義，填滿為止
7. cta 類型：簡短、有行動力的按鈕文字（例：「立即了解方案」「點我免費諮詢」）
8. conclusion 類型：溫暖且完整的結語，**必須達到目標字數的 80% 以上**。若目標 10 字，寫「期待與您攜手，共創安心生活」（12字但被截到10字），而非「與您守家」（4字）

## 請填入以下 JSON（不可增減欄位）
{skeleton}"""

    def _validate_and_normalize_copy(self, copy: Dict) -> Dict:
        """驗證和標準化文案"""
        # 處理 CTA
        call_to_action = copy.get("call_to_action", [])
        if isinstance(call_to_action, str):
            call_to_action = [call_to_action]
        elif not isinstance(call_to_action, list):
            call_to_action = []
        
        normalized = {
            "title": copy.get("title", "").strip(),
            "content": copy.get("content", "").strip(),
            "call_to_action": [cta.strip() for cta in call_to_action if cta.strip()],
            "tone": copy.get("tone", ""),
            "key_points": copy.get("key_points", [])
        }
        
        # 確保標題和內文不為空（使用壽險相關預設值）
        if not normalized["title"]:
            normalized["title"] = "完善保障，守護未來"
        if not normalized["content"]:
            normalized["content"] = "立即了解保障方案，為您與家人規劃最適合的保險計畫"
        
        # 確保至少有一個 CTA
        if not normalized["call_to_action"]:
            normalized["call_to_action"] = ["立即了解保障方案"]
        
        return normalized
