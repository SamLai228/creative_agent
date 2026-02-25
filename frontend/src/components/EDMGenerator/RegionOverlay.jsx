import { useRef, useEffect, useState } from 'react';
import RegionToolbar from './RegionToolbar';
import './RegionOverlay.css';

function RegionOverlay({ region, scale, isSelected, onSelect, onDeselect, onChange }) {
  const { text, x, y, width, height, font_size, bold, color } = region;
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
          pointerEvents: isEditing ? 'text' : 'none',
        }}
        onBlur={handleBlur}
        onKeyDown={(e) => e.stopPropagation()}
      />
    </div>
  );
}

export default RegionOverlay;
