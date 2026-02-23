# Swagger UI 測試 Template 功能指南

## 前置準備

1. **確認後端服務已啟動**
   ```bash
   # 啟動後端（如果還沒啟動）
   ./start_backend.sh
   # 或
   source venv/bin/activate
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **開啟 Swagger UI**
   - 在瀏覽器中開啟：`http://localhost:8000/docs`
   - 或使用 ReDoc：`http://localhost:8000/redoc`

## 測試步驟

### 步驟 1：找到生成端點

在 Swagger UI 中，找到 **`POST /api/generation/generate`** 端點，點擊展開。

### 步驟 2：準備測試資料

點擊 **"Try it out"** 按鈕，然後在 Request body 中填入以下 JSON：

#### 範例 1：使用 Template + 手動提供標題和內文

```json
{
  "template": "edm_template_01.jpeg",
  "title": "完善保障，守護未來",
  "description": "立即了解保障方案，為您與家人規劃最適合的保險計畫",
  "layout": "centered",
  "output_format": "png"
}
```

#### 範例 2：使用 Template + 自動生成文案（意外險）

```json
{
  "template": "edm_template_01.jpeg",
  "product_name": "意外險",
  "product_info": "提供意外傷害保障，包含意外醫療、意外住院、意外失能等保障",
  "target_audience": "一般消費者",
  "tone": "安心、專業",
  "layout": "centered",
  "output_format": "png"
}
```

#### 範例 3：使用 Template + 完整文案生成參數

```json
{
  "template": "edm_template_01.jpeg",
  "product_name": "醫療險",
  "promotion_type": "新商品上市",
  "key_message": "完善的醫療保障，讓您安心就醫",
  "call_to_action": "立即諮詢",
  "product_info": "提供住院醫療、手術醫療、門診醫療等全方位保障",
  "target_audience": "30-50歲有家庭責任的上班族",
  "tone": "專業、溫暖",
  "layout": "centered",
  "output_format": "png"
}
```

### 步驟 3：執行請求

1. 確認 JSON 格式正確（沒有語法錯誤）
2. 點擊 **"Execute"** 按鈕
3. 等待回應（可能需要幾秒鐘）

### 步驟 4：查看結果

成功後，您會看到：

```json
{
  "output_path": "output/edm/edm_20260210_xxxxxx.png",
  "materials_used": [...],
  "layout": "centered",
  "message": "EDM 生成成功"
}
```

### 步驟 5：查看生成的 EDM

生成的 EDM 圖片會保存在 `output/edm/` 目錄下，檔名格式為 `edm_YYYYMMDD_HHMMSS.png`。

您可以直接在檔案系統中開啟查看，或使用以下方式：

```bash
# 在終端機中開啟（macOS）
open output/edm/edm_*.png

# 或使用 Python
from pathlib import Path
from PIL import Image
img = Image.open("output/edm/edm_20260210_xxxxxx.png")
img.show()
```

## 欄位說明

### Template 相關
- **`template`** (可選): Template 圖片檔名，放在 `templates/images/` 目錄下
  - 範例：`"edm_template_01.jpeg"`
  - 如果未提供，系統會使用背景素材或純色背景

### 文案相關（可選，如果未提供 title/description 則自動生成）
- **`title`** (可選): EDM 標題
- **`description`** (可選): EDM 內文
- **`product_name`**: 產品名稱（用於自動生成文案）
- **`product_info`**: 產品資訊（用於自動生成文案）
- **`target_audience`**: 目標受眾（用於自動生成文案）
- **`tone`**: 文案風格（用於自動生成文案）

### 版面相關
- **`layout`** (可選): 版面配置名稱
  - 可用選項：`"centered"`, `"left-aligned"`, `"hero"`, `"grid"`
  - 預設：`"centered"`

### 輸出相關
- **`output_format`** (可選): 輸出格式
  - 選項：`"png"` 或 `"pdf"`
  - 預設：`"png"`

## 常見問題

### Q: Template 找不到怎麼辦？
A: 確認：
1. Template 檔案是否放在 `templates/images/` 目錄下
2. 檔名是否完全一致（包含副檔名）
3. 檔案格式是否支援（PNG, JPG, JPEG）

### Q: 中文顯示不出來？
A: 已修正中文字體問題，如果仍有問題，請檢查：
1. 系統是否有中文字體（macOS 預設有 PingFang）
2. 查看終端機是否有字體載入錯誤訊息

### Q: 如何知道有哪些可用的 Template？
A: 查看 `templates/images/` 目錄下的檔案列表

### Q: 如何知道有哪些可用的 Layout？
A: 使用 **`GET /api/generation/layouts`** 端點查詢

## 其他有用的端點

### 查詢可用版面配置
- **`GET /api/generation/layouts`**
- 返回所有可用的版面配置名稱列表

### 預覽素材選擇
- **`GET /api/generation/preview-materials`**
- 根據條件預覽會選擇哪些素材（不實際生成 EDM）

### 獨立生成文案
- **`POST /api/generation/generate-copy`**
- 只生成文案，不生成完整 EDM
