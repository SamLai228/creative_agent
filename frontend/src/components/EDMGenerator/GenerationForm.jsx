import { useState } from 'react';
import { generateHtml } from '../../services/api';
import './GenerationForm.css';

function GenerationForm({ onComplete }) {
  const [formValues, setFormValues] = useState({
    product_name: '',
    promotion_type: '',
    key_message: '',
    target_audience: '',
    tone: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await generateHtml(formValues);
      onComplete(result.html);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || '生成失敗';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field) => (e) =>
    setFormValues((v) => ({ ...v, [field]: e.target.value }));

  return (
    <div className="generation-form">
      <div className="form-header">
        <h2>生成 EDM</h2>
        <p className="form-subtitle">填寫需求，讓 AI 生成完整 HTML EDM</p>
      </div>

      <section className="form-section">
        <h3 className="section-title">填寫需求</h3>
        <form onSubmit={handleSubmit} className="requirements-form">
          <div className="form-row">
            <div className="form-group">
              <label>產品 / 服務名稱</label>
              <input
                type="text"
                value={formValues.product_name}
                onChange={updateField('product_name')}
                placeholder="例：夏日特賣會"
              />
            </div>
            <div className="form-group">
              <label>促銷類型</label>
              <input
                type="text"
                value={formValues.promotion_type}
                onChange={updateField('promotion_type')}
                placeholder="例：限時折扣、新品發布"
              />
            </div>
          </div>

          <div className="form-group">
            <label>主要訊息</label>
            <textarea
              value={formValues.key_message}
              onChange={updateField('key_message')}
              placeholder="例：全館 7 折，活動限時三天"
              rows={3}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>目標受眾</label>
              <select
                value={formValues.target_audience}
                onChange={updateField('target_audience')}
              >
                <option value="">請選擇目標受眾</option>
                <option value="0–18 歲">0–18 歲</option>
                <option value="18–24 歲">18–24 歲</option>
                <option value="25–34 歲 ｜ 單身">25–34 歲 ｜ 單身</option>
                <option value="25–34 歲 ｜ 已婚未育">25–34 歲 ｜ 已婚未育</option>
                <option value="25–34 歲 ｜ 有子女（幼齡）">25–34 歲 ｜ 有子女（幼齡）</option>
                <option value="35–45 歲 ｜ 單身">35–45 歲 ｜ 單身</option>
                <option value="35–45 歲 ｜ 已婚未育">35–45 歲 ｜ 已婚未育</option>
                <option value="35–45 歲 ｜ 有子女（未成年）">35–45 歲 ｜ 有子女（未成年）</option>
                <option value="45–64 歲 ｜ 單身">45–64 歲 ｜ 單身</option>
                <option value="45–64 歲 ｜ 已婚未育">45–64 歲 ｜ 已婚未育</option>
                <option value="45–64 歲 ｜ 有子女（未成年）">45–64 歲 ｜ 有子女（未成年）</option>
                <option value="45–64 歲 ｜ 有子女（已成年）">45–64 歲 ｜ 有子女（已成年）</option>
                <option value="65 歲以上">65 歲以上</option>
              </select>
            </div>
            <div className="form-group">
              <label>文案風格</label>
              <input
                type="text"
                value={formValues.tone}
                onChange={updateField('tone')}
                placeholder="例：活潑、專業、溫暖"
              />
            </div>
          </div>

          {error && <div className="form-error">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="btn-generate"
          >
            {loading ? (
              <span className="loading-text">
                <span className="spinner" />
                生成中...
              </span>
            ) : (
              '生成 EDM'
            )}
          </button>
        </form>
      </section>
    </div>
  );
}

export default GenerationForm;
