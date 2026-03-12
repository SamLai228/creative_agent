"""HTML EDM 生成器：LLM 只生成文案 JSON，Python 做模板替換，確保版型 100% 保留"""
import json
import re
from pathlib import Path
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "html" / "edm_base_template.html"

# 模板中所有 placeholder 的說明，提供給 LLM
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

SYSTEM_PROMPT = "你是 EDM 文案撰寫專家，請根據需求生成繁體中文文案，以 JSON 格式輸出，不要任何額外說明。"

USER_PROMPT_TEMPLATE = """根據以下需求，為 EDM 各區塊撰寫繁體中文文案，以 JSON 格式輸出。

需求：
- 產品／服務名稱：{product_name}
- 活動類型：{promotion_type}
- 核心訊息：{key_message}
- 目標受眾：{target_audience}
- 語氣風格：{tone}

請輸出以下 JSON 結構（每個 key 的說明僅供參考，不要出現在輸出中）：
{schema_json}

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
        LLM 只負責生成文案 JSON，Python 做模板替換。
        """
        copy = self._generate_copy(requirements)
        return self._render(copy)

    def _generate_copy(self, requirements: dict) -> dict:
        """呼叫 LLM，取得各區塊的文案 JSON"""
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
        )

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=1024,
        )

        raw = response.choices[0].message.content.strip()

        # 去掉可能的 markdown 包裝
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        return json.loads(raw)

    def _render(self, copy: dict) -> str:
        """將文案 JSON 填入 HTML 模板"""
        html = self.template
        for key, value in copy.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))
        return html
