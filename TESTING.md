# EDM 生成功能測試指南

## 測試方式

### 方式一：使用 Python 測試腳本（推薦）

#### 1. 直接測試生成功能

```bash
# 確保虛擬環境已啟動
source venv/bin/activate

# 執行測試腳本
python test_generation.py
```

這個腳本會執行以下測試案例：
- ✓ 取得可用版面配置
- ✓ 素材預覽功能
- ✓ 測試案例 1: 春季特賣活動
- ✓ 測試案例 2: 家庭活動宣傳
- ✓ 測試案例 3: 商業促銷活動
- ✓ 測試案例 4: 旅遊促銷
- ✓ 測試案例 5: PDF 格式輸出

#### 2. 測試 API 端點

```bash
# 確保後端服務正在運行（在另一個終端機）
uvicorn api.main:app --reload --port 8000

# 執行 API 測試腳本
python test_generation_api.py
```

### 方式二：使用 API 文檔（Swagger UI）

1. 啟動後端服務：
```bash
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

2. 打開瀏覽器訪問：`http://localhost:8000/docs`

3. 在 Swagger UI 中測試以下端點：
   - `GET /api/generation/layouts` - 取得可用版面配置
   - `GET /api/generation/preview-materials` - 預覽素材
   - `POST /api/generation/generate` - 生成 EDM

### 方式三：使用 curl 命令

#### 取得可用版面配置
```bash
curl http://localhost:8000/api/generation/layouts
```

#### 預覽素材
```bash
curl "http://localhost:8000/api/generation/preview-materials?category=人物&mood=歡樂"
```

#### 生成 EDM
```bash
curl -X POST "http://localhost:8000/api/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "春季特賣",
    "description": "全館商品 8 折優惠",
    "style": ["現代", "簡約"],
    "mood": ["活力", "歡樂"],
    "layout": "centered",
    "output_format": "png"
  }'
```

## 測試案例說明

### 測試案例 1: 春季特賣活動
- **目的**: 測試基本生成功能
- **需求**: 現代簡約風格，活力歡樂氛圍
- **版面**: 置中版面
- **預期**: 生成包含標題、描述和素材的 EDM

### 測試案例 2: 家庭活動宣傳
- **目的**: 測試人物素材選擇
- **需求**: 家庭情境，可愛風格
- **版面**: 左對齊版面
- **預期**: 選擇適合的人物素材

### 測試案例 3: 商業促銷活動
- **目的**: 測試專業風格生成
- **需求**: 專業氛圍，中性色系
- **版面**: 英雄版面
- **預期**: 生成專業風格的 EDM

### 測試案例 4: 旅遊促銷
- **目的**: 測試情境搜尋
- **需求**: 旅行情境，活力氛圍
- **版面**: 網格版面
- **預期**: 選擇旅行相關素材

### 測試案例 5: PDF 格式輸出
- **目的**: 測試 PDF 輸出功能
- **需求**: 基本需求
- **格式**: PDF
- **預期**: 生成 PDF 檔案

## 檢查生成結果

生成的 EDM 檔案會儲存在：
```
output/edm/
```

檔案命名格式：
- PNG: `edm_YYYYMMDD_HHMMSS.png`
- PDF: `edm_YYYYMMDD_HHMMSS.pdf`

## 常見問題

### 1. 找不到素材
**問題**: 測試時提示找不到符合條件的素材

**解決方案**:
- 確保 `assets/` 目錄中有已貼標的素材
- 執行 `python cli.py tag --dir assets/` 為素材貼標
- 檢查 `data/material_tags.json` 是否有資料

### 2. 圖片載入失敗
**問題**: 生成時提示圖片不存在

**解決方案**:
- 檢查素材路徑是否正確
- 確認 `assets/` 目錄中的圖片檔案存在
- 檢查 `material_tags.json` 中的 `file_path` 是否正確

### 3. API 連接失敗
**問題**: API 測試無法連接

**解決方案**:
- 確認後端服務正在運行：`uvicorn api.main:app --reload --port 8000`
- 檢查端口是否被占用
- 確認 CORS 設定正確

### 4. 生成結果不理想
**問題**: 生成的 EDM 版面或素材選擇不理想

**解決方案**:
- 調整需求參數（style, mood, color_scheme 等）
- 嘗試不同的版面配置
- 確保有足夠的已貼標素材可供選擇

## 進階測試

### 自訂測試案例

你可以修改 `test_generation.py` 來創建自己的測試案例：

```python
def test_custom_case():
    generator = EDMGenerator()
    
    requirements = {
        "title": "你的標題",
        "description": "你的描述",
        "style": ["你的風格"],
        "mood": ["你的氛圍"],
        "layout": "centered"
    }
    
    result = generator.generate(requirements)
    print(f"生成成功: {result['output_path']}")
```

### 批次測試

可以創建多個測試案例並批次執行，比較不同參數組合的效果。

## 測試檢查清單

- [ ] 後端服務正常運行
- [ ] 素材已貼標（至少 3-5 個素材）
- [ ] 輸出目錄可寫入
- [ ] 所有測試案例都能執行
- [ ] 生成的檔案可以正常打開
- [ ] 版面配置正確套用
- [ ] 素材選擇符合需求
