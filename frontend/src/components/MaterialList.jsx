/** 素材列表元件 */
import { useState, useEffect } from 'react';
import { getAllMaterials, searchMaterials, tagMaterial, deleteMaterial } from '../services/api';
import MaterialCard from './MaterialCard';
import SearchBar from './SearchBar';
import './MaterialList.css';

function MaterialList() {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchParams, setSearchParams] = useState({});

  useEffect(() => {
    loadMaterials();
  }, []);

  const loadMaterials = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllMaterials();
      // 確保 data 是陣列
      if (Array.isArray(data)) {
        setMaterials(data);
      } else {
        console.warn('API 返回的資料格式不正確:', data);
        setMaterials([]);
        setError('資料格式錯誤，請檢查後端服務');
      }
    } catch (err) {
      console.error('載入素材失敗:', err);
      const errorMessage = err.message || '載入素材失敗';
      setError(errorMessage);
      setMaterials([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (params) => {
    setSearchParams(params);
    try {
      setLoading(true);
      setError(null);
      
      if (Object.keys(params).length === 0) {
        await loadMaterials();
      } else {
        const results = await searchMaterials(params);
        setMaterials(results);
      }
    } catch (err) {
      console.error('搜尋失敗:', err);
      setError('搜尋失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleTagMaterial = async (material) => {
    try {
      await tagMaterial(material.file_path, false);
      // 重新載入該素材的標籤
      await loadMaterials();
    } catch (err) {
      console.error('貼標失敗:', err);
      alert('貼標失敗: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteMaterial = async (material) => {
    try {
      const result = await deleteMaterial(material.file_path);
      
      // 立即從列表中移除，提供更好的使用者體驗
      setMaterials(prevMaterials => 
        prevMaterials.filter(m => {
          // 比對多種可能的路徑格式
          const currentPath = m.file_path;
          const targetPath = material.file_path;
          
          // 直接比對
          if (currentPath === targetPath) return false;
          
          // 比對檔案名稱
          const currentName = currentPath.split('/').pop() || currentPath;
          const targetName = targetPath.split('/').pop() || targetPath;
          if (currentName === targetName) return false;
          
          return true;
        })
      );
      
      // 強制重新載入列表以確保資料庫和前端同步
      // 使用 setTimeout 確保狀態更新後再重新載入
      setTimeout(async () => {
        if (Object.keys(searchParams).length > 0) {
          await handleSearch(searchParams);
        } else {
          await loadMaterials();
        }
      }, 100);
      
    } catch (err) {
      console.error('刪除失敗:', err);
      alert('刪除失敗: ' + (err.response?.data?.detail || err.message));
      // 如果刪除失敗，重新載入列表以確保資料正確
      await loadMaterials();
    }
  };

  if (loading && materials.length === 0) {
    return (
      <div className="material-list">
        <div className="loading">載入中...</div>
      </div>
    );
  }

  return (
    <div className="material-list">
      <SearchBar onSearch={handleSearch} />
      
      {error && (
        <div className="error-message">
          {error}
          <button onClick={loadMaterials}>重試</button>
        </div>
      )}

      {materials.length === 0 ? (
        <div className="empty-state">
          <p>目前沒有已貼標的素材</p>
          <p className="empty-hint">請先上傳素材並進行貼標</p>
        </div>
      ) : (
        <div className="materials-grid">
          {materials.map((material, index) => (
            <MaterialCard
              key={material.file_path || index}
              material={material}
              onRefresh={handleTagMaterial}
              onDelete={handleDeleteMaterial}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default MaterialList;
