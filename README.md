# 行銷 EDM 素材工廠

LLM 驅動的 EDM 生成工具：上傳圖片素材 → 自動貼標 → 語義搜尋 → 生成 EDM 圖文。

---

## 目錄

1. [環境需求](#環境需求)
2. [首次安裝](#首次安裝)
3. [啟動服務](#啟動服務)
4. [使用方式](#使用方式)
   - [素材管理（Web）](#素材管理web)
   - [EDM 生成（Web）](#edm-生成web)
   - [CLI 工具](#cli-工具)
5. [API 端點](#api-端點)
6. [排錯指南](#排錯指南)

---

## 環境需求

| 工具 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 20.19+ 或 22.12+ |
| OpenAI API Key | 需支援 Vision（gpt-4o 以上） |

---

## 首次安裝

```bash
# 1. 建立並啟動 Python 虛擬環境
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 2. 安裝後端依賴
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env            # 若無 .env.example 則直接建立 .env
# 編輯 .env，填入：
#   OPENAI_API_KEY=sk-...
#   OPENAI_MODEL=gpt-4o

# 4. 安裝前端依賴
cd frontend && npm install && cd ..
```

---

## 啟動服務

需要開啟**兩個終端機**同時運行。

**終端機 1 — 後端（port 8000）：**
```bash
source venv/bin/activate
./start_backend.sh
# 或手動：uvicorn api.main:app --reload --port 8000
```

**終端機 2 — 前端（port 5173）：**
```bash
./start_frontend.sh
# 或手動：cd frontend && npm run dev
```

### 驗證服務正常

```bash
# 後端健康檢查
curl http://localhost:8000/health
# → {"status":"ok"}

# 前端
open http://localhost:5173
```

### 停止服務

各終端機按 `Ctrl + C`，或強制關閉：
```bash
kill $(lsof -ti :8000)   # 關閉後端
kill $(lsof -ti :5173)   # 關閉前端
```

---

## 使用方式

### 素材管理（Web）

1. 開啟 `http://localhost:5173`
2. **上傳素材** 標籤 → 拖放圖片 → 點擊「上傳並貼標」
3. **素材列表** 標籤 → 查看所有素材、標籤、搜尋

### EDM 生成（Web）

1. 切換到 **EDM 生成** 標籤
2. 選擇 Template（需先在 `templates/images/` 放入 template 圖片）
3. 若 Template 還沒有 region 配置，先執行偵測：
   ```bash
   # 從含文字的完稿 EDM 自動偵測（推薦）
   curl -X POST "http://localhost:8000/api/generation/detect-regions-from-reference?template_name=edm_template_01.jpeg&reference_name=edm_full_01.png"

   # 或直接分析空白 template（準確度較低）
   curl -X POST "http://localhost:8000/api/generation/detect-template-regions?template_name=edm_template_01.jpeg"
   ```
4. 填寫產品名稱、促銷類型、主要訊息等需求 → 點擊「生成文案並進入編輯」
5. 在互動式編輯器中調整文字：
   - **單擊** 選取區域
   - **拖移** 調整位置
   - **雙擊** 直接輸入文字
   - 工具列：`A-` / `A+` 調整字級、`B` 切換粗體、色塊更換顏色
6. 點擊「匯出 PNG」→ 後端渲染 → 下載最終圖檔

### CLI 工具

```bash
source venv/bin/activate

# 單一檔案貼標
python cli.py tag --file assets/example.jpg

# 批次貼標（強制重建）
python cli.py tag --dir assets/ --force

# 搜尋素材
python cli.py search --category 人物 --style 插畫

# 統計資訊
python cli.py stats
```

---

## API 端點

完整互動式文件：`http://localhost:8000/docs`

### 素材管理

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/materials/upload` | 上傳圖片 |
| POST | `/api/materials/tag` | 為素材貼標 |
| GET | `/api/materials` | 取得所有素材 |
| POST | `/api/materials/search` | 搜尋素材 |
| GET | `/api/materials/stats` | 統計資訊 |
| DELETE | `/api/materials/{file_path}` | 刪除素材 |

### EDM 生成

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/generation/templates` | 列出所有 template |
| GET | `/api/generation/template-regions` | 取得 template region 配置 |
| POST | `/api/generation/detect-template-regions` | 分析空白 template 偵測區域 |
| POST | `/api/generation/detect-regions-from-reference` | 從完稿 EDM 偵測區域（推薦） |
| POST | `/api/generation/generate-copy-for-template` | LLM 生成各區域文案 |
| POST | `/api/generation/render-with-copy` | 渲染文字到 template，輸出 PNG |

### 靜態資源

| 路徑 | 說明 |
|------|------|
| `/assets/{filename}` | 素材圖片 |
| `/templates/{filename}` | Template 圖片 |
| `/output/{path}` | 生成的 EDM 圖檔 |

---

## 排錯指南

### 後端無法啟動

```bash
# 確認虛擬環境
which python   # 應指向 venv/bin/python

# 確認 port 是否被佔用
lsof -i :8000
kill $(lsof -ti :8000)   # 強制釋放

# 重新安裝依賴
pip install -r requirements.txt
```

### 前端無法啟動

```bash
# 確認 Node 版本（需 20.19+ 或 22.12+）
node --version

# 確認 port 是否被佔用
lsof -i :5173

# 重新安裝依賴
cd frontend && rm -rf node_modules && npm install
```

### EDM 生成失敗

| 錯誤訊息 | 解決方式 |
|---------|---------|
| `找不到 template 配置` | 先呼叫 `/detect-template-regions` 或 `/detect-regions-from-reference` |
| `Template 不存在` | 確認圖片放在 `templates/images/` 目錄下 |
| `文案生成失敗` | 確認 `.env` 中 `OPENAI_API_KEY` 有效 |
| `渲染失敗` | 確認 `output/` 目錄存在（服務啟動時會自動建立） |

### API 連線失敗

- 確認後端運行：`curl http://localhost:8000/health`
- 確認 Vite proxy 設定包含 `/templates` 和 `/output`（已設定於 `frontend/vite.config.js`）
- 查看瀏覽器 DevTools Console 的錯誤訊息

---

## 目錄結構

```
creative_agent/
├── api/                    # FastAPI 後端
│   ├── main.py             # 入口、CORS、StaticFiles
│   ├── models.py           # Pydantic 模型
│   └── routes/
│       ├── materials.py    # 素材 API
│       └── generation.py   # 生成 API
├── src/
│   ├── config.py           # 目錄設定、API Key
│   ├── material_factory/   # 素材貼標 pipeline
│   └── generator/          # EDM 生成 pipeline
│       ├── layout_engine.py        # 圖文合成
│       ├── template_engine.py      # Template 載入
│       ├── template_region_detector.py  # Region 偵測
│       ├── copywriter.py           # LLM 文案生成
│       └── edm_generator.py        # 整合入口
├── frontend/src/
│   ├── components/
│   │   ├── EDMGenerator/   # EDM 生成互動編輯器
│   │   ├── MaterialUpload/ # 素材上傳
│   │   └── MaterialList/   # 素材列表
│   └── services/api.js     # 所有 API 呼叫
├── templates/
│   ├── images/             # 空白 template 圖片
│   ├── references/         # 含文字的完稿 EDM（偵測用）
│   └── configs/            # Region 配置 JSON
├── assets/                 # 素材圖片
├── output/edm/             # 生成的 EDM 圖檔
├── data/material_tags.json # 標籤資料庫
├── .env                    # 環境變數（不提交 git）
└── requirements.txt
```
