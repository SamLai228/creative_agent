"""HTML EDM 生成器：LLM 只生成文案 JSON，Python 做模板替換，確保版型 100% 保留"""
import json
import re
from pathlib import Path
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "html" / "edm_base_template.html"

# 模板中所有文字 placeholder 的說明，提供給 LLM
PLACEHOLDER_SCHEMA = {
    "title":          "主標題第一行（約 12–18 字）",
    "title_2":        "主標題第二行（約 8–14 字，延伸或副標）",
    "content":        "痛點第一行（1 句話，描述現況或數據）",
    "content_2":      "痛點第二行（1 句話，帶出問題場景）",
    "content_3":      "痛點第三行（1 句話，具體痛點或問題）",
    "content_4":      "引導問句（12–18 字，粗體膠囊呈現）",
    "content_5":      "解決方案第一行（1 句話）",
    "content_6":      "解決方案第二行（1 句話）",
    "content_7":      "解決方案第三行（1 句話，收尾）",
    "cta":            "主 CTA 按鈕文字（5–10 字）",
    "product_intro":  "產品推薦引導語（約 10–15 字，例：也許適合你的醫療保障…）",
    "product_name":   "產品全名（精準完整，例：新 iHealth 一年期住院醫療健康保險（外溢型））",
    "content_8":      "底部金句第一行（粗體，約 8–12 字）",
    "content_9":      "底部金句第二行（粗體，約 8–12 字）",
    "content_10":     "底部金句第三行（粗體，約 8–12 字）",
    "cta_2":          "諮詢 CTA 按鈕文字（3–6 字）",
    "conclusion":     "按鈕下方輔助說明（一句話，約 10 字）",
}

# 素材庫中實際存在的 tag 值，提供給 LLM 選擇
CHARACTER_TAG_OPTIONS = {
    "scenario": ["工作", "商業", "通勤", "家庭", "休閒", "其他"],
    "mood":     ["專業", "活力", "歡樂", "平靜", "可愛"],
    "style":    ["3D", "插畫", "現代", "簡約"],
}

SYSTEM_PROMPT = "你是 EDM 文案撰寫專家，請根據需求生成繁體中文文案，以 JSON 格式輸出，不要任何額外說明。"

USER_PROMPT_TEMPLATE = """根據以下需求，為 EDM 各區塊撰寫繁體中文文案，並根據文案內容決定搭配的人物素材需求，以 JSON 格式輸出。

需求：
- 產品／服務名稱：{product_name}
- 活動類型：{promotion_type}
- 核心訊息：{key_message}
- 目標受眾：{target_audience}
- 語氣風格：{tone}

請輸出以下 JSON 結構（每個 key 的說明僅供參考，不要出現在輸出中）：
{schema_json}

另外，請根據文案內容額外輸出 "character_requirements" 欄位，描述最適合搭配此 EDM 的人物插圖：
{{
  "character_requirements": {{
    "count": 人物數量（整數，1 或 2；若文案提及多類人物或情境對比則用 2，否則用 1）,
    "scenario": 從以下選擇最相關的 1–2 個: {scenario_options},
    "mood": 從以下選擇最相關的 1–2 個: {mood_options},
    "style": 從以下選擇最相關的 1–2 個: {style_options}
  }}
}}

只輸出純 JSON，不要 markdown 包裝。"""


class HTMLGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"找不到 HTML 模板：{TEMPLATE_PATH}")
        self.template = TEMPLATE_PATH.read_text(encoding="utf-8")

    def generate(self, requirements: dict) -> str:
        """
        根據需求生成 HTML EDM。
        LLM 同時輸出文案與人物素材需求，Python 選素材、做模板替換。
        """
        copy = self._generate_copy(requirements)

        # 取出人物需求（不是文字 placeholder，需單獨處理）
        char_reqs = copy.pop("character_requirements", None)

        # 選人物素材並產生 HTML 區塊
        characters = []
        if char_reqs:
            try:
                characters = self._select_characters(char_reqs)
            except Exception as e:
                print(f"[HTMLGenerator] 選人物素材失敗，略過：{e}")

        copy["character_section"] = self._build_character_section(characters)

        return self._render(copy)

    def _generate_copy(self, requirements: dict) -> dict:
        """呼叫 LLM，取得各區塊的文案 JSON（含 character_requirements）"""
        schema_json = json.dumps(
            {k: f"（{v}）" for k, v in PLACEHOLDER_SCHEMA.items()},
            ensure_ascii=False, indent=2
        )
        prompt = USER_PROMPT_TEMPLATE.format(
            product_name=requirements.get("product_name", ""),
            promotion_type=requirements.get("promotion_type", ""),
            key_message=requirements.get("key_message", ""),
            target_audience=requirements.get("target_audience", ""),
            tone=requirements.get("tone", ""),
            schema_json=schema_json,
            scenario_options=CHARACTER_TAG_OPTIONS["scenario"],
            mood_options=CHARACTER_TAG_OPTIONS["mood"],
            style_options=CHARACTER_TAG_OPTIONS["style"],
        )

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=1500,
        )

        raw = response.choices[0].message.content.strip()

        # 去掉可能的 markdown 包裝
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        return json.loads(raw)

    def _select_characters(self, char_reqs: dict) -> list:
        """根據 LLM 輸出的人物需求，從素材庫選出最匹配的人物"""
        from src.generator.material_selector import MaterialSelector
        selector = MaterialSelector()
        count = int(char_reqs.get("count", 1))
        requirements = {
            "scenario": char_reqs.get("scenario"),
            "mood":     char_reqs.get("mood"),
            "style":    char_reqs.get("style"),
        }
        return selector.select_characters(requirements, count=count)

    def _build_character_section(self, characters: list) -> str:
        """將選出的人物素材轉換成 HTML <tr> 區塊"""
        if not characters:
            return ""

        def img_tag(material: dict, max_width: int) -> str:
            file_path = material.get("file_path", "")
            url = "/" + file_path if not file_path.startswith("/") else file_path
            return (
                f'<img src="{url}" alt="人物插圖" '
                f'style="max-width: {max_width}px; width: 100%; height: auto; display: block; margin: 0 auto;">'
            )

        if len(characters) == 1:
            return (
                "<tr>\n"
                '    <td align="center" style="padding: 0 20px 10px;">\n'
                f"        {img_tag(characters[0], 280)}\n"
                "    </td>\n"
                "</tr>"
            )
        else:
            col_width = 100 // len(characters)
            cells = "".join(
                f'<td width="{col_width}%" align="center" style="padding: 0 5px;">'
                f"{img_tag(c, 220)}</td>"
                for c in characters
            )
            return (
                "<tr>\n"
                '    <td style="padding: 0 20px 10px;">\n'
                '        <table border="0" cellpadding="0" cellspacing="0" width="100%">\n'
                f"            <tr>{cells}</tr>\n"
                "        </table>\n"
                "    </td>\n"
                "</tr>"
            )

    def _render(self, copy: dict) -> str:
        """將文案 JSON 填入 HTML 模板"""
        html = self.template
        for key, value in copy.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))
        return html
