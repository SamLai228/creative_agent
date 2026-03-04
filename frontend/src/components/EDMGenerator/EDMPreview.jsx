import './EDMPreview.css';

function EDMPreview({ html, onBack, onRegenerate }) {
  return (
    <div className="edm-preview">
      <div className="preview-toolbar">
        <button onClick={onBack} className="btn-secondary">← 返回</button>
        <span className="preview-title">EDM 預覽</span>
        <button onClick={onRegenerate} className="btn-ghost">重新生成</button>
      </div>
      <div className="preview-frame-wrap">
        <iframe
          srcDoc={html}
          title="EDM Preview"
          className="preview-frame"
          sandbox="allow-same-origin"
        />
      </div>
    </div>
  );
}

export default EDMPreview;
