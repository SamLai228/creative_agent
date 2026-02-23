# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 工作原則

### 規劃
- 任何非瑣碎任務（3 步以上或涉及架構決策）必須先進入 plan mode
- 遇到問題立即停下來重新規劃，不要硬撐
- 實作前寫好詳細 spec，減少模糊空間
- 計畫寫入 `tasks/todo.md`，完成後補充結果摘要

### Subagent 策略
- 大量使用 subagent 保持主 context 乾淨
- 研究、探索、平行分析都交給 subagent
- 每個 subagent 只做一件事

### 自我改善
- 被使用者糾正後：立即更新 `tasks/lessons.md`，寫下防止同樣錯誤的規則
- 每次 session 開始時回顧 `tasks/lessons.md`

### 完成驗證
- 沒有證明可以運作之前，不算完成
- 相關時比對修改前後的行為差異
- 跑測試、看 log、展示正確性

### 程式品質
- 非瑣碎修改前問自己：「有沒有更優雅的解法？」
- 若 fix 感覺很 hacky：「知道現在這些後，實作優雅的解法」
- 簡單明顯的修改不要過度設計

### 除錯
- 收到 bug report 就直接修，不需要使用者手把手
- 對著 log、錯誤、失敗測試找根因並解決

### 核心守則
- **Simplicity First**：每個改動盡可能簡單，影響最小範圍的程式碼
- **No Laziness**：找根本原因，不做臨時修補，以 senior developer 標準要求自己
- **Minimal Impact**：只改必要的地方，避免引入新問題

---

## 專案概述

行銷 EDM 素材工廠：上傳圖片素材 → LLM 自動貼標 → 語義搜尋 → 生成 EDM 圖文。分為兩個階段：
1. **Material Factory**：素材貼標與管理
2. **Generator**：EDM 排版生成

## 啟動服務

```bash
# Terminal 1 - Backend (port 8000)
./start_backend.sh

# Terminal 2 - Frontend (port 5173)
./start_frontend.sh
```

- API 文件：`http://localhost:8000/docs`
- 健康檢查：`curl http://localhost:8000/health`

Frontend 透過 Vite proxy 轉發 `/api` 和 `/assets` 到 backend，不需要直接設定 CORS。若 5173 被佔用，Vite 會自動改用下一個可用 port，此時需確認 `api/main.py` 的 `allow_origins` 包含該 port。

## 環境設定

`.env` 必填：
```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o   # 需支援 Vision
```

可選覆蓋目錄：`ASSETS_DIR`, `OUTPUT_DIR`, `TEMPLATE_DIR`（預設見 `src/config.py`）

## 架構

### Backend (`src/`)

**Material Factory** (`src/material_factory/`):
- `image_analyzer.py` → 將圖片轉為 base64 供 LLM 分析
- `llm_tagger.py` → 呼叫 OpenAI Vision API 產生結構化標籤（類型/風格/情境/色系/氛圍/關鍵字）
- `tag_database.py` → 讀寫 `data/material_tags.json`
- `factory.py` → 整合以上三者的主入口

**Generator** (`src/generator/`):
- `material_selector.py` → 根據需求從 tag_database 搜尋素材
- `template_engine.py` + `layout_engine.py` → 載入 `templates/` 並套用素材
- `template_region_detector.py` → 偵測 EDM 範本中的素材區域
- `output_handler.py` → 輸出到 `output/`
- `copywriter.py` → LLM 生成文案
- `edm_generator.py` → 整合生成流程的主入口

**API** (`api/`):
- `routes/materials.py` → 素材上傳、貼標、搜尋、刪除
- `routes/generation.py` → EDM 生成、版面預覽
- `main.py` → FastAPI 入口，掛載靜態檔 `/assets`

### Frontend (`frontend/src/`)

- `services/api.js` → 所有 API 呼叫集中於此，`API_BASE_URL = ''`（走 Vite proxy）
- `components/` → React 元件
- `App.jsx` → 主應用

### 資料流

```
assets/（圖片）
  → material_factory → data/material_tags.json
  → generator → output/（生成的 EDM）
```

標籤資料庫為單一 JSON 檔 `data/material_tags.json`，無外部資料庫依賴。

## CLI

```bash
source venv/bin/activate

python cli.py tag --file assets/example.jpg        # 單一檔案貼標
python cli.py tag --dir assets/ --force            # 批次貼標（強制更新）
python cli.py search --category 人物 --style 插畫  # 搜尋素材
python cli.py stats                                # 統計資訊
```

## 常用排錯

```bash
# 檢查 port 佔用
lsof -i :8000
lsof -i :5173

# 強制關閉服務
kill $(lsof -ti :8000)
kill $(lsof -ti :5173)
```
