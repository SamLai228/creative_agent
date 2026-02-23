#!/bin/bash
# 啟動後端 API 伺服器

source venv/bin/activate
uvicorn api.main:app --reload --port 8000
