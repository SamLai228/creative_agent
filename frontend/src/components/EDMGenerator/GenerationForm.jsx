import { useState, useEffect } from 'react';
import { getTemplates, getTemplateRegions, generateCopyForTemplate } from '../../services/api';
import './GenerationForm.css';

function GenerationForm({ onComplete }) {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [formValues, setFormValues] = useState({
    product_name: '',
    promotion_type: '',
    key_message: '',
    target_audience: '',
    tone: '',
  });
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    getTemplates()
      .then(setTemplates)
      .catch(() => setError('無法載入 template 列表'));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedTemplate) {
      setError('請選擇 Template');
      return;
    }
    setLoading(true);
    setError('');

    try {
      // Step 1: Get region config
      setLoadingStep('載入 region 配置...');
      const regionConfig = await getTemplateRegions(selectedTemplate);
      const configRegions = regionConfig.regions;

      // Step 2: Generate copy
      setLoadingStep('LLM 生成文案中...');
      const copyResult = await generateCopyForTemplate({
        template_name: selectedTemplate,
        ...formValues,
      });
      const copyMap = copyResult.copy;

      // Step 3: Merge into flat region format (include stroke/shadow defaults from config)
      const merged = configRegions.map((r) => ({
        id: r.id,
        text: copyMap[r.id] ?? '',
        x: r.bbox[0],
        y: r.bbox[1],
        width: r.bbox[2],
        height: r.bbox[3],
        font_size: r.font_size || 32,
        bold: r.bold ?? false,
        color: r.color || [255, 255, 255],
        anchor: r.anchor || 'lt',
        max_width: r.max_width ?? r.bbox[2],
        stroke_width: r.stroke_width ?? 0,
        stroke_color: r.stroke_color ?? [0, 0, 0],
        shadow_offset: r.shadow_offset ?? 0,
        shadow_color: r.shadow_color ?? [0, 0, 0],
      }));

      onComplete(selectedTemplate, merged);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || '生成失敗';
      setError(detail);
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  const updateField = (field) => (e) =>
    setFormValues((v) => ({ ...v, [field]: e.target.value }));

  return (
    <div className="generation-form">
      <div className="form-header">
        <h2>生成 EDM</h2>
        <p className="form-subtitle">選擇 Template，填寫需求，讓 LLM 自動生成文案</p>
      </div>

      {/* Template selector */}
      <section className="form-section">
        <h3 className="section-title">選擇 Template</h3>
        {templates.length === 0 ? (
          <p className="form-hint">載入中...</p>
        ) : (
          <div className="template-grid">
            {templates.map((t) => (
              <div
                key={t.name}
                className={`template-item ${selectedTemplate === t.name ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate(t.name)}
              >
                <div className="template-img-wrap">
                  <img src={t.url} alt={t.stem} />
                </div>
                <span className="template-label">{t.stem}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Requirements form */}
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
              <input
                type="text"
                value={formValues.target_audience}
                onChange={updateField('target_audience')}
                placeholder="例：25-35 歲女性"
              />
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
            disabled={loading || !selectedTemplate}
            className="btn-generate"
          >
            {loading ? (
              <span className="loading-text">
                <span className="spinner" />
                {loadingStep || '生成中...'}
              </span>
            ) : (
              '生成文案並進入編輯'
            )}
          </button>
        </form>
      </section>
    </div>
  );
}

export default GenerationForm;
