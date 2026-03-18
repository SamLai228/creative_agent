# 行銷 EDM 素材工廠

LLM 驅動的 EDM 生成工具：上傳圖片素材 → 自動去背 → 自動貼標 → 語義搜尋 → 生成 HTML EDM。

---

## 目錄

1. [環境需求](#環境需求)
2. [首次安裝](#首次安裝)
3. [啟動服務](#啟動服務)
4. [使用方式](#使用方式)
   - [素材管理（Web）](#素材管理web)
   - [EDM 生成（Web）](#edm-生成web)
   - [CLI 工具](#cli-工具)
5. [功能說明](#功能說明)
   - [Material Factory（素材工廠）](#material-factory素材工廠)
   - [Generator（EDM 生成器）](#generatoredm-生成器)
6. [API 端點](#api-端點)
7. [排錯指南](#排錯指南)
8. [目錄結構](#目錄結構)

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
   - 上傳後自動執行**去背**，產生透明背景版本（`_nobg.png`）
   - 去背完成後 LLM 自動分析圖片，生成類型、風格、情境、色系、氛圍等標籤
3. **素材列表** 標籤 → 查看所有素材、標籤、搜尋

### EDM 生成（Web）

1. 切換到 **EDM 生成** 標籤
2. 填寫產品名稱、活動類型、核心訊息、目標受眾、語氣風格等需求
3. 點擊「生成 EDM」→ 後端自動：
   - 呼叫 LLM 生成各區塊文案
   - 根據文案內容智慧選取匹配的人物素材（使用去背版本）
   - 將文案與素材填入 HTML 模板，輸出完整 EDM
4. 預覽生成的 HTML EDM，可直接複製或下載使用

### CLI 工具

```bash
source venv/bin/activate

# 單一檔案貼標（含自動去背）
python cli.py tag --file assets/example.jpg

# 批次貼標（強制重建）
python cli.py tag --dir assets/ --force

# 批次去背（不重新貼標）
python cli.py remove-bg --dir assets/

# 搜尋素材
python cli.py search --category 人物 --style 插畫

# 統計資訊
python cli.py stats
```

---

## 功能說明

### Material Factory（素材工廠）

素材管理的完整 pipeline，位於 `src/material_factory/`。

#### 自動去背（bg_remover.py）

- 使用 [rembg](https://github.com/danielgatis/rembg) + `birefnet-general` 模型
- 支援 alpha matting，保留白色/淺色前景物件的細節
- 輸出透明背景 PNG，檔名自動加上 `_nobg` 後綴
- 去背版本作為 EDM 生成時的預設素材來源
- 已存在去背檔案時自動跳過，`--force` 強制重新處理

#### LLM 自動貼標（llm_tagger.py）

呼叫 OpenAI Vision API 分析圖片，生成結構化標籤：

| 標籤欄位 | 說明 |
|---------|------|
| `category` | 素材類型（人物、風景、物件等） |
| `style` | 視覺風格（3D、插畫、現代、簡約等） |
| `scenario` | 使用情境（工作、家庭、休閒等） |
| `color_scheme` | 主色系 |
| `mood` | 氛圍（專業、活力、歡樂、平靜等） |
| `keywords` | 描述關鍵字 |
| `nobg_path` | 去背版本的相對路徑 |

#### 標籤資料庫（tag_database.py）

- 所有標籤儲存於 `data/material_tags.json`，無外部資料庫依賴
- 支援多維度語義搜尋（類型 + 風格 + 情境 + 色系 + 氛圍 + 關鍵字）

---

### Generator（EDM 生成器）

HTML EDM 的生成 pipeline，位於 `src/generator/`。

#### HTML 生成模式（html_generator.py）

目前的主要生成方式，版型完全由 HTML 模板控制：

- LLM 只負責生成**文案 JSON**，不產生任何 HTML 結構
- Python 做模板字串替換，版型 100% 保留
- LLM 同時根據文案內容輸出**人物素材需求**（scenario / mood / style），系統自動從素材庫選出最匹配的去背人物圖片
- 支援 1 或 2 個人物，根據文案情境決定數量

#### HTML 模板結構（templates/html/edm_base_template.html）

模板支援以下文案 placeholder：

| Placeholder | 說明 |
|-------------|------|
| `{{title}}` / `{{title_2}}` | 主標題（兩行） |
| `{{content}}` ~ `{{content_3}}` | 痛點描述（三行） |
| `{{content_4}}` | 引導問句（粗體膠囊） |
| `{{content_5}}` ~ `{{content_7}}` | 解決方案（三行） |
| `{{cta}}` | 主 CTA 按鈕 |
| `{{product_intro}}` / `{{product_name}}` | 產品推薦區 |
| `{{content_8}}` ~ `{{content_10}}` | 底部金句（三行） |
| `{{cta_2}}` | 諮詢 CTA 按鈕 |
| `{{conclusion}}` | 按鈕下方輔助說明 |
| `{{character_section}}` | 人物素材 HTML（自動填入） |

#### 素材選擇（material_selector.py）

根據 LLM 提供的人物需求，從標籤資料庫語義搜尋最匹配的去背素材。

---

## API 端點

完整互動式文件：`http://localhost:8000/docs`

### 素材管理

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/materials/upload` | 上傳圖片（自動觸發去背 + 貼標） |
| POST | `/api/materials/tag` | 為素材貼標（含去背） |
| GET | `/api/materials` | 取得所有素材 |
| POST | `/api/materials/search` | 搜尋素材 |
| GET | `/api/materials/stats` | 統計資訊 |
| DELETE | `/api/materials/{file_path}` | 刪除素材 |

### EDM 生成

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/generation/generate-html` | 生成完整 HTML EDM（主要端點） |
| POST | `/api/generation/generate-copy` | 僅生成文案 JSON |
| GET | `/api/generation/templates` | 列出所有 HTML template |

### 靜態資源

| 路徑 | 說明 |
|------|------|
| `/assets/{filename}` | 素材圖片（含去背版本） |
| `/output/{path}` | 生成的 EDM 輸出 |

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
| `找不到 HTML 模板` | 確認 `templates/html/edm_base_template.html` 存在 |
| `文案生成失敗` | 確認 `.env` 中 `OPENAI_API_KEY` 有效 |
| `選人物素材失敗` | 確認素材庫已上傳並貼標，或忽略此訊息（EDM 仍會生成，僅無人物圖） |

### 去背失敗

```bash
# 確認 rembg 已安裝
pip install rembg

# 首次執行會下載模型（birefnet-general，約數百 MB），需要網路連線
# 模型快取位置：~/.u2net/
```

### API 連線失敗

- 確認後端運行：`curl http://localhost:8000/health`
- 確認 Vite proxy 設定（`frontend/vite.config.js`）
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
│   ├── material_factory/   # 素材管理 pipeline
│   │   ├── bg_remover.py   # 自動去背（rembg）
│   │   ├── image_analyzer.py       # 圖片基本資訊擷取
│   │   ├── llm_tagger.py           # LLM Vision 自動貼標
│   │   ├── tag_database.py         # 標籤讀寫（JSON）
│   │   └── factory.py              # 整合入口
│   └── generator/          # EDM 生成 pipeline
│       ├── html_generator.py       # HTML EDM 生成（主）
│       ├── material_selector.py    # 語義搜尋選素材
│       ├── copywriter.py           # LLM 文案生成
│       └── template_engine.py      # Template 載入
├── frontend/src/
│   ├── components/
│   │   ├── EDMGenerator/   # EDM 生成介面
│   │   ├── MaterialUpload/ # 素材上傳
│   │   └── MaterialList/   # 素材列表
│   └── services/api.js     # 所有 API 呼叫
├── templates/
│   ├── html/               # HTML EDM 模板
│   ├── images/             # 圖片 template（備用）
│   ├── references/         # 完稿 EDM 參考圖
│   └── configs/            # Region 配置 JSON（備用）
├── assets/                 # 素材圖片（含 _nobg.png 去背版本）
├── output/                 # 生成的 EDM 輸出
├── data/material_tags.json # 標籤資料庫
├── .env                    # 環境變數（不提交 git）
└── requirements.txt
```
