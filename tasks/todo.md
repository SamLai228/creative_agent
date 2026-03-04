# HTML EDM Generation — Implementation Plan

**Design doc:** `docs/plans/2026-03-04-html-edm-generation-design.md`

---

## Step 1：產生 Reference HTML（一次性）

**目標：** 執行腳本，把 `edm_full_01.png` 轉成靜態 HTML，存至 `templates/html/edm_base.html`

**新增 `scripts/generate_base_html.py`：**
- 讀取 `templates/references/edm_full_01.png`，轉 base64
- 呼叫 `openai.chat.completions.create`（model: gpt-4o，含 image_url）
- Prompt：「請將此 EDM 圖片轉換為 HTML + inline CSS，忽略所有圖示/圖片元素，只保留文字版型與配色，寬度 600px，輸出純 HTML 不含 markdown」
- 將輸出存至 `templates/html/edm_base.html`

**執行：**
```bash
source venv/bin/activate
python scripts/generate_base_html.py
```

**驗證：** 用瀏覽器開啟 `templates/html/edm_base.html`，確認版型與原圖相似。

---

## Step 2：實作 `HTMLGenerator`

**新增 `src/generator/html_generator.py`：**

```python
class HTMLGenerator:
    def __init__(self):
        # 讀取 edm_base.html，存為 self.reference_html

    def generate(self, requirements: dict) -> str:
        # requirements keys: product_name, promotion_type, key_message,
        #                     target_audience, tone
        # 組 prompt（含 reference_html + requirements）
        # 呼叫 openai.chat.completions.create
        # 回傳純 HTML string
```

**驗證：** 寫一個簡單 test，確認輸出是 HTML string 且包含 `<html` 或 `<!DOCTYPE`。

---

## Step 3：新增 API Endpoint

**修改 `api/routes/generation.py`：**

新增：
```python
@router.post("/generate-html")
async def generate_html(request: GenerateHTMLRequest):
    # 呼叫 HTMLGenerator().generate(request.dict())
    # 回傳 { "html": "..." }
```

**新增到 `api/models.py`（或 inline）：**
```python
class GenerateHTMLRequest(BaseModel):
    product_name: str
    promotion_type: str
    key_message: str
    target_audience: str
    tone: str
```

**驗證：**
```bash
curl -X POST http://localhost:8000/api/generation/generate-html \
  -H "Content-Type: application/json" \
  -d '{"product_name":"健康寶","promotion_type":"新品上市","key_message":"守護全家健康","target_audience":"30-50歲家長","tone":"溫暖專業"}'
```
確認回傳 JSON 含 `html` 欄位。

---

## Step 4：前端 API 層

**修改 `frontend/src/services/api.js`：**

新增：
```js
export async function generateHtml(requirements) {
  const res = await axios.post('/api/generation/generate-html', requirements);
  return res.data; // { html: "..." }
}
```

---

## Step 5：修改 GenerationForm

**修改 `frontend/src/components/EDMGenerator/GenerationForm.jsx`：**
- 移除 template 選擇下拉選單及相關 state (`templates`, `selectedTemplate`)
- 移除 `getTemplates`、`getTemplateRegions`、`generateCopyForTemplate` import
- import `generateHtml`
- `handleSubmit` 改為：呼叫 `generateHtml(formValues)` → 取得 `html` → 呼叫 `onComplete(html)`
- 保留 5 個輸入欄位不變

---

## Step 6：新增 EDMPreview + 整合

**新增 `frontend/src/components/EDMGenerator/EDMPreview.jsx`：**
```jsx
function EDMPreview({ html }) {
  return (
    <iframe
      srcDoc={html}
      style={{ width: '100%', height: '800px', border: 'none' }}
      title="EDM Preview"
    />
  );
}
```

**修改 `frontend/src/components/EDMGenerator/EDMGenerator.jsx`：**
- `onComplete` callback 接收 `html` string（而非舊的 template + regions）
- 移除 `EDMCanvas` 相關邏輯，改用 `<EDMPreview html={html} />`

---

## 完成驗證

1. 啟動 backend + frontend
2. 前端填入需求，按送出
3. 出現 iframe 顯示 HTML EDM
4. 確認文字符合輸入需求
5. 確認版型與 edm_base.html 風格相似
