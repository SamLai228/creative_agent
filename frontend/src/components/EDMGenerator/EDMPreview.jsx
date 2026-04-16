import { useState, useRef, useCallback, useEffect } from 'react';
import html2canvas from 'html2canvas';
import { savePNG } from '../../services/api';
import './EDMPreview.css';

function generateTitleCss(style) {
  const { color, bold, strokeEnabled, strokeColor, strokeWidth } = style;
  const strokeCss = strokeEnabled
    ? `-webkit-text-stroke: ${strokeWidth}px ${strokeColor}; paint-order: stroke fill;`
    : '-webkit-text-stroke: 0;';
  return `
        .edm-title { color: ${color}; font-weight: ${bold ? 'bold' : 'normal'}; ${strokeCss} }
        .edm-title span { color: ${color}; font-weight: ${bold ? 'bold' : 'normal'}; ${strokeCss} }`;
}

function applyTitleStyle(html, style) {
  return html.replace(
    /<style id="edm-title-style">[\s\S]*?<\/style>/,
    `<style id="edm-title-style">${generateTitleCss(style)}</style>`
  );
}

function injectEditing(html) {
  const cleaned = html.replace(/<script id="edm-edit-script">[\s\S]*?<\/script>/g, '');
  const script = `<script id="edm-edit-script">(function(){
    var sel = 'h1, p, h3, a.main-btn, a.product-btn, a.consult-btn';
    document.querySelectorAll(sel).forEach(function(el){
      if(el.querySelector('img')) return;
      el.contentEditable='true'; el.style.cursor='text';
    });
    document.addEventListener('focusin', function(e){
      if(e.target.contentEditable==='true'){
        e.target.style.outline='2px dashed #52b69a';
        e.target.style.outlineOffset='2px';
      }
    });
    document.addEventListener('focusout', function(e){
      if(e.target.contentEditable!=='true') return;
      e.target.style.outline=''; e.target.style.outlineOffset='';
      var clone = document.documentElement.cloneNode(true);
      clone.querySelectorAll('[contenteditable]').forEach(function(c){
        c.removeAttribute('contenteditable'); c.style.cursor=''; c.style.outline=''; c.style.outlineOffset='';
      });
      var s = clone.querySelector('#edm-edit-script'); if(s) s.remove();
      window.parent.postMessage({type:'edmUpdate',html:'<!DOCTYPE html>'+clone.outerHTML},'*');
    }, true);
    document.querySelectorAll('[contenteditable]').forEach(function(el){
      el.addEventListener('mouseenter', function(){ if(document.activeElement!==el) el.style.outline='1px dashed rgba(82,182,154,0.4)'; });
      el.addEventListener('mouseleave', function(){ if(document.activeElement!==el) el.style.outline=''; });
    });
  })();<\/script>`;
  return cleaned.replace('</body>', script + '\n</body>');
}

function EDMPreview({ html, onBack, onRegenerate }) {
  const [tab, setTab] = useState('preview'); // 'preview' | 'code'
  const [saving, setSaving] = useState(false);
  const iframeRef = useRef(null);

  const [titleStyle, setTitleStyle] = useState({
    color: '#000000',
    bold: true,
    strokeEnabled: true,
    strokeColor: '#ffffff',
    strokeWidth: 3,
  });

  // editedHtml: loaded into iframe srcDoc (includes editing script)
  // exportHtml: clean HTML for copy / code tab (no contenteditable, no edit script)
  const [editedHtml, setEditedHtml] = useState(() => injectEditing(html));
  const [exportHtml, setExportHtml] = useState(html);

  // When html prop changes (new generation) → full reset
  useEffect(() => {
    const styled = applyTitleStyle(html, titleStyle);
    setEditedHtml(injectEditing(styled));
    setExportHtml(styled);
  }, [html]); // intentionally omit titleStyle — handled separately below

  // Receive clean HTML back from iframe after each text edit
  useEffect(() => {
    const handler = (e) => {
      if (e.data?.type === 'edmUpdate') setExportHtml(e.data.html);
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, []);

  // titleStyle changes → update iframe DOM directly (no srcDoc reload)
  useEffect(() => {
    const iframe = iframeRef.current;
    const css = generateTitleCss(titleStyle);
    const styleEl = iframe?.contentDocument?.getElementById('edm-title-style');
    if (styleEl) styleEl.textContent = css;
    setExportHtml(prev => applyTitleStyle(prev, titleStyle));
  }, [titleStyle]);

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

  // Let iframe height fit content after load
  const handleIframeLoad = useCallback(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    try {
      const h = iframe.contentDocument?.documentElement?.scrollHeight;
      if (h && h > 0) iframe.style.height = h + 'px';
    } catch {
      // cross-origin — ignore
    }
  }, []);

  const updateStyle = (key, value) =>
    setTitleStyle(prev => ({ ...prev, [key]: value }));

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
        <>
          <div className="title-style-panel">
            <span className="panel-hint">點擊文字可直接編輯</span>
            <label className="style-field">
              <span>字體顏色</span>
              <input
                type="color"
                value={titleStyle.color}
                onChange={e => updateStyle('color', e.target.value)}
              />
            </label>
            <label className="style-field">
              <span>加粗</span>
              <input
                type="checkbox"
                checked={titleStyle.bold}
                onChange={e => updateStyle('bold', e.target.checked)}
              />
            </label>
            <label className="style-field">
              <span>文字邊框</span>
              <input
                type="checkbox"
                checked={titleStyle.strokeEnabled}
                onChange={e => updateStyle('strokeEnabled', e.target.checked)}
              />
            </label>
            {titleStyle.strokeEnabled && (
              <>
                <label className="style-field">
                  <span>邊框顏色</span>
                  <input
                    type="color"
                    value={titleStyle.strokeColor}
                    onChange={e => updateStyle('strokeColor', e.target.value)}
                  />
                </label>
                <label className="style-field">
                  <span>寬度 {titleStyle.strokeWidth}px</span>
                  <input
                    type="range"
                    min="1"
                    max="6"
                    value={titleStyle.strokeWidth}
                    onChange={e => updateStyle('strokeWidth', Number(e.target.value))}
                  />
                </label>
              </>
            )}
          </div>
          <div className="preview-frame-wrap">
            <iframe
              ref={iframeRef}
              key={html}
              srcDoc={editedHtml}
              title="EDM Preview"
              className="preview-frame"
              sandbox="allow-scripts allow-same-origin"
              onLoad={handleIframeLoad}
            />
          </div>
        </>
      )}

      {tab === 'code' && (
        <div className="code-wrap">
          <div className="code-actions">
            <button
              className="btn-copy"
              onClick={() => navigator.clipboard.writeText(exportHtml)}
            >
              複製
            </button>
          </div>
          <pre className="code-block"><code>{exportHtml}</code></pre>
        </div>
      )}
    </div>
  );
}

export default EDMPreview;
