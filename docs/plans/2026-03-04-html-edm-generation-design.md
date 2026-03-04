# HTML EDM Generation — Design Doc

**Date:** 2026-03-04
**Status:** Approved

## Problem

現有 generation pipeline 用 region 偵測 + image overlay 的方式將文字貼在圖片上。這種方式不彈性：文字稍長就溢出框格，無法自動換行調整版面。

## Solution

改為 LLM 直接生成 HTML EDM。HTML 天然支援文字自動換行、版面彈性調整，不再有溢出問題。

## Architecture

### Generation Flow

```
User 輸入 (product_name, promotion_type, key_message, target_audience, tone)
  ↓
POST /api/generation/generate-html
  ↓
HTMLGenerator
  ├── 讀取 templates/html/edm_base.html（靜態 reference）
  └── 組 prompt → OpenAI → 回傳完整 HTML string
  ↓
前端 <iframe srcdoc={html} /> 顯示
```

### Reference HTML 產生方式（一次性）

執行 `scripts/generate_base_html.py`：
- 傳 `templates/references/edm_full_01.png` 給 OpenAI Vision API
- 請 LLM 輸出對應的 HTML/inline CSS（忽略圖示，只保留文字版型）
- 輸出存至 `templates/html/edm_base.html`
- 之後可手動微調，靜態存在 repo 中

### Prompt 設計

```
你是 EDM 設計師，請根據以下需求生成一份 HTML EDM。

參考範本：
<reference_html>
{edm_base.html 內容}
</reference_html>

需求：
- 產品名稱：{product_name}
- 活動類型：{promotion_type}
- 核心訊息：{key_message}
- 目標受眾：{target_audience}
- 語氣風格：{tone}

規則：
1. 維持相似的版型結構和視覺風格
2. 所有文字改為符合需求的新文案（使用繁體中文）
3. 配色可微調但維持整體感
4. 輸出純 HTML（含 inline CSS），不要 markdown、不要 ```html 標記
5. 寬度固定 600px（EDM 標準）
6. 不包含任何 <img> 標籤（此階段忽略素材圖片）
```

## Files Changed

### New Files
- `scripts/generate_base_html.py` — 一次性腳本，Vision API 轉 HTML
- `templates/html/edm_base.html` — 由腳本產生的靜態 reference HTML
- `src/generator/html_generator.py` — HTMLGenerator class
- `frontend/src/components/EDMGenerator/EDMPreview.jsx` — iframe 顯示元件

### Modified Files
- `api/routes/generation.py` — 新增 `POST /api/generation/generate-html`
- `frontend/src/components/EDMGenerator/GenerationForm.jsx` — 移除 template 選擇，改呼叫新 endpoint
- `frontend/src/services/api.js` — 新增 `generateHtml()` 函式
- `frontend/src/components/EDMGenerator/EDMGenerator.jsx` — 整合新流程，換掉舊 canvas 顯示

### Unchanged (舊流程保留但不主動使用)
- `src/generator/layout_engine.py`
- `src/generator/template_engine.py`
- `src/generator/template_region_detector.py`
- `src/generator/copywriter.py`

## Implementation Steps

1. 執行 `generate_base_html.py` 產生 `edm_base.html`
2. 實作 `html_generator.py`
3. 新增 `/api/generation/generate-html` endpoint
4. 修改前端 `GenerationForm.jsx` + `api.js`
5. 新增 `EDMPreview.jsx`，整合進 `EDMGenerator.jsx`
6. 端對端測試

## Out of Scope (此次)

- 素材圖片（人物、救護車等）嵌入 HTML
- 多個 HTML 版型選擇
- HTML 匯出 / 下載功能
