"""HTML EDM 生成器：LLM 只生成文案 JSON，Python 做模板替換，確保版型 100% 保留"""
import json
import re
from pathlib import Path
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "html" / "edm_base_template.html"

# 模板中所有 placeholder 的說明，提供給 LLM
PLACEHOLDER_SCHEMA = {
    "title_1":              "主標題第一行（約 12–18 字）",
    "title_2":              "主標題第二行（約 8–14 字，可為副標題或延伸）",
    "body_paragraph":       "正文段落，2–3 句話，說明情境或問題（用 <br/> 換行）",
    "question_pill":        "引導問句，用膠囊框呈現（約 12–18 字）",
    "supporting_text":      "補充說明，2–3 句話，呼應問句（用 <br/> 換行）",
    "cta_button":           "主要 CTA 按鈕文字（5–10 字，不含 >）",
    "product_section_label":"產品區塊標題（約 8–12 字，帶省略號結尾）",
    "product_name":         "產品正式名稱",
    "product_subtitle":     "產品副名稱或類型說明",
    "closing_quote":        "結尾激勵金句，2–3 行（用 <br/> 換行）",
    "consult_button":       "諮詢按鈕文字（3–6 字，不含 >）",
    "consult_note":         "按鈕下方輔助說明（一句話，約 10 字）",
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
