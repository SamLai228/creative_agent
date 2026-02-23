# EDM Template 圖片目錄

此目錄用於存放 EDM template 圖片檔案。

## 使用方式

1. **放置 Template 圖片**
   - 將您的 EDM template 圖片（如 `edm_template.png`）放在此目錄下
   - 支援的格式：PNG, JPG, JPEG

2. **在生成 EDM 時指定 Template**
   - 在 API 請求的 `requirements` 中，加入 `template` 欄位
   - 值為 template 圖片檔名（例如：`"edm_template.png"`）

## 範例

```json
{
  "template": "edm_template.png",
  "title": "您的標題",
  "description": "您的內文",
  "layout": "centered"
}
```

## 注意事項

- Template 圖片會自動調整為 EDM 畫布大小（預設 1200x800）
- 如果指定的 template 不存在，系統會使用預設背景色
- Template 會作為底圖，文字和素材會疊加在上面
