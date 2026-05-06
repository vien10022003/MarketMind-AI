import React, { useState } from 'react';
import './ModelSelector.css';

export interface ModelSelectorProps {
  currentProvider: 'llama' | 'gemini-2.5' | 'gemini-3.1';
  onProviderChange: (provider: 'llama' | 'gemini-2.5' | 'gemini-3.1') => void;
}

const MODEL_LABELS: Record<string, string> = {
  llama: 'Llama-3.2 (Local)',
  'gemini-2.5': 'Gemini 2.5 Flash',
  'gemini-3.1': 'Gemini 3.1 Flash',
};

export const ModelSelector: React.FC<ModelSelectorProps> = ({ currentProvider, onProviderChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (provider: 'llama' | 'gemini-2.5' | 'gemini-3.1') => {
    onProviderChange(provider);
    setIsOpen(false);
  };

  return (
    <div className="model-selector">
      <button
        className="model-selector-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Click to change AI model"
      >
        <span className="model-selector-label">Model: {MODEL_LABELS[currentProvider]}</span>
        <span className="model-selector-chevron">▼</span>
      </button>

      {isOpen && (
        <div className="model-selector-dropdown">
          {(Object.keys(MODEL_LABELS) as Array<'llama' | 'gemini-2.5' | 'gemini-3.1'>).map((provider) => (
            <button
              key={provider}
              className={`model-selector-option ${currentProvider === provider ? 'active' : ''}`}
              onClick={() => handleSelect(provider)}
            >
              <span className="model-selector-option-label">{MODEL_LABELS[provider]}</span>
              {currentProvider === provider && <span className="model-selector-checkmark">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
