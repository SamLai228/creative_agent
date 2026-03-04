import { useState, useRef, useCallback } from 'react';
import './EDMPreview.css';

function EDMPreview({ html, onBack, onRegenerate }) {
  const [tab, setTab] = useState('preview'); // 'preview' | 'code'
  const iframeRef = useRef(null);

  // 讓 iframe 高度自動貼合內容，避免跳版
  const handleIframeLoad = useCallback(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    try {
      const h = iframe.contentDocument?.documentElement?.scrollHeight;
      if (h && h > 0) iframe.style.height = h + 'px';
    } catch {
      // cross-origin 時忽略
    }
  }, []);

  return (
    <div className="edm-preview">
      <div className="preview-toolbar">
        <button onClick={onBack} className="btn-secondary">← 返回</button>

        <div className="preview-tabs">
          <button
            className={`tab-btn ${tab === 'preview' ? 'active' : ''}`}
            onClick={() => setTab('preview')}
          >
            預覽
          </button>
          <button
            className={`tab-btn ${tab === 'code' ? 'active' : ''}`}
            onClick={() => setTab('code')}
          >
            HTML 程式碼
          </button>
        </div>

        <button onClick={onRegenerate} className="btn-ghost">重新生成</button>
      </div>

      {tab === 'preview' && (
        <div className="preview-frame-wrap">
          <iframe
            ref={iframeRef}
            key={html}
            srcDoc={html}
            title="EDM Preview"
            className="preview-frame"
            sandbox="allow-same-origin"
            onLoad={handleIframeLoad}
          />
        </div>
      )}

      {tab === 'code' && (
        <div className="code-wrap">
          <div className="code-actions">
            <button
              className="btn-copy"
              onClick={() => navigator.clipboard.writeText(html)}
            >
              複製
            </button>
          </div>
          <pre className="code-block"><code>{html}</code></pre>
        </div>
      )}
    </div>
  );
}

export default EDMPreview;
