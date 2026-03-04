"""
一次性腳本：將 edm_full_01.png 轉換為 HTML reference template。
輸出存至 templates/html/edm_base.html。

用法：
    source venv/bin/activate
    python scripts/generate_base_html.py
"""
import base64
import sys
from pathlib import Path

# 將專案根目錄加入 path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from openai import OpenAI

REFERENCE_PATH = ROOT / "templates" / "references" / "edm_full_01.png"
OUTPUT_PATH = ROOT / "templates" / "html" / "edm_base.html"

PROMPT = """請將這張 EDM 圖片轉換為 HTML。

要求：
1. 還原圖片中的版型結構、配色、字體大小層級
2. 忽略所有圖示／插畫／照片（人物、救護車、醫療箱等），只保留文字內容與背景色塊
3. 使用 inline CSS，不要外部 CSS 檔
4. 固定寬度 600px，高度自適應
5. 中文字體：font-family: 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif
6. 直接輸出純 HTML，不要 markdown 包裝，不要 ```html 標記
7. HTML 從 <!DOCTYPE html> 開始"""


def main():
    if not REFERENCE_PATH.exists():
        print(f"錯誤：找不到 reference 圖片：{REFERENCE_PATH}")
        sys.exit(1)

    print(f"讀取圖片：{REFERENCE_PATH}")
    with open(REFERENCE_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(api_key=OPENAI_API_KEY)

    print(f"呼叫 {OPENAI_MODEL} Vision API...")
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                            "detail": "high",
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        max_completion_tokens=4096,
    )

    html_content = response.choices[0].message.content.strip()

    # 若 LLM 還是包了 markdown，去掉它
    if html_content.startswith("```"):
        lines = html_content.split("\n")
        html_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html_content, encoding="utf-8")
    print(f"完成！HTML 已存至：{OUTPUT_PATH}")
    print(f"用瀏覽器開啟驗證：open {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
