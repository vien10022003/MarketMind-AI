import { useState } from 'react';
import { ResearchForm, ResearchProgress, ResearchReportComponent } from './components';
import type { ResearchRequest, UIState } from './types';
import { researchService } from './services/researchService';
import './App.css';

function App() {
  const [uiState, setUIState] = useState<UIState>({
    isLoading: false,
    messages: [],
  });

  const handleResearchSubmit = async (request: ResearchRequest) => {
    setUIState({
      isLoading: true,
      messages: [],
      report: undefined,
      error: undefined,
    });

    try {
      await researchService.callStageAResearch(
        request,
        (streamMessage) => {
          setUIState((prev) => {
            const newMessages = [...prev.messages, streamMessage.message];

            return {
              ...prev,
              messages: newMessages,
              report: streamMessage.status === 'completed' ? streamMessage.report : prev.report,
              mongodbId: streamMessage.status === 'completed' ? streamMessage.mongodb_id : prev.mongodbId,
              isLoading: streamMessage.status !== 'completed' && streamMessage.status !== 'error',
              error: streamMessage.status === 'error' ? streamMessage.message : undefined,
            };
          });
        },
        (errorMsg) => {
          setUIState((prev) => ({
            ...prev,
            isLoading: false,
            error: errorMsg,
          }));
        }
      );
    } catch (err) {
      setUIState((prev) => ({
        ...prev,
        isLoading: false,
        error: 'Lỗi không xác định',
      }));
    }
  };

  const handleReset = () => {
    setUIState({
      isLoading: false,
      messages: [],
      report: undefined,
      error: undefined,
    });
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎯 MarketMind AI - Marketing Assistant</h1>
        <p>Hệ thống trợ lý Marketing thông minh sử dụng GenAI & Agentic AI</p>
      </header>

      <main className="app-main">
        <div className="app-grid">
          <div className="form-section">
            <ResearchForm onSubmit={handleResearchSubmit} isLoading={uiState.isLoading} />
          </div>

          <div className="progress-section">
            <ResearchProgress messages={uiState.messages} isLoading={uiState.isLoading} />
          </div>
        </div>

        {uiState.error && (
          <div className="error-container">
            <p className="error-message">❌ Lỗi: {uiState.error}</p>
            <button onClick={handleReset} className="reset-btn">
              Thử Lại
            </button>
          </div>
        )}

        {uiState.report && (
          <div className="report-section">
            <ResearchReportComponent report={uiState.report} mongodbId={uiState.mongodbId} />
            <button onClick={handleReset} className="reset-btn">
              Bắt đầu lại
            </button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 MarketMind AI. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
