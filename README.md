# 行銷 EDM 產生器

一個用於產生行銷 EDM 圖文素材的工具。

## 功能特色

### 第一階段：素材工廠（Material Factory）

- **自動貼標系統**：使用 LLM API 為素材元件自動生成語義標籤
- **標籤分類**：
  - 類型（人物/背景/裝飾/物件/文字）
  - 風格（插畫/扁平/寫實/手繪/3D等）
  - 情境（通勤/家庭/旅行/工作等）
  - 色系（暖色/冷色/中性/鮮豔等）
  - 氛圍（歡樂/專業/溫馨/活力等）
  - 可用範圍描述
  - 關鍵字
- **語義搜尋**：根據標籤快速找到適合的素材元件
- **批次處理**：一次處理多個素材檔案
- **Web 介面**：React 前端 + FastAPI 後端，提供直觀的使用者介面

## 安裝

### 後端設定

1. 建立並啟動虛擬環境：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 設定環境變數：
編輯 `.env` 檔案並填入您的 OpenAI API Key：
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o  # 或使用其他支援視覺的模型
```

### 前端設定

1. 進入前端目錄：
```bash
cd frontend
```

2. 安裝依賴：
```bash
npm install
```

## 啟動方式

### 完整啟動流程

#### 方式一：使用啟動腳本（推薦）

**終端機 1 - 啟動後端：**
```bash
# 在專案根目錄執行
./start_backend.sh
```

**終端機 2 - 啟動前端：**
```bash
cd frontend
npm run dev
```

#### 方式二：手動啟動

**步驟 1：啟動後端 API**

```bash
# 1. 進入專案目錄
cd /Users/samlai/Documents/creative_agent

# 2. 啟動虛擬環境
source venv/bin/activate

# 3. 啟動 FastAPI 伺服器
uvicorn api.main:app --reload --port 8000
```

後端 API 將在 `http://localhost:8000` 運行
- API 文檔：`http://localhost:8000/docs`
- 健康檢查：`http://localhost:8000/health`

**步驟 2：啟動前端（新開一個終端機）**

```bash
# 1. 進入前端目錄
cd /Users/samlai/Documents/creative_agent/frontend

# 2. 啟動開發伺服器
npm run dev
```

前端將在 `http://localhost:5173` 運行（Vite 預設端口）

#### 啟動順序

1. **先啟動後端**：確保 API 服務正常運行
2. **再啟動前端**：前端會連接到後端 API

#### 驗證服務是否正常

**檢查後端：**
```bash
# 在瀏覽器訪問或使用 curl
curl http://localhost:8000/health
# 應該返回: {"status":"ok"}
```

**檢查前端：**
- 在瀏覽器訪問 `http://localhost:5173`
- 應該看到「EDM 素材工廠」首頁

#### 停止服務

- **後端**：在終端機按 `Ctrl + C`
- **前端**：在終端機按 `Ctrl + C`

### 快速啟動檢查清單

- [ ] 虛擬環境已建立並啟動
- [ ] 後端依賴已安裝（`pip install -r requirements.txt`）
- [ ] `.env` 檔案已設定 OpenAI API Key
- [ ] 前端依賴已安裝（`cd frontend && npm install`）
- [ ] 後端服務正在運行（`http://localhost:8000`）
- [ ] 前端服務正在運行（`http://localhost:5173`）

## 使用方式

### Web 介面

1. 開啟瀏覽器訪問 `http://localhost:5173`
2. **上傳素材**：
   - 點擊「上傳素材」標籤
   - 拖放圖片或點擊選擇檔案
   - 點擊「上傳並貼標」按鈕
   - 系統會自動上傳並為素材貼標
3. **查看素材**：
   - 點擊「素材列表」標籤
   - 查看所有已貼標的素材
   - 每個素材卡片會顯示圖片和完整的標籤資訊
4. **搜尋素材**：
   - 在素材列表頁面使用搜尋欄
   - 可以根據類型、色系、關鍵字等條件搜尋

### 命令列介面 (CLI)

#### 為素材貼標

**單一檔案：**
```bash
python cli.py tag --file assets/example.jpg
```

**批次處理（整個目錄）：**
```bash
python cli.py tag --dir assets/
```

**強制更新已存在的標籤：**
```bash
python cli.py tag --dir assets/ --force
```

#### 搜尋素材

根據標籤搜尋素材：
```bash
# 搜尋「人物」類型的「插畫」風格素材
python cli.py search --category 人物 --style 插畫

# 搜尋「家庭」情境的素材
python cli.py search --scenario 家庭

# 搜尋包含特定關鍵字的素材
python cli.py search --keywords 旅行 假期
```

#### 查看統計資訊

```bash
python cli.py stats
```

### Python API

