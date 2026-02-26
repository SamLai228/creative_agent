import { useRef, useEffect, useState } from 'react';
import RegionToolbar from './RegionToolbar';
import './RegionOverlay.css';

function RegionOverlay({ region, scale, isSelected, onSelect, onDeselect, onChange }) {
  const {
    text, x, y, width, height, font_size, bold, color,
    stroke_width = 0,
    stroke_color = [0, 0, 0],
    shadow_offset = 0,
    shadow_color = [0, 0, 0],
  } = region;
  const contentRef = useRef(null);
  const dragRef = useRef(null);
  const [isEditing, setIsEditing] = useState(false);

  // Sync text to DOM when not editing
  useEffect(() => {
    const el = contentRef.current;
    if (el && !isEditing) {
      el.innerText = text;
    }
  }, [text, isEditing]);

  // When deselected, exit editing mode
  useEffect(() => {
    if (!isSelected) {
      setIsEditing(false);
    }
  }, [isSelected]);

  const handlePointerDown = (e) => {
    if (isEditing) return; // Don't start drag while editing
    e.preventDefault();
    e.stopPropagation();
    onSelect();

    dragRef.current = {
      mouseX: e.clientX,
      mouseY: e.clientY,
      rx: x,
      ry: y,
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e) => {
    if (!dragRef.current) return;
    const dx = (e.clientX - dragRef.current.mouseX) / scale;
    const dy = (e.clientY - dragRef.current.mouseY) / scale;
    onChange({
      x: dragRef.current.rx + dx,
      y: dragRef.current.ry + dy,
    });
  };

  const handlePointerUp = () => {
    dragRef.current = null;
  };

  const handleDoubleClick = (e) => {
    e.stopPropagation();
    setIsEditing(true);
    const el = contentRef.current;
    if (el) {
      el.focus();
      // Place cursor at end
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(el);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
    }
  };

  const handleBlur = (e) => {
    const newText = e.currentTarget.innerText;
    setIsEditing(false);
    onChange({ text: newText });
  };

  const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;

  // Build CSS stroke preview via text-shadow (widely supported, avoids webkit-only quirks)
  const buildStrokeShadow = (sw, sc) => {
    if (!sw || sw <= 0) return null;
    const c = `rgb(${sc[0]}, ${sc[1]}, ${sc[2]})`;
    const shadows = [];
    for (let dx = -sw; dx <= sw; dx++) {
      for (let dy = -sw; dy <= sw; dy++) {
        if (dx !== 0 || dy !== 0) shadows.push(`${dx}px ${dy}px 0 ${c}`);
      }
    }
    return shadows.join(', ');
  };

  const strokeShadow = buildStrokeShadow(stroke_width, stroke_color);
  const dropShadow =
    shadow_offset > 0
      ? `${shadow_offset}px ${shadow_offset}px 2px rgb(${shadow_color[0]}, ${shadow_color[1]}, ${shadow_color[2]})`
      : null;

  const textShadow = [strokeShadow, dropShadow].filter(Boolean).join(', ') || undefined;

  return (
    <div
      className={`region-overlay${isSelected ? ' selected' : ''}${isEditing ? ' editing' : ''}`}
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        cursor: isEditing ? 'text' : 'move',
      }}
      onClick={(e) => { e.stopPropagation(); onSelect(); }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onDoubleClick={handleDoubleClick}
    >
      {isSelected && (
        <RegionToolbar
          region={region}
          onChange={onChange}
          onDeselect={onDeselect}
        />
      )}

      <div
        ref={contentRef}
        className="region-text-content"
        contentEditable
        suppressContentEditableWarning
        style={{
          fontSize: font_size,
          fontWeight: bold ? 'bold' : 'normal',
          color: colorStr,
          lineHeight: `${font_size + 10}px`,
          textShadow,
          pointerEvents: isEditing ? 'text' : 'none',
        }}
        onBlur={handleBlur}
        onKeyDown={(e) => e.stopPropagation()}
      />
    </div>
  );
}

export default RegionOverlay;
