import { useState, useRef, useEffect } from 'react';
import { ChatMessageBubble } from './components';
import type { ChatMessage, ResearchRequest } from './types';
import { researchService } from './services/researchService';
import './App.css';

let msgIdCounter = 0;
function nextId() {
  return `msg-${++msgIdCounter}-${Date.now()}`;
}

function App() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'assistant',
      content: 'Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích! 🚀',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [waitingClarification, setWaitingClarification] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const addMessage = (msg: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMsg: ChatMessage = {
      ...msg,
      id: nextId(),
      timestamp: new Date(),
    };
    setChatMessages((prev) => [...prev, newMsg]);
  };

  const handleSend = async (prompt?: string) => {
    const text = prompt ?? inputValue.trim();
    if (!text || isLoading) return;

    // Add user bubble
    addMessage({ type: 'user', content: text });
    setInputValue('');
    setIsLoading(true);
    setWaitingClarification(false);

    const request: ResearchRequest = { user_prompt: text };

    await runPipeline(request);
  };

  const runPipeline = async (request: ResearchRequest) => {
    try {
      await researchService.callStageAResearch(
        request,
        (streamMessage) => {
          // Map each stream event to a ChatMessage
          if (streamMessage.status === 'chat_response') {
            addMessage({ type: 'assistant', content: streamMessage.message });
            setIsLoading(false);
          } else if (streamMessage.status === 'clarification_provided') {
            addMessage({
              type: 'clarification',
              content: streamMessage.message,
              clarificationData: {
                detected_info: streamMessage.detected_info || '',
                questions_for_user: streamMessage.questions_for_user || (streamMessage as any).questions || [],
                clarified_input: streamMessage.clarified_input || { user_prompt: '' },
                explanations: streamMessage.explanations || {},
                auto_proceeding: streamMessage.auto_proceeding || false,
                note: streamMessage.note || '',
              },
            });
            setIsLoading(false);
            setWaitingClarification(true);
          } else if (streamMessage.status === 'plan_completed' && streamMessage.plan) {
            addMessage({
              type: 'plan',
              content: streamMessage.message,
              planData: streamMessage.plan,
            });
          } else if (streamMessage.status === 'react_completed' && streamMessage.react_summary) {
            addMessage({
              type: 'react_summary',
              content: streamMessage.message,
              reactSummaryData: streamMessage.react_summary,
            });
          } else if (streamMessage.status === 'evidence_ready' && streamMessage.evidence) {
            addMessage({
              type: 'evidence',
              content: streamMessage.message,
              evidenceData: streamMessage.evidence,
              evidenceCountData: streamMessage.evidence_count,
            });
          } else if (streamMessage.status === 'report_ready' && streamMessage.report) {
            addMessage({
              type: 'report',
              content: streamMessage.message,
              reportData: streamMessage.report,
            });
          } else if (streamMessage.status === 'completed') {
            addMessage({
              type: 'completed',
              content: streamMessage.message,
              mongodbId: streamMessage.mongodb_id,
            });
            setIsLoading(false);
          } else if (streamMessage.status === 'error') {
            addMessage({ type: 'error', content: streamMessage.message });
            setIsLoading(false);
          } else if (streamMessage.status === 'progress' || streamMessage.status === 'starting') {
            addMessage({ type: 'status', content: streamMessage.message });
          }
        },
        (errorMsg) => {
          addMessage({ type: 'error', content: errorMsg });
          setIsLoading(false);
        }
      );
    } catch {
      addMessage({ type: 'error', content: 'Lỗi không xác định' });
      setIsLoading(false);
    }
  };

  const handleClarificationConfirm = (overrides: Partial<ResearchRequest>) => {
    setWaitingClarification(false);
    setIsLoading(true);
    addMessage({ type: 'status', content: 'Đã xác nhận thông tin. Tiếp tục nghiên cứu...' });

    const confirmed: ResearchRequest = {
      user_prompt: overrides.user_prompt || '',
      nganh_hang: overrides.nganh_hang,
      thi_truong_muc_tieu: overrides.thi_truong_muc_tieu,
      phan_khuc_quan_tam: overrides.phan_khuc_quan_tam,
      doi_thu_seed: overrides.doi_thu_seed,
      khung_thoi_gian: overrides.khung_thoi_gian,
      muc_tieu_nghien_cuu: overrides.muc_tieu_nghien_cuu,
    };
    runPipeline(confirmed);
  };

  const handleReset = () => {
    setChatMessages([
      {
        id: 'welcome',
        type: 'assistant',
        content: 'Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích! 🚀',
        timestamp: new Date(),
      },
    ]);
    setIsLoading(false);
    setWaitingClarification(false);
    setInputValue('');
    msgIdCounter = 0;
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🎯 MarketMind AI</h1>
          <p>Trợ lý nghiên cứu thị trường thông minh</p>
        </div>
        <button className="header-reset" onClick={handleReset} title="Cuộc hội thoại mới">
          ✨ Mới
        </button>
      </header>

      {/* Chat area */}
      <main className="chat-area">
        <div className="chat-messages">
          {chatMessages.map((msg) => (
            <ChatMessageBubble
              key={msg.id}
              message={msg}
              isLoading={isLoading}
              onClarificationConfirm={handleClarificationConfirm}
            />
          ))}

          {isLoading && !waitingClarification && (
            <div className="chat-row chat-row--assistant">
              <div className="chat-avatar chat-avatar--assistant">🤖</div>
              <div className="chat-bubble chat-bubble--typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Input bar */}
      <footer className="chat-input-bar">
        <div className="input-bar-inner">
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập yêu cầu nghiên cứu của bạn..."
            disabled={isLoading}
            rows={1}
          />
          <button
            className="send-btn"
            onClick={() => handleSend()}
            disabled={isLoading || !inputValue.trim()}
            title="Gửi"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <small className="input-hint">
          Nhấn <kbd>Enter</kbd> để gửi · <kbd>Shift+Enter</kbd> xuống dòng
        </small>
      </footer>
    </div>
  );
}

export default App;