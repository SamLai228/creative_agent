"""HTML EDM 生成器：以 edm_base.html 為 reference，LLM 生成新的 HTML 變體"""
from pathlib import Path
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

BASE_HTML_PATH = Path(__file__).parent.parent.parent / "templates" / "html" / "edm_base.html"

SYSTEM_PROMPT = """你是一位專業的 EDM 設計師，擅長撰寫 HTML EDM。
根據使用者提供的需求，生成一份繁體中文 HTML EDM。
請直接輸出純 HTML，不要任何 markdown 包裝或說明文字。"""

USER_PROMPT_TEMPLATE = """請根據以下需求，參考範本 HTML，生成一份新的 HTML EDM。

<reference_html>
{reference_html}
</reference_html>

需求：
- 產品／服務名稱：{product_name}
- 活動類型：{promotion_type}
- 核心訊息：{key_message}
- 目標受眾：{target_audience}
- 語氣風格：{tone}

規則：
1. 維持與範本相似的版型結構與視覺風格（色系、區塊配置、字體層級）
2. 所有文字改為符合需求的新繁體中文文案
3. 配色可依產品性質微調，但維持整體質感
4. 輸出純 HTML（含 inline CSS），不含 markdown 標記
5. 寬度固定 600px
6. 不包含任何 <img> 標籤"""


class HTMLGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        if not BASE_HTML_PATH.exists():
            raise FileNotFoundError(
                f"找不到 reference HTML：{BASE_HTML_PATH}\n"
                "請先執行：python scripts/generate_base_html.py"
            )
        self.reference_html = BASE_HTML_PATH.read_text(encoding="utf-8")

    def generate(self, requirements: dict) -> str:
        """
        根據需求生成 HTML EDM。

        Args:
            requirements: 包含 product_name, promotion_type, key_message,
                          target_audience, tone

        Returns:
            完整 HTML string
        """
        prompt = USER_PROMPT_TEMPLATE.format(
            reference_html=self.reference_html,
            product_name=requirements.get("product_name", ""),
            promotion_type=requirements.get("promotion_type", ""),
            key_message=requirements.get("key_message", ""),
            target_audience=requirements.get("target_audience", ""),
            tone=requirements.get("tone", ""),
        )

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=4096,
        )

        html = response.choices[0].message.content.strip()

        # 若 LLM 還是包了 markdown，去掉它
        if html.startswith("```"):
            lines = html.split("\n")
            html = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        return html
