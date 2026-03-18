import { useState, useRef, useCallback } from 'react';
import html2canvas from 'html2canvas';
import { savePNG } from '../../services/api';
import './EDMPreview.css';

function EDMPreview({ html, onBack, onRegenerate }) {
  const [tab, setTab] = useState('preview'); // 'preview' | 'code'
  const [saving, setSaving] = useState(false);
  const iframeRef = useRef(null);

  const handleSavePNG = useCallback(async () => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    setSaving(true);
    try {
      const target = iframe.contentDocument?.body;
      if (!target) throw new Error('無法存取 iframe 內容');
      const canvas = await html2canvas(target, { useCORS: true, scale: 2 });
      const imageData = canvas.toDataURL('image/png');
      const result = await savePNG(imageData);
      alert(`已儲存至 ${result.saved_path}`);
    } catch (e) {
      alert('儲存失敗：' + e.message);
    } finally {
      setSaving(false);
    }
  }, []);

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

        <button onClick={handleSavePNG} className="btn-secondary" disabled={saving}>
          {saving ? '儲存中…' : '儲存為 PNG'}
        </button>
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
