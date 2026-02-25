import { useState } from 'react';
import GenerationForm from './GenerationForm';
import EDMCanvas from './EDMCanvas';
import './EDMGenerator.css';

function EDMGenerator() {
  const [step, setStep] = useState('form'); // 'form' | 'editor' | 'done'
  const [templateName, setTemplateName] = useState('');
  const [regions, setRegions] = useState([]);
  const [exportedUrl, setExportedUrl] = useState('');

  const handleGenerateDone = (name, generatedRegions) => {
    setTemplateName(name);
    setRegions(generatedRegions);
    setStep('editor');
  };

  const handleExportDone = (url) => {
    setExportedUrl(url);
    setStep('done');
  };

  const handleReset = () => {
    setStep('form');
    setRegions([]);
    setExportedUrl('');
    setTemplateName('');
  };

  return (
    <div className="edm-generator">
      {step === 'form' && (
        <GenerationForm onComplete={handleGenerateDone} />
      )}
      {step === 'editor' && (
        <EDMCanvas
          templateName={templateName}
          regions={regions}
          onRegionsChange={setRegions}
          onExport={handleExportDone}
          onBack={() => setStep('form')}
        />
      )}
      {step === 'done' && (
        <div className="export-done glass-card">
          <h2>匯出完成！</h2>
          <div className="export-preview-wrap">
            <img src={exportedUrl} alt="Exported EDM" className="export-preview" />
          </div>
          <div className="export-actions">
            <a href={exportedUrl} download className="btn-primary">下載 PNG</a>
            <button onClick={() => setStep('editor')} className="btn-secondary">返回編輯</button>
            <button onClick={handleReset} className="btn-ghost">重新開始</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default EDMGenerator;
