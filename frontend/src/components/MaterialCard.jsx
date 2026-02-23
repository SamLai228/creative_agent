/** 素材卡片元件 - 展示圖片和標籤 */
import { useState, useEffect } from 'react';
import { getMaterialImageUrl, getMaterialTags } from '../services/api';
import TagDisplay from './TagDisplay';
import './MaterialCard.css';

function MaterialCard({ material, onRefresh, onDelete }) {
  const [imageUrl, setImageUrl] = useState('');
  const [tags, setTags] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (material) {
      // 設定圖片 URL
      const url = getMaterialImageUrl(material.file_path);
      setImageUrl(url);
      
      // 載入標籤資訊
      loadTags();
    }
  }, [material]);

  const loadTags = async () => {
    try {
      setLoading(true);
      setError(null);
      const tagsData = await getMaterialTags(material.file_path);
      setTags(tagsData);
    } catch (err) {
      console.error('載入標籤失敗:', err);
      setError('載入標籤失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleImageError = () => {
    setError('圖片載入失敗');
  };

  return (
    <div className="material-card">
      <div className="material-card-content">
        <div className="material-image-container">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={material.file_name}
              onError={handleImageError}
              className="material-image"
            />
          ) : (
            <div className="material-image-placeholder">載入中...</div>
          )}
          {error && <div className="material-error">{error}</div>}
        </div>
        
        <div className="material-info">
          <div className="material-header">
            <h2 className="material-title">{material.file_name}</h2>
            <div className="material-actions">
              <button 
                onClick={loadTags} 
                className="refresh-button"
                disabled={loading}
              >
                {loading ? '載入中...' : '重新載入標籤'}
              </button>
              {onDelete && (
                <button 
                  onClick={() => {
                    if (window.confirm(`確定要刪除「${material.file_name}」嗎？此操作無法復原。`)) {
                      onDelete(material);
                    }
                  }}
                  className="delete-button"
                >
                  刪除
                </button>
              )}
            </div>
          </div>
          
          {loading && !tags ? (
            <div className="loading">載入標籤中...</div>
          ) : tags ? (
            <TagDisplay tags={tags} />
          ) : (
            <div className="no-tags">
              <p>此素材尚未貼標</p>
              <button 
                onClick={() => onRefresh && onRefresh(material)}
                className="tag-button"
              >
                立即貼標
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MaterialCard;
