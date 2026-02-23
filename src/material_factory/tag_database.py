"""標籤資料庫管理模組"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from src.config import TAGS_DB_PATH


class TagDatabase:
    """管理素材標籤的資料庫"""
    
    def __init__(self, db_path: Path = TAGS_DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """確保資料庫檔案存在"""
        if not self.db_path.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict:
        """載入資料庫"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data: Dict):
        """儲存資料庫"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_tags(self, file_path: str, tags: Dict) -> bool:
        """
        新增或更新素材標籤
        
        Args:
            file_path: 素材檔案路徑（作為唯一識別）
            tags: 標籤字典
            
        Returns:
            是否成功
        """
        data = self._load_data()
        data[file_path] = {
            **tags,
            "updated_at": self._get_timestamp()
        }
        self._save_data(data)
        return True
    
    def get_tags(self, file_path: str) -> Optional[Dict]:
        """取得指定素材的標籤"""
        data = self._load_data()
        return data.get(file_path)
    
    def get_all_tags(self) -> Dict:
        """取得所有標籤"""
        return self._load_data()
    
    def search_by_tags(
        self,
        category: Optional[str] = None,
        style: Optional[List[str]] = None,
        scenario: Optional[List[str]] = None,
        color_scheme: Optional[str] = None,
        mood: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        根據標籤搜尋素材
        
        Args:
            category: 類型
            style: 風格列表
            scenario: 情境列表
            color_scheme: 色系
            mood: 氛圍列表
            keywords: 關鍵字列表
            
        Returns:
            符合條件的素材列表
        """
        data = self._load_data()
        results = []
        
        for file_path, tags in data.items():
            match = True
            
            # 檢查類型
            if category and tags.get("category") != category:
                match = False
            
            # 檢查風格（至少符合一個）
            if style and not any(s in tags.get("style", []) for s in style):
                match = False
            
            # 檢查情境（至少符合一個）
            if scenario and not any(s in tags.get("scenario", []) for s in scenario):
                match = False
            
            # 檢查色系
            if color_scheme and tags.get("color_scheme") != color_scheme:
                match = False
            
            # 檢查氛圍（至少符合一個）
            if mood and not any(m in tags.get("mood", []) for m in mood):
                match = False
            
            # 檢查關鍵字（至少符合一個）
            if keywords:
                tag_keywords = [k.lower() for k in tags.get("keywords", [])]
                search_keywords = [k.lower() for k in keywords]
                if not any(k in tag_keywords for k in search_keywords):
                    match = False
            
            if match:
                results.append({
                    "file_path": file_path,
                    **tags
                })
        
        return results
    
    def delete_tags(self, file_path: str) -> bool:
        """刪除指定素材的標籤"""
        data = self._load_data()
        if file_path in data:
            del data[file_path]
            self._save_data(data)
            return True
        return False
    
    def _get_timestamp(self) -> str:
        """取得時間戳記"""
        from datetime import datetime
        return datetime.now().isoformat()
