/** 搜尋欄元件 */
import { useState } from 'react';
import './SearchBar.css';

function SearchBar({ onSearch }) {
  const [searchParams, setSearchParams] = useState({
    category: '',
    style: [],
    scenario: [],
    color_scheme: '',
    mood: [],
    keywords: [],
  });

  const [keywordInput, setKeywordInput] = useState('');

  const handleInputChange = (field, value) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleKeywordAdd = () => {
    if (keywordInput.trim()) {
      setSearchParams(prev => ({
        ...prev,
        keywords: [...prev.keywords, keywordInput.trim()],
      }));
      setKeywordInput('');
    }
  };

  const handleKeywordRemove = (index) => {
    setSearchParams(prev => ({
      ...prev,
      keywords: prev.keywords.filter((_, i) => i !== index),
    }));
  };

  const handleSearch = () => {
    const params = {};
    if (searchParams.category) params.category = searchParams.category;
    if (searchParams.style.length > 0) params.style = searchParams.style;
    if (searchParams.scenario.length > 0) params.scenario = searchParams.scenario;
    if (searchParams.color_scheme) params.color_scheme = searchParams.color_scheme;
    if (searchParams.mood.length > 0) params.mood = searchParams.mood;
    if (searchParams.keywords.length > 0) params.keywords = searchParams.keywords;

    onSearch(params);
  };

  const handleReset = () => {
    setSearchParams({
      category: '',
      style: [],
      scenario: [],
      color_scheme: '',
      mood: [],
      keywords: [],
    });
    setKeywordInput('');
    onSearch({});
  };

  return (
    <div className="search-bar">
      <h3>搜尋素材</h3>
      
      <div className="search-fields">
        <div className="search-field">
          <label>類型</label>
          <select
            value={searchParams.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
          >
            <option value="">全部</option>
            <option value="人物">人物</option>
            <option value="背景">背景</option>
            <option value="裝飾">裝飾</option>
            <option value="物件">物件</option>
            <option value="文字">文字</option>
            <option value="其他">其他</option>
          </select>
        </div>

        <div className="search-field">
          <label>色系</label>
          <select
            value={searchParams.color_scheme}
            onChange={(e) => handleInputChange('color_scheme', e.target.value)}
          >
            <option value="">全部</option>
            <option value="暖色">暖色</option>
            <option value="冷色">冷色</option>
            <option value="中性">中性</option>
            <option value="鮮豔">鮮豔</option>
            <option value="柔和">柔和</option>
            <option value="單色">單色</option>
          </select>
        </div>

        <div className="search-field">
          <label>關鍵字</label>
          <div className="keyword-input-group">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleKeywordAdd()}
              placeholder="輸入關鍵字後按 Enter"
            />
            <button onClick={handleKeywordAdd}>新增</button>
          </div>
          {searchParams.keywords.length > 0 && (
            <div className="keyword-tags">
              {searchParams.keywords.map((keyword, index) => (
                <span key={index} className="keyword-tag">
                  {keyword}
                  <button onClick={() => handleKeywordRemove(index)}>×</button>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="search-actions">
        <button onClick={handleSearch} className="search-button">
          搜尋
        </button>
        <button onClick={handleReset} className="reset-button">
          重置
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
