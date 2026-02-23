"""配置管理模組"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent

# 目錄設定
ASSETS_DIR = BASE_DIR / os.getenv("ASSETS_DIR", "assets")
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
TEMPLATE_DIR = BASE_DIR / os.getenv("TEMPLATE_DIR", "templates")
TEMPLATE_IMAGES_DIR = TEMPLATE_DIR / "images"  # EDM template 圖片目錄
TEMPLATE_CONFIGS_DIR = TEMPLATE_DIR / "configs"  # Template 區域配置目錄
DATA_DIR = BASE_DIR / "data"

# 確保目錄存在
ASSETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR.mkdir(exist_ok=True)
TEMPLATE_IMAGES_DIR.mkdir(exist_ok=True)
TEMPLATE_CONFIGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# API 設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

# 標籤資料庫路徑
TAGS_DB_PATH = DATA_DIR / "material_tags.json"
