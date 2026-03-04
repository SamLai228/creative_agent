"""HTML EDM 生成器：以 edm_base.html 為 reference，LLM 生成新的 HTML 變體"""
from pathlib import Path
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

BASE_HTML_PATH = Path(__file__).parent.parent.parent / "templates" / "html" / "edm_base.html"

SYSTEM_PROMPT = """你是一位 EDM 文案撰寫專家。
你的任務是：給定一份 HTML EDM 範本和新的需求，**完整保留 HTML 結構與 CSS 樣式，只替換文字內容**。
請直接輸出純 HTML，不要任何 markdown 包裝或說明文字。"""

USER_PROMPT_TEMPLATE = """以下是一份 HTML EDM 範本。請根據新需求，**只修改文字內容**，輸出完整 HTML。

規則（嚴格遵守）：
1. HTML 結構、div 層級、class、inline style 全部原封不動複製
2. 只替換各區塊內的文字（標題、內文、按鈕文字、說明文字）
3. 不可新增、刪除或重排任何 div 區塊
4. 不可修改任何 CSS 屬性（顏色、字體大小、padding、border-radius 等全部保持不變）
5. 輸出純 HTML，從 <!DOCTYPE html> 開始，不含 markdown 標記

新需求：
- 產品／服務名稱：{product_name}
- 活動類型：{promotion_type}
- 核心訊息：{key_message}
- 目標受眾：{target_audience}
- 語氣風格：{tone}

範本 HTML：
{reference_html}"""


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
