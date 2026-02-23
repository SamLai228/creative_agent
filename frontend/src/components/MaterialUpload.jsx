/** 上傳元件 */
import { useState, useRef } from 'react';
import { uploadMaterial } from '../services/api';
import TaggingProgress from './TaggingProgress';
import './MaterialUpload.css';

function MaterialUpload({ onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    const imageFiles = droppedFiles.filter(file => 
      file.type.startsWith('image/')
    );
    setFiles(imageFiles);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const progress = {};

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        progress[file.name] = { status: 'uploading', filePath: null };
        setUploadProgress({ ...progress });

        try {
          // 上傳檔案
          const uploadResult = await uploadMaterial(file);
          progress[file.name] = {
            status: 'uploaded',
            filePath: uploadResult.file_path,
          };
          setUploadProgress({ ...progress });

          // 自動開始貼標（TaggingProgress 元件會處理）
          progress[file.name].status = 'tagging';
          setUploadProgress({ ...progress });
          
          // 注意：實際的貼標會在 TaggingProgress 元件中執行
          // 這裡只是標記狀態，讓 TaggingProgress 元件開始工作
        } catch (error) {
          console.error(`處理 ${file.name} 失敗:`, error);
          progress[file.name] = {
            status: 'error',
            error: error.response?.data?.detail || error.message,
          };
          setUploadProgress({ ...progress });
        }
      }
    } finally {
      setUploading(false);
      // 清空檔案列表
      setTimeout(() => {
        setFiles([]);
        setUploadProgress({});
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 2000);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setUploadProgress({});
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="material-upload">
      <h2>上傳素材</h2>
      
      <div
        className="upload-area"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="upload-content">
          <svg
            className="upload-icon"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p className="upload-text">
            拖放圖片到這裡，或
            <button
              className="upload-button-link"
              onClick={() => fileInputRef.current?.click()}
            >
              點擊選擇檔案
            </button>
          </p>
          <p className="upload-hint">
            支援 JPG, PNG, GIF, WebP, BMP 格式
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="file-input"
        />
      </div>

      {files.length > 0 && (
        <div className="upload-files">
          <div className="files-header">
            <h3>已選擇的檔案 ({files.length})</h3>
            <button onClick={handleClear} className="clear-button">
              清空
            </button>
          </div>
          <ul className="files-list">
            {files.map((file, index) => (
              <li key={index} className="file-item">
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </li>
            ))}
          </ul>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="upload-submit-button"
          >
            {uploading ? '處理中...' : '上傳並貼標'}
          </button>
        </div>
      )}

      {Object.keys(uploadProgress).length > 0 && (
        <div className="upload-progress-list">
          {Object.entries(uploadProgress).map(([fileName, progress]) => (
            <TaggingProgress
              key={fileName}
              fileName={fileName}
              filePath={progress.filePath}
              onComplete={() => {
                progress.status = 'completed';
                setUploadProgress({ ...uploadProgress });
                if (onUploadComplete) {
                  onUploadComplete({ file_path: progress.filePath });
                }
              }}
              onError={(error) => {
                progress.status = 'error';
                progress.error = error.response?.data?.detail || error.message;
                setUploadProgress({ ...uploadProgress });
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default MaterialUpload;
