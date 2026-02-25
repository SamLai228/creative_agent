import { useRef } from 'react';
import './RegionToolbar.css';

function RegionToolbar({ region, onChange, onDeselect }) {
  const colorInputRef = useRef(null);
  const { font_size, bold, color, y } = region;

  // Show toolbar below the region if near the top of the canvas
  const showBelow = y < 60;

  const rgbToHex = ([r, g, b]) =>
    '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('');

  const hexToRgb = (hex) => [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];

  const stop = (fn) => (e) => {
    e.stopPropagation();
    fn(e);
  };

  return (
    <div className={`region-toolbar ${showBelow ? 'toolbar-below' : 'toolbar-above'}`}>
      <button
        className="tb-btn"
        title="縮小字體 (A-)"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ font_size: Math.max(8, font_size - 2) }))}
      >
        A-
      </button>

      <button
        className="tb-btn"
        title="放大字體 (A+)"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ font_size: Math.min(100, font_size + 2) }))}
      >
        A+
      </button>

      <button
        className={`tb-btn tb-bold ${bold ? 'active' : ''}`}
        title="粗體"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ bold: !bold }))}
      >
        <b>B</b>
      </button>

      {/* Color swatch */}
      <div
        className="tb-color-swatch"
        title="文字顏色"
        style={{ backgroundColor: rgbToHex(color) }}
        onPointerDown={stop(() => {})}
        onClick={stop(() => colorInputRef.current?.click())}
      >
        <input
          ref={colorInputRef}
          type="color"
          value={rgbToHex(color)}
          onChange={(e) => onChange({ color: hexToRgb(e.target.value) })}
          className="tb-color-input"
        />
      </div>

      <button
        className="tb-btn tb-close"
        title="取消選取"
        onPointerDown={stop(() => {})}
        onClick={stop(onDeselect)}
      >
        ✕
      </button>
    </div>
  );
}

export default RegionToolbar;
