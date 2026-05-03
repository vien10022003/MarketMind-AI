import { useState, useRef, useEffect } from 'react';
import { ChatMessageBubble } from './components';
import type { ChatMessage, ResearchRequest, ConversationTurn, ContentBrief, StageBOutput, ResearchReport } from './types';
import { researchService } from './services/researchService';
import { initializeBackendUrl } from './config';
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
  const [waitingMarketingForm, setWaitingMarketingForm] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Stage B/C state
  const [lastReportData, setLastReportData] = useState<ResearchReport | null>(null);
  const [lastReportInput, setLastReportInput] = useState<Record<string, unknown> | null>(null);
  const [lastMongodbId, setLastMongodbId] = useState<string | undefined>(undefined);
  const [lastStrategy, setLastStrategy] = useState<StageBOutput | null>(null);

  // Initialize backend URL from Firebase on app startup
  useEffect(() => {
    initializeBackendUrl();
  }, []);

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

  /**
   * Extract the last N user/assistant conversation turns for short-term memory.
   * This gives the LLM context about recent conversation.
   */
  const getRecentHistory = (maxTurns = 3): ConversationTurn[] => {
    const turns: ConversationTurn[] = [];
    // Walk through chatMessages, pick user + assistant/chat_response pairs
    for (const msg of chatMessages) {
      if (msg.type === 'user') {
        turns.push({ role: 'user', content: msg.content });
      } else if (msg.type === 'assistant' || msg.type === 'knowledge') {
        turns.push({ role: 'assistant', content: msg.content });
      }
    }
    // Return only the last N turns (each turn = 1 message)
    // We want last maxTurns pairs → maxTurns * 2 messages
    return turns.slice(-(maxTurns * 2));
  };

  const handleSend = async (prompt?: string) => {
    const text = prompt ?? inputValue.trim();
    if (!text || isLoading) return;

    // Build conversation history BEFORE adding the new user message
    const conversationHistory = getRecentHistory(3);

    // Add user bubble
    addMessage({ type: 'user', content: text });
    setInputValue('');
    setIsLoading(true);
    setWaitingMarketingForm(false);

    const request: ResearchRequest = {
      user_prompt: text,
      conversation_history: conversationHistory,
    };

    await runPipeline(request);
  };

  /**
   * Shared stream event handler for both main endpoint and marketing endpoint
   */
  const handleStreamMessage = (streamMessage: import('./types').StreamMessage) => {
    // ─── Chat response ───
    if (streamMessage.status === 'chat_response') {
      addMessage({ type: 'assistant', content: streamMessage.message });
      setIsLoading(false);

    // ─── Knowledge path ───
    } else if (streamMessage.status === 'knowledge_searching') {
      addMessage({ type: 'status', content: streamMessage.message });
    } else if (streamMessage.status === 'knowledge_response') {
      addMessage({
        type: 'knowledge',
        content: streamMessage.message,
        knowledgeData: {
          answer: streamMessage.message,
          sources: streamMessage.sources || [],
        },
      });
      setIsLoading(false);

    // ─── Marketing form path ───
    } else if (streamMessage.status === 'show_marketing_form') {
      addMessage({
        type: 'marketing_form',
        content: streamMessage.message,
        marketingFormData: {
          detected_prompt: streamMessage.detected_prompt || '',
        },
      });
      setIsLoading(false);
      setWaitingMarketingForm(true);

    // ─── Research pipeline events (unchanged) ───
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
      // Save report data for Stage B
      setLastReportData(streamMessage.report);
    } else if (streamMessage.status === 'completed') {
      addMessage({
        type: 'completed',
        content: streamMessage.message,
        mongodbId: streamMessage.mongodb_id,
      });
      setLastMongodbId(streamMessage.mongodb_id);
      setIsLoading(false);

      // Auto-trigger Stage B after Stage A completes
      if (lastReportData || streamMessage.report) {
        addMessage({
          type: 'assistant',
          content: '📊 Báo cáo nghiên cứu đã hoàn tất! Bây giờ tôi sẽ xây dựng chiến lược marketing dựa trên kết quả nghiên cứu...',
        });
        // Slight delay before triggering Stage B
        setTimeout(() => {
          handleStartStageB(streamMessage.report || lastReportData!, streamMessage.mongodb_id);
        }, 1500);
      }
    } else if (streamMessage.status === 'error') {
      addMessage({ type: 'error', content: streamMessage.message });
      setIsLoading(false);
    } else if (streamMessage.status === 'progress' || streamMessage.status === 'starting') {
      addMessage({ type: 'status', content: streamMessage.message });
    }
  };

  /**
   * Stage B stream event handler
   */
  const handleStageBStreamMessage = (streamMessage: import('./types').StreamMessage) => {
    if (streamMessage.status === 'stage_b_completed' && streamMessage.strategy) {
      // Show the full strategy
      addMessage({
        type: 'strategy',
        content: streamMessage.message,
        strategyData: streamMessage.strategy,
      });
      setLastStrategy(streamMessage.strategy);

      // Show content briefs editor
      if (streamMessage.strategy.content_briefs?.length) {
        addMessage({
          type: 'content_briefs',
          content: `📝 ${streamMessage.strategy.content_briefs.length} content briefs đã sẵn sàng để review`,
          contentBriefsData: streamMessage.strategy.content_briefs,
        });
      }
      setIsLoading(false);
    } else if (streamMessage.status === 'error') {
      addMessage({ type: 'error', content: streamMessage.message });
      setIsLoading(false);
    } else if (
      streamMessage.status === 'stage_b_starting' ||
      streamMessage.status === 'progress' ||
      streamMessage.status === 'swot_completed' ||
      streamMessage.status === 'usp_completed' ||
      streamMessage.status === 'persona_completed' ||
      streamMessage.status === 'pillars_completed' ||
      streamMessage.status === 'campaign_plan_completed' ||
      streamMessage.status === 'briefs_generated'
    ) {
      addMessage({ type: 'status', content: streamMessage.message });
    }
  };

  /**
   * Stage C stream event handler
   */
  const handleStageCStreamMessage = (streamMessage: import('./types').StreamMessage) => {
    if (streamMessage.status === 'stage_c_completed' && streamMessage.campaign_log) {
      addMessage({
        type: 'campaign_results',
        content: streamMessage.message,
        campaignLogData: streamMessage.campaign_log,
      });
      setIsLoading(false);
    } else if (streamMessage.status === 'error') {
      addMessage({ type: 'error', content: streamMessage.message });
      setIsLoading(false);
    } else if (
      streamMessage.status === 'stage_c_starting' ||
      streamMessage.status === 'progress' ||
      streamMessage.status === 'brief_executing' ||
      streamMessage.status === 'image_generating' ||
      streamMessage.status === 'image_generated' ||
      streamMessage.status === 'discord_posting' ||
      streamMessage.status === 'discord_posted' ||
      streamMessage.status === 'discord_post_failed'
    ) {
      addMessage({ type: 'status', content: streamMessage.message });
    }
  };

  const runPipeline = async (request: ResearchRequest) => {
    try {
      // Save input for Stage B
      setLastReportInput(request as unknown as Record<string, unknown>);

      await researchService.callStageAResearch(
        request,
        handleStreamMessage,
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

  /**
   * Start Stage B: Build strategy from Stage A report
   */
  const handleStartStageB = async (reportData: ResearchReport, mongodbId?: string) => {
    setIsLoading(true);
    try {
      await researchService.callStageBStrategy(
        {
          stage_a_report: reportData as unknown as Record<string, unknown>,
          stage_a_input: lastReportInput || {},
          mongodb_id: mongodbId || lastMongodbId,
        },
        handleStageBStreamMessage,
        (errorMsg) => {
          addMessage({ type: 'error', content: errorMsg });
          setIsLoading(false);
        }
      );
    } catch {
      addMessage({ type: 'error', content: 'Lỗi Stage B không xác định' });
      setIsLoading(false);
    }
  };

  /**
   * Called when user approves all briefs
   */
  const handleBriefsApproveAll = (briefs: ContentBrief[]) => {
    addMessage({
      type: 'assistant',
      content: `✅ Đã duyệt ${briefs.filter(b => b.status === 'approved').length} briefs. Nhấn "Thực Thi" để bắt đầu đăng lên Discord!`,
    });
  };

  /**
   * Called when user clicks "Start Campaign" in the brief editor
   */
  const handleStartCampaign = async (approvedBriefs: ContentBrief[]) => {
    if (approvedBriefs.length === 0) {
      addMessage({ type: 'error', content: 'Không có brief nào được duyệt!' });
      return;
    }

    addMessage({
      type: 'status',
      content: `🚀 Bắt đầu thực thi chiến dịch: ${approvedBriefs.length} bài đăng...`,
    });
    setIsLoading(true);

    // Save approval to backend
    if (lastStrategy) {
      await researchService.approveStageBBriefs({
        mongodb_id: lastMongodbId,
        strategy: lastStrategy as unknown as Record<string, unknown>,
        approved_briefs: approvedBriefs,
      });
    }

    // Run Stage C
    try {
      await researchService.callStageCCampaign(
        {
          approved_briefs: approvedBriefs,
          mongodb_stage_a_id: lastMongodbId,
        },
        handleStageCStreamMessage,
        (errorMsg) => {
          addMessage({ type: 'error', content: errorMsg });
          setIsLoading(false);
        }
      );
    } catch {
      addMessage({ type: 'error', content: 'Lỗi Stage C không xác định' });
      setIsLoading(false);
    }
  };

  /**
   * Called when user submits the marketing form.
   * Calls the dedicated /marketing endpoint that skips intent classification.
   */
  const handleMarketingFormSubmit = async (formData: ResearchRequest) => {
    setWaitingMarketingForm(false);
    setIsLoading(true);
    addMessage({ type: 'status', content: '🚀 Bắt đầu nghiên cứu thị trường...' });

    // Save form data for Stage B
    setLastReportInput(formData as unknown as Record<string, unknown>);

    try {
      await researchService.callMarketingResearch(
        formData,
        handleStreamMessage,
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
    setWaitingMarketingForm(false);
    setInputValue('');
    setLastReportData(null);
    setLastReportInput(null);
    setLastMongodbId(undefined);
    setLastStrategy(null);
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
              onClarificationConfirm={() => {}}
              onMarketingFormSubmit={handleMarketingFormSubmit}
              onBriefsApproveAll={handleBriefsApproveAll}
              onStartCampaign={handleStartCampaign}
            />
          ))}

          {isLoading && !waitingMarketingForm && (
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