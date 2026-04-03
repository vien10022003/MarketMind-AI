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
      plan: undefined,
      reactSummary: undefined,
      evidence: undefined,
      evidenceCount: undefined,
      report: undefined,
      markdownReport: undefined,
      error: undefined,
    });

    try {
      await researchService.callStageAResearch(
        request,
        (streamMessage) => {
          setUIState((prev) => {
            const newMessages = [...prev.messages, streamMessage.message];

            const newState = {
              ...prev,
              messages: newMessages,
              isLoading: streamMessage.status !== 'completed' && streamMessage.status !== 'error',
              error: streamMessage.status === 'error' ? streamMessage.message : undefined,
            };

            // Handle different stream events
            if (streamMessage.status === 'plan_completed' && streamMessage.plan) {
              newState.plan = streamMessage.plan;
            } else if (streamMessage.status === 'react_completed' && streamMessage.react_summary) {
              newState.reactSummary = streamMessage.react_summary;
            } else if (streamMessage.status === 'evidence_ready' && streamMessage.evidence) {
              newState.evidence = streamMessage.evidence;
              newState.evidenceCount = streamMessage.evidence_count;
            } else if (streamMessage.status === 'report_ready' && streamMessage.report) {
              newState.report = streamMessage.report;
              newState.markdownReport = streamMessage.markdown_report;
            } else if (streamMessage.status === 'completed') {
              newState.mongodbId = streamMessage.mongodb_id;
            }

            return newState;
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
      plan: undefined,
      reactSummary: undefined,
      evidence: undefined,
      evidenceCount: undefined,
      report: undefined,
      markdownReport: undefined,
      error: undefined,
      mongodbId: undefined,
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

        {uiState.plan && (
          <div className="plan-section">
            <h2>📋 Kế Hoạch Nghiên Cứu</h2>
            
            <section className="plan-subsection">
              <h3>Các Câu Hỏi Nghiên Cứu</h3>
              <ul>
                {uiState.plan.research_questions.map((q, idx) => (
                  <li key={idx}>{q}</li>
                ))}
              </ul>
            </section>

            <section className="plan-subsection">
              <h3>Giả Thuyết</h3>
              <ul>
                {uiState.plan.hypotheses.map((h, idx) => (
                  <li key={idx}>{h}</li>
                ))}
              </ul>
            </section>

            <section className="plan-subsection">
              <h3>Các Bước Thực Hiện</h3>
              <ol>
                {uiState.plan.steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </section>

            <section className="plan-subsection">
              <h3>Tiêu Chí Thành Công</h3>
              <ul>
                {uiState.plan.success_criteria.map((criterion, idx) => (
                  <li key={idx}>{criterion}</li>
                ))}
              </ul>
            </section>
          </div>
        )}

        {uiState.reactSummary && (
          <div className="react-summary-section">
            <h2>🔍 Tóm Tắt Quá Trình Thu Thập Dữ Liệu</h2>
            
            <div className="react-stats">
              <div className="stat-item">
                <span className="stat-label">Số Lần Tìm Kiếm:</span>
                <span className="stat-value">{uiState.reactSummary.tool_calls}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Tổng Dữ Liệu Thu Được:</span>
                <span className="stat-value">{uiState.reactSummary.total_evidence_collected}</span>
              </div>
            </div>

            {uiState.reactSummary.intermediate_steps.length > 0 && (
              <details className="intermediate-steps">
                <summary>Chi tiết các bước trung gian</summary>
                <div className="steps-list">
                  {uiState.reactSummary.intermediate_steps.map((step, idx) => (
                    <div key={idx} className="step-item">
                      <p><strong>Bước {step.step}:</strong> {step.action}</p>
                      <p><strong>Truy vấn:</strong> {step.query}</p>
                      <p><strong>Kết quả tìm được:</strong> {step.result_count}</p>
                      <p><strong>Lý do:</strong> {step.reason}</p>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}

        {uiState.evidence && uiState.evidence.length > 0 && (
          <div className="evidence-section">
            <h2>📚 Các Nguồn Dữ Liệu Thu Thập Được</h2>
            
            {uiState.evidenceCount && (
              <div className="evidence-stats">
                <p>Tổng dữ liệu gốc: <strong>{uiState.evidenceCount.raw}</strong> | Dữ liệu hợp lệ: <strong>{uiState.evidenceCount.filtered}</strong></p>
              </div>
            )}

            <div className="evidence-table">
              <div className="evidence-list">
                {uiState.evidence.map((item, idx) => (
                  <div key={idx} className="evidence-item">
                    <h4>
                      <a href={item.url} target="_blank" rel="noopener noreferrer">
                        {item.title}
                      </a>
                    </h4>
                    <p className="evidence-snippet">{item.snippet}</p>
                    <div className="evidence-meta">
                      {item.published_date && <span className="evidence-date">📅 {item.published_date}</span>}
                      <span className="evidence-score">⭐ {(item.source_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
