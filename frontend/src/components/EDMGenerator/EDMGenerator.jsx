import { useState } from 'react';
import GenerationForm from './GenerationForm';
import EDMPreview from './EDMPreview';
import './EDMGenerator.css';

function EDMGenerator() {
  const [step, setStep] = useState('form'); // 'form' | 'preview'
  const [html, setHtml] = useState('');

  const handleGenerateDone = (generatedHtml) => {
    setHtml(generatedHtml);
    setStep('preview');
  };

  const handleBack = () => {
    setStep('form');
  };

  const handleRegenerate = () => {
    setStep('form');
    setHtml('');
  };

  return (
    <div className="edm-generator">
      {step === 'form' && (
        <GenerationForm onComplete={handleGenerateDone} />
      )}
      {step === 'preview' && (
        <EDMPreview
          html={html}
          onBack={handleBack}
          onRegenerate={handleRegenerate}
        />
      )}
    </div>
  );
}

export default EDMGenerator;
