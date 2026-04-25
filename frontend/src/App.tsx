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
      clarification: undefined,
      plan: undefined,
      reactSummary: undefined,
      evidence: undefined,
      evidenceCount: undefined,
      report: undefined,
      markdownReport: undefined,
      chatResponse: undefined,
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
              isLoading: streamMessage.status !== 'completed' && streamMessage.status !== 'error' && streamMessage.status !== 'clarification_provided' && streamMessage.status !== 'chat_response',
              error: streamMessage.status === 'error' ? streamMessage.message : undefined,
            };

            // Handle different stream events
            if (streamMessage.status === 'chat_response') {
              newState.chatResponse = streamMessage.message;
              newState.isLoading = false;
            } else if (streamMessage.status === 'clarification_provided') {
              newState.clarification = {
                detected_info: streamMessage.detected_info || '',
                questions_for_user: streamMessage.questions_for_user || [],
                clarified_input: streamMessage.clarified_input || { user_prompt: '' },
                explanations: streamMessage.explanations || {},
                auto_proceeding: streamMessage.auto_proceeding || false,
                note: streamMessage.note || '',
              };
              newState.isLoading = false; // Stop loading for clarification step
            } else if (streamMessage.status === 'plan_completed' && streamMessage.plan) {
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

  const handleClarificationConfirm = (overrides: Partial<ResearchRequest>) => {
    if (uiState.clarification) {
      // Merge with original clarified input
      const confirmedRequest: ResearchRequest = {
        user_prompt: uiState.clarification.clarified_input.user_prompt || '',
        nganh_hang: overrides.nganh_hang || uiState.clarification.clarified_input.nganh_hang,
        thi_truong_muc_tieu: overrides.thi_truong_muc_tieu || uiState.clarification.clarified_input.thi_truong_muc_tieu,
        phan_khuc_quan_tam: overrides.phan_khuc_quan_tam || uiState.clarification.clarified_input.phan_khuc_quan_tam,
        doi_thu_seed: overrides.doi_thu_seed || uiState.clarification.clarified_input.doi_thu_seed,
        khung_thoi_gian: overrides.khung_thoi_gian || uiState.clarification.clarified_input.khung_thoi_gian,
        muc_tieu_nghien_cuu: overrides.muc_tieu_nghien_cuu || uiState.clarification.clarified_input.muc_tieu_nghien_cuu,
      };

      // Continue with the confirmed research
      setUIState((prev) => ({
        ...prev,
        isLoading: true,
        clarification: undefined,
      }));

      // Resubmit with confirmed data
      handleResearchSubmit(confirmedRequest);
    }
  };

  const handleReset = () => {
    setUIState({
      isLoading: false,
      messages: [],
      clarification: undefined,
      plan: undefined,
      reactSummary: undefined,
      evidence: undefined,
      evidenceCount: undefined,
      report: undefined,
      markdownReport: undefined,
      chatResponse: undefined,
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
            <ResearchForm 
              onSubmit={handleResearchSubmit} 
              isLoading={uiState.isLoading}
              clarification={uiState.clarification}
              onClarificationConfirm={handleClarificationConfirm}
            />
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

        {uiState.chatResponse && (
          <div className="chat-response-section">
            <div className="chat-bubble">
              <span className="chat-icon">🤖</span>
              <div className="chat-content">
                <p>{uiState.chatResponse}</p>
              </div>
            </div>
            <button onClick={handleReset} className="reset-btn" style={{marginTop: '1rem'}}>
              Bắt Đầu Lại
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