/** 標籤展示元件 */
import './TagDisplay.css';

function TagDisplay({ tags }) {
  if (!tags) {
    return <div className="tag-display">無標籤資訊</div>;
  }

  return (
    <div className="tag-display">
      <div className="tag-section">
        <h3>類型</h3>
        <span className="tag-badge category">{tags.category}</span>
      </div>

      <div className="tag-section">
        <h3>風格</h3>
        <div className="tag-list">
          {tags.style && tags.style.length > 0 ? (
            tags.style.map((style, index) => (
              <span key={index} className="tag-badge style">{style}</span>
            ))
          ) : (
            <span className="tag-empty">無</span>
          )}
        </div>
      </div>

      <div className="tag-section">
        <h3>情境</h3>
        <div className="tag-list">
          {tags.scenario && tags.scenario.length > 0 ? (
            tags.scenario.map((scenario, index) => (
              <span key={index} className="tag-badge scenario">{scenario}</span>
            ))
          ) : (
            <span className="tag-empty">無</span>
          )}
        </div>
      </div>

      <div className="tag-section">
        <h3>色系</h3>
        <span className="tag-badge color">{tags.color_scheme}</span>
      </div>

      <div className="tag-section">
        <h3>氛圍</h3>
        <div className="tag-list">
          {tags.mood && tags.mood.length > 0 ? (
            tags.mood.map((mood, index) => (
              <span key={index} className="tag-badge mood">{mood}</span>
            ))
          ) : (
            <span className="tag-empty">無</span>
          )}
        </div>
      </div>

      {tags.keywords && tags.keywords.length > 0 && (
        <div className="tag-section">
          <h3>關鍵字</h3>
          <div className="tag-list">
            {tags.keywords.map((keyword, index) => (
              <span key={index} className="tag-badge keyword">{keyword}</span>
            ))}
          </div>
        </div>
      )}

      {tags.usage_scope && (
        <div className="tag-section">
          <h3>可用範圍</h3>
          <p className="usage-scope">{tags.usage_scope}</p>
        </div>
      )}
    </div>
  );
}

export default TagDisplay;
