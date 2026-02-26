import { useRef } from 'react';
import './RegionToolbar.css';

function RegionToolbar({ region, onChange, onDeselect }) {
  const colorInputRef = useRef(null);
  const strokeColorInputRef = useRef(null);
  const shadowColorInputRef = useRef(null);
  const {
    font_size, bold, color, y,
    stroke_width = 0,
    stroke_color = [0, 0, 0],
    shadow_offset = 0,
    shadow_color = [0, 0, 0],
  } = region;

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
      {/* Font size */}
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

      {/* Text color */}
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

      {/* Divider */}
      <span className="tb-sep" />

      {/* Stroke width */}
      <span className="tb-label" title="描邊寬度">邊</span>
      <button
        className="tb-btn"
        title="減少描邊"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ stroke_width: Math.max(0, stroke_width - 1) }))}
      >
        −
      </button>
      <span className="tb-num">{stroke_width}</span>
      <button
        className="tb-btn"
        title="增加描邊"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ stroke_width: Math.min(12, stroke_width + 1) }))}
      >
        +
      </button>

      {/* Stroke color */}
      <div
        className="tb-color-swatch tb-stroke-swatch"
        title="描邊顏色"
        style={{ backgroundColor: rgbToHex(stroke_color) }}
        onPointerDown={stop(() => {})}
        onClick={stop(() => strokeColorInputRef.current?.click())}
      >
        <input
          ref={strokeColorInputRef}
          type="color"
          value={rgbToHex(stroke_color)}
          onChange={(e) => onChange({ stroke_color: hexToRgb(e.target.value) })}
          className="tb-color-input"
        />
      </div>

      {/* Divider */}
      <span className="tb-sep" />

      {/* Shadow offset */}
      <span className="tb-label" title="陰影距離">影</span>
      <button
        className="tb-btn"
        title="減少陰影"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ shadow_offset: Math.max(0, shadow_offset - 1) }))}
      >
        −
      </button>
      <span className="tb-num">{shadow_offset}</span>
      <button
        className="tb-btn"
        title="增加陰影"
        onPointerDown={stop(() => {})}
        onClick={stop(() => onChange({ shadow_offset: Math.min(20, shadow_offset + 1) }))}
      >
        +
      </button>

      {/* Shadow color */}
      <div
        className="tb-color-swatch tb-stroke-swatch"
        title="陰影顏色"
        style={{ backgroundColor: rgbToHex(shadow_color) }}
        onPointerDown={stop(() => {})}
        onClick={stop(() => shadowColorInputRef.current?.click())}
      >
        <input
          ref={shadowColorInputRef}
          type="color"
          value={rgbToHex(shadow_color)}
          onChange={(e) => onChange({ shadow_color: hexToRgb(e.target.value) })}
          className="tb-color-input"
        />
      </div>

      {/* Deselect */}
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
