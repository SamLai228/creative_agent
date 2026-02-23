"""FastAPI 應用程式入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.config import ASSETS_DIR
from api.routes import materials, generation

app = FastAPI(
    title="EDM 素材工廠 API",
    description="行銷 EDM 素材貼標系統 API",
    version="1.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite 和 CRA 預設端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(materials.router)
app.include_router(generation.router)

# 靜態檔案服務（用於提供圖片）
assets_path = Path(ASSETS_DIR)
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "EDM 素材工廠 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "ok"}