```python
from src.material_factory import MaterialFactory
from pathlib import Path

factory = MaterialFactory()

# 為單一素材貼標
tags = factory.tag_single_material(Path("assets/example.jpg"))

# 批次處理
results = factory.tag_batch_materials()

# 搜尋素材
results = factory.search_materials(
    category="人物",
    style=["插畫"],
    scenario=["家庭"]
)

# 查看統計
stats = factory.get_material_stats()
```

## 專案結構

```
creative_agent/
├── venv/              # 虛擬環境
├── api/               # FastAPI 後端
│   ├── main.py        # API 入口
│   ├── models.py      # Pydantic 模型
│   ├── utils.py       # 工具函數
│   └── routes/        # API 路由
│       └── materials.py
├── src/               # 原始碼
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── image_analyzer.py   # 圖片分析
│   ├── llm_tagger.py       # LLM 標籤生成
│   ├── tag_database.py     # 標籤資料庫
│   └── material_factory.py # 素材工廠主程式
├── frontend/          # React 前端
│   ├── src/
│   │   ├── components/    # React 元件
│   │   ├── services/      # API 服務
│   │   └── App.jsx        # 主應用程式
│   └── package.json
├── templates/         # EDM 範本
├── assets/           # 素材資源（圖片、字體等）
├── output/           # 產生的圖文素材輸出
├── data/             # 資料庫（標籤 JSON）
├── cli.py            # 命令列介面
├── example_usage.py  # 使用範例
├── .env              # 環境變數設定
├── .gitignore        # Git 忽略檔案
├── requirements.txt  # Python 依賴套件
└── README.md         # 專案說明
```

## API 端點

### 素材相關

- `POST /api/materials/upload` - 上傳圖片素材
- `POST /api/materials/tag` - 為素材貼標
- `GET /api/materials` - 取得所有已貼標素材
- `GET /api/materials/{file_path}` - 取得單一素材標籤
- `GET /api/materials/image/{file_path}` - 取得素材圖片
- `POST /api/materials/search` - 搜尋素材
- `GET /api/materials/stats` - 取得統計資訊
- `DELETE /api/materials/{file_path}` - 刪除素材

### 生成相關（第二階段）

- `POST /api/generation/generate` - 生成 EDM
- `GET /api/generation/layouts` - 取得可用版面配置
- `GET /api/generation/preview-materials` - 預覽素材

詳細 API 文檔請訪問 `http://localhost:8000/docs`

## 工作流程

```
┌─────────────────────────────┐
│ 第一次素材貼標（語義建立） │
│  - 類型（人物/背景/裝飾）     │
│  - 風格（插畫/扁平/寫實）     │
│  - 情境（通勤/家庭/旅行）     │
│  - 色系 / 氛圍 / 可用範圍     │
│  → 建立「語義錨點」           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 標籤儲存到資料庫             │
│ (data/material_tags.json)    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 使用者輸入需求               │
│ → 透過標籤搜尋適合的素材     │
└─────────────────────────────┘
```

## 快速開始

### 第一次使用

1. **安裝後端依賴**：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

2. **設定 API Key**：
編輯 `.env` 檔案，填入 `OPENAI_API_KEY`

3. **安裝前端依賴**：
```bash
cd frontend
npm install
cd ..
```

4. **啟動服務**（需要兩個終端機）：
   - 終端機 1：`./start_backend.sh` 或 `uvicorn api.main:app --reload --port 8000`
   - 終端機 2：`cd frontend && npm run dev`

5. **訪問應用程式**：
   - 打開瀏覽器訪問 `http://localhost:5173`

### 日常使用

每次使用時，只需啟動兩個服務：

**終端機 1 - 後端：**
```bash
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**終端機 2 - 前端：**
```bash
cd frontend
npm run dev
```

## 注意事項

- **需要有效的 OpenAI API Key**：在 `.env` 檔案中設定
- **API 費用**：使用 Vision API 會產生費用，請注意使用量
- **資料儲存**：標籤資料儲存在 `data/material_tags.json`
- **圖片格式**：支援 JPG, PNG, GIF, WebP, BMP
- **服務依賴**：前端和後端需要同時運行才能正常使用 Web 介面
- **端口衝突**：如果 8000 或 5173 端口被占用，請修改對應的端口設定

## 故障排除

### 後端無法啟動

- 檢查虛擬環境是否已啟動：`which python` 應該指向 `venv/bin/python`
- 檢查依賴是否安裝：`pip list | grep fastapi`
- 檢查端口是否被占用：`lsof -i :8000`

### 前端無法啟動

- 檢查 Node.js 版本：`node --version`（建議 v18+）
- 檢查依賴是否安裝：`cd frontend && ls node_modules`
- 重新安裝依賴：`cd frontend && rm -rf node_modules && npm install`

### API 連接失敗

- 確認後端正在運行：訪問 `http://localhost:8000/health`
- 檢查 CORS 設定：確認前端 URL 在後端的允許列表中
- 檢查瀏覽器控制台是否有錯誤訊息