import { useState, useEffect, useRef, useCallback } from 'react';
import RegionOverlay from './RegionOverlay';
import { renderWithCopy } from '../../services/api';
import './EDMCanvas.css';

const ZOOM_STEP = 0.1;
const ZOOM_MIN = 0.1;
const ZOOM_MAX = 4.0;

function EDMCanvas({ templateName, regions, onRegionsChange, onExport, onBack }) {
  const containerRef = useRef(null);
  const [fitScale, setFitScale] = useState(1);   // auto-fit value, for Fit button
  const [scale, setScale] = useState(1);          // actual display scale, starts at 100%
  const [canvasSize, setCanvasSize] = useState([656, 1616]);
  const [selectedId, setSelectedId] = useState(null);
  const [exporting, setExporting] = useState(false);

  // Load template image to get natural dimensions
  useEffect(() => {
    if (!templateName) return;
    const img = new Image();
    img.onload = () => setCanvasSize([img.naturalWidth, img.naturalHeight]);
    img.src = `/templates/${templateName}`;
  }, [templateName]);

  // Keep fitScale updated for the Fit button; don't touch scale
  useEffect(() => {
    const updateFitScale = () => {
      if (!containerRef.current) return;
      const { clientWidth, clientHeight } = containerRef.current;
      if (!clientWidth || !clientHeight) return;
      setFitScale(Math.min(
        (clientHeight - 32) / canvasSize[1],
        (clientWidth - 32) / canvasSize[0],
        1
      ));
    };

    updateFitScale();
    const observer = new ResizeObserver(updateFitScale);
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [canvasSize]);

  const zoomIn  = () => setScale((s) => Math.min(ZOOM_MAX, parseFloat((s + ZOOM_STEP).toFixed(2))));
  const zoomOut = () => setScale((s) => Math.max(ZOOM_MIN, parseFloat((s - ZOOM_STEP).toFixed(2))));
  const zoomFit = () => setScale(parseFloat(fitScale.toFixed(2)));

  const handleRegionChange = useCallback(
    (id, changes) => {
      onRegionsChange((prev) => prev.map((r) => (r.id === id ? { ...r, ...changes } : r)));
    },
    [onRegionsChange]
  );

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = await renderWithCopy({ template_name: templateName, regions });
      onExport(result.url);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || '匯出失敗';
      alert('匯出失敗：' + detail);
    } finally {
      setExporting(false);
    }
  };

  const scaledWidth = canvasSize[0] * scale;
  const scaledHeight = canvasSize[1] * scale;

  return (
    <div className="edm-canvas-wrapper">
      {/* Top toolbar */}
      <div className="canvas-topbar">
        <button onClick={onBack} className="topbar-btn back-btn">
          ← 返回
        </button>

        <span className="topbar-hint">單擊選取・雙擊輸入・拖移位置</span>

        {/* Zoom controls */}
        <div className="zoom-controls">
          <button className="zoom-btn" onClick={zoomOut} disabled={scale <= ZOOM_MIN} title="縮小">−</button>
          <span className="zoom-label">{Math.round(scale * 100)}%</span>
          <button className="zoom-btn" onClick={zoomIn}  disabled={scale >= ZOOM_MAX} title="放大">+</button>
          <button className="zoom-btn zoom-fit-btn" onClick={zoomFit} title="自動縮放">Fit</button>
        </div>

        <button onClick={handleExport} disabled={exporting} className="topbar-btn export-btn">
          {exporting ? (
            <>
              <span className="spinner-sm" /> 渲染中...
            </>
          ) : (
            '匯出 PNG'
          )}
        </button>
      </div>

      {/* Canvas area */}
      <div className="canvas-area">
        <div
          className="canvas-scroll-container"
          ref={containerRef}
          onClick={() => setSelectedId(null)}
        >
          {/* Outer wrapper sized to scaled dimensions so layout doesn't shift */}
          <div
            className="canvas-scaled-outer"
            style={{ width: scaledWidth, height: scaledHeight }}
          >
            {/* Inner div at original size, scaled via CSS transform */}
            <div
              className="canvas-inner"
              style={{
                width: canvasSize[0],
                height: canvasSize[1],
                transform: `scale(${scale})`,
                transformOrigin: 'top left',
              }}
            >
              <img
                src={`/templates/${templateName}`}
                alt="EDM Template"
                className="canvas-template-img"
                draggable={false}
              />
              {regions.map((region) => (
                <RegionOverlay
                  key={region.id}
                  region={region}
                  scale={scale}
                  isSelected={selectedId === region.id}
                  onSelect={() => setSelectedId(region.id)}
                  onDeselect={() => setSelectedId(null)}
                  onChange={(changes) => handleRegionChange(region.id, changes)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Side panel: region list */}
        <div className="region-list-panel">
          <h4 className="panel-title">文字區域</h4>
          <div className="region-list">
            {regions.map((r) => (
              <div
                key={r.id}
                className={`region-list-item ${selectedId === r.id ? 'active' : ''}`}
                onClick={() => setSelectedId(r.id)}
              >
                <span className="region-list-id">{r.id}</span>
                <span className="region-list-text">{r.text || '(空白)'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EDMCanvas;
