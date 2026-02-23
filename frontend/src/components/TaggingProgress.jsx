/** 貼標進度展示元件 */
import { useState, useEffect } from 'react';
import { tagMaterial } from '../services/api';
import './TaggingProgress.css';

function TaggingProgress({ filePath, fileName, onComplete, onError }) {
  const [status, setStatus] = useState('analyzing');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('準備中...');

  useEffect(() => {
    if (filePath) {
      startTagging();
    }
  }, [filePath]);

  const startTagging = async () => {
    try {
      setStatus('analyzing');
      setMessage('正在分析圖片...');
      setProgress(20);
      
      // 短暫延遲以顯示進度
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setStatus('tagging');
      setMessage('正在呼叫 LLM 生成標籤...');
      setProgress(50);
      
      // 實際呼叫 API
      await tagMaterial(filePath, false);
      
      setStatus('saving');
      setMessage('正在儲存標籤...');
      setProgress(90);
      
      // 短暫延遲
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setStatus('completed');
      setMessage('貼標完成！');
      setProgress(100);
      
      if (onComplete) {
        setTimeout(() => {
          onComplete();
        }, 500);
      }
    } catch (error) {
      setStatus('error');
      setMessage('貼標失敗: ' + (error.response?.data?.detail || error.message || '未知錯誤'));
      if (onError) {
        onError(error);
      }
    }
  };

  return (
    <div className="tagging-progress">
      <div className="progress-header">
        <h3>{fileName}</h3>
        <span className={`status-badge status-${status}`}>
          {status === 'uploading' && '上傳中'}
          {status === 'analyzing' && '分析中'}
          {status === 'tagging' && '貼標中'}
          {status === 'saving' && '儲存中'}
          {status === 'completed' && '完成'}
          {status === 'error' && '錯誤'}
        </span>
      </div>
      
      <div className="progress-bar-container">
        <div 
          className={`progress-bar progress-${status}`}
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <p className="progress-message">{message}</p>
    </div>
  );
}

export default TaggingProgress;
