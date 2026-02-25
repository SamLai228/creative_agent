import { useState } from 'react';
import MaterialUpload from './components/MaterialUpload';
import MaterialList from './components/MaterialList';
import EDMGenerator from './components/EDMGenerator/EDMGenerator';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = () => {
    // 上傳完成後，切換到列表頁面並刷新
    setActiveTab('list');
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎨 素材工廠</h1>
        <p className="subtitle">行銷 EDM 素材貼標系統</p>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'upload' ? 'active' : ''}
          onClick={() => setActiveTab('upload')}
        >
          上傳素材
        </button>
        <button
          className={activeTab === 'list' ? 'active' : ''}
          onClick={() => setActiveTab('list')}
        >
          素材列表
        </button>
        <button
          className={activeTab === 'generate' ? 'active' : ''}
          onClick={() => setActiveTab('generate')}
        >
          EDM 生成
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'upload' && (
          <MaterialUpload onUploadComplete={handleUploadComplete} />
        )}
        {activeTab === 'list' && (
          <MaterialList key={refreshKey} />
        )}
        {activeTab === 'generate' && (
          <EDMGenerator />
        )}
      </main>

      <footer className="app-footer">
        <p>© 2026 素材工廠 - 使用 LLM 自動貼標</p>
      </footer>
    </div>
  );
}

export default App;
