import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { ChatMessageBubble, ConversationList, ModelSelector } from './components';
import { ProcessLog, isProcessLogMessage } from './components/ProcessLog';
import AuthPage from './components/AuthPage';
import type { ChatMessage, ResearchRequest, ConversationTurn, ContentBrief, StageBOutput, ResearchReport } from './types';
import { researchService } from './services/researchService';
import { authService } from './services/authService';
import { initializeBackendUrl } from './config';
import './App.css';

let msgIdCounter = 0;
function nextId() {
  return `msg-${++msgIdCounter}-${Date.now()}`;
}

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(authService.isAuthenticated());
  
  // UI state
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('theme') as 'dark' | 'light') || 'dark';
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Conversation state
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [selectedLLMProvider, setSelectedLLMProvider] = useState<'llama' | 'gemini-2.5' | 'gemini-3.1'>('llama');

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'assistant',
      content: 'Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích!',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [waitingMarketingForm, setWaitingMarketingForm] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const messagesSaveBuffer = useRef<ChatMessage[]>([]);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Stage B/C state
  const [, setLastReportData] = useState<ResearchReport | null>(null);
  const lastReportDataRef = useRef<ResearchReport | null>(null);
  const [lastReportInput, setLastReportInput] = useState<Record<string, unknown> | null>(null);
  const [lastMongodbId, setLastMongodbId] = useState<string | undefined>(undefined);
  const [lastStrategy, setLastStrategy] = useState<StageBOutput | null>(null);

  // Initialize backend URL from Firebase on app startup
  useEffect(() => {
    initializeBackendUrl();
  }, []);

  // Theme management
  const toggleTheme = useCallback(() => {
    setTheme(prev => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      return next;
    });
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const userName = authService.getUser()?.name || authService.getUser()?.username || 'User';

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const isAuth = authService.isAuthenticated();
      setIsAuthenticated(isAuth);
    };
    
    checkAuth();
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Auto-save messages (debounced)
  useEffect(() => {
    if (messagesSaveBuffer.current.length === 0 || !currentConversationId) return;

    // Clear existing timeout
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);

    // Set new timeout to save after 3 seconds of inactivity
    saveTimeoutRef.current = setTimeout(async () => {
      if (messagesSaveBuffer.current.length > 0 && currentConversationId) {
        const toSave = messagesSaveBuffer.current;
        messagesSaveBuffer.current = [];
        await researchService.saveMessagesToConversation(currentConversationId, toSave);
      }
    }, 3000);

    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, [chatMessages, currentConversationId]);

  const createNewConversation = async (firstMessage?: string, title?: string) => {
    try {
      const conv = await researchService.createConversation(firstMessage, title);
      if (conv && conv.conversation_id) {
        setCurrentConversationId(conv.conversation_id);
        return conv.conversation_id;
      }
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
    return null;
  };

  const handleCreateNewConversation = () => {
    // Reset UI state
    setChatMessages([
      {
        id: 'welcome',
        type: 'assistant',
        content: 'Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích!',
        timestamp: new Date(),
      },
    ]);
    setInputValue('');
    setLastReportData(null);
    lastReportDataRef.current = null;
    setLastReportInput(null);
    setLastMongodbId(undefined);
    setLastStrategy(null);
    msgIdCounter = 0;
    messagesSaveBuffer.current = [];

    // Just reset ID, don't create in backend yet
    setCurrentConversationId(null);
  };

  const handleLoadConversation = async (conversationId: string) => {
    try {
      const conv = await researchService.getConversation(conversationId);
      if (conv && conv.messages) {
        setCurrentConversationId(conversationId);
        setChatMessages(conv.messages);
        messagesSaveBuffer.current = [];
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  };

  const addMessage = (msg: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMsg: ChatMessage = {
      ...msg,
      id: nextId(),
      timestamp: new Date(),
    };
    setChatMessages((prev) => [...prev, newMsg]);
    // Buffer message for auto-save
    messagesSaveBuffer.current.push(newMsg);
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

    let convId = currentConversationId;
    
    // Create conversation on first message if it doesn't exist
    if (!convId) {
      convId = await createNewConversation(text);
      if (!convId) return;
    }

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
      llm_provider: selectedLLMProvider,
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
      console.log('streamMessage1 for Stage B react_completed:', streamMessage);
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
      console.log('streamMessage1 for Stage B report_ready:', streamMessage);
      addMessage({
        type: 'report',
        content: streamMessage.message,
        reportData: streamMessage.report,
      });
      // Save report data for Stage B (both state and ref for immediate access)
      setLastReportData(streamMessage.report);
      lastReportDataRef.current = streamMessage.report;
    } else if (streamMessage.status === 'completed') {
      addMessage({
        type: 'completed',
        content: streamMessage.message,
        mongodbId: streamMessage.mongodb_id,
      });
      setLastMongodbId(streamMessage.mongodb_id);
      setIsLoading(false);

      // Show Stage B proposal instead of auto-trigger
      // Use ref for immediate access (not state which is async)
      const reportData = streamMessage.report || lastReportDataRef.current;
      console.log('Report data for Stage B streamMessage:', streamMessage);
      console.log('Report data for Stage B lastReportDataRef:', lastReportDataRef.current);
      console.log('Report data for Stage B proposal:', reportData);
      if (reportData) {
        addMessage({
          type: 'stage_b_proposal',
          content: 'Báo cáo nghiên cứu đã hoàn tất! Bạn có muốn lập chiến lược marketing dựa trên kết quả này không?',
          stageBProposalData: {
            reportData: reportData,
            mongodbId: streamMessage.mongodb_id,
          },
        });
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
          content: `${streamMessage.strategy.content_briefs.length} content briefs đã sẵn sàng để review`,
          contentBriefsData: streamMessage.strategy.content_briefs,
        });
      }

      // Show Stage C proposal instead of auto-trigger
      addMessage({
        type: 'stage_c_schedule_proposal',
        content: 'Chiến lược marketing đã hoàn tất! Bạn có muốn thực thi chiến dịch marketing này không?',
        stageCScheduleProposalData: {
          briefs: streamMessage.strategy.content_briefs || [],
          mongodbId: streamMessage.mongodb_id,
        },
      });
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
          llm_provider: selectedLLMProvider,
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
   * Called when user clicks "Lập Chiến Lược Marketing"
   */
  const handleAcceptStageBProposal = async (reportData: ResearchReport, mongodbId?: string) => {
    addMessage({
      type: 'status',
      content: 'Bắt đầu lập chiến lược marketing...',
    });
    setIsLoading(true);
    await handleStartStageB(reportData, mongodbId);
  };

  /**
   * Called when user clicks "Thực Thi Chiến Dịch" from proposal
   */
  const handleAcceptStageCProposal = async (briefs: ContentBrief[]) => {
    if (briefs.length === 0) {
      addMessage({ type: 'error', content: 'Không có brief nào để thực thi!' });
      return;
    }

    addMessage({
      type: 'status',
      content: `Bắt đầu thực thi chiến dịch: ${briefs.length} bài đăng...`,
    });
    setIsLoading(true);

    // Save approval to backend
    if (lastStrategy) {
      await researchService.approveStageBBriefs({
        mongodb_id: lastMongodbId,
        strategy: lastStrategy as unknown as Record<string, unknown>,
        approved_briefs: briefs,
      });
    }

    // Run Stage C
    try {
      await researchService.callStageCCampaign(
        {
          approved_briefs: briefs,
          mongodb_stage_a_id: lastMongodbId,
          llm_provider: selectedLLMProvider,
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
   * Called when user schedules campaign with specific times
   */
  const handleAcceptStageCScheduleProposal = async (briefs: ContentBrief[], scheduledTimes: string[], mongodbId?: string) => {
    if (briefs.length === 0) {
      addMessage({ type: 'error', content: 'Không có brief nào để thực thi!' });
      return;
    }

    if (scheduledTimes.length !== briefs.length) {
      addMessage({ type: 'error', content: 'Số lượng thời gian không khớp với số lượng bài đăng!' });
      return;
    }

    addMessage({
      type: 'status',
      content: `Đang lên lịch chiến dịch: ${briefs.length} bài đăng...`,
    });
    setIsLoading(true);

    // Save approval to backend
    if (lastStrategy) {
      await researchService.approveStageBBriefs({
        mongodb_id: mongodbId || lastMongodbId,
        strategy: lastStrategy as unknown as Record<string, unknown>,
        approved_briefs: briefs,
      });
    }

    // Run Stage C with scheduled mode
    try {
      await researchService.callStageCCampaignScheduled(
        {
          approved_briefs: briefs,
          scheduled_times: scheduledTimes,
          mongodb_stage_a_id: mongodbId || lastMongodbId,
          llm_provider: selectedLLMProvider,
        },
        handleStageCStreamMessage,
        (errorMsg) => {
          addMessage({ type: 'error', content: errorMsg });
          setIsLoading(false);
        }
      );
    } catch {
      addMessage({ type: 'error', content: 'Lỗi lên lịch Stage C không xác định' });
      setIsLoading(false);
    }
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
      content: `Bắt đầu thực thi chiến dịch: ${approvedBriefs.length} bài đăng...`,
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
          llm_provider: selectedLLMProvider,
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
    addMessage({ type: 'status', content: 'Bắt đầu nghiên cứu thị trường...' });

    // Save form data for Stage B
    setLastReportInput(formData as unknown as Record<string, unknown>);

    // Ensure llm_provider is set
    const formDataWithProvider: ResearchRequest = {
      ...formData,
      llm_provider: selectedLLMProvider,
    };

    try {
      await researchService.callMarketingResearch(
        formDataWithProvider,
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
    handleCreateNewConversation();
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentConversationId(null);
    setChatMessages([
      {
        id: 'welcome',
        type: 'assistant',
        content: 'Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích!',
        timestamp: new Date(),
      },
    ]);
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  const showWelcomeHero = chatMessages.length <= 1 && chatMessages[0]?.id === 'welcome';

  const suggestionChips = [
    { icon: '', text: 'Nghiên cứu thị trường trà sữa tại Việt Nam' },
    { icon: '', text: 'Phân tích đối thủ ngành thương mại điện tử' },
    { icon: '', text: 'Xu hướng marketing 2026 cho startup' },
    { icon: '', text: 'Lập chiến lược quảng cáo cho sản phẩm mới' },
  ];

  /**
   * Group consecutive process-log messages (status, plan, react_summary, evidence)
   * into a single ProcessLog segment. Non-process messages stay as individual segments.
   */
  type MessageSegment = {
    type: 'single' | 'process-log';
    key: string;
    messages: ChatMessage[];
  };

  const groupedMessages = useMemo<MessageSegment[]>(() => {
    const segments: MessageSegment[] = [];
    let currentGroup: ChatMessage[] = [];

    const flushGroup = () => {
      if (currentGroup.length > 0) {
        segments.push({
          type: 'process-log',
          key: `plog-${currentGroup[0].id}`,
          messages: [...currentGroup],
        });
        currentGroup = [];
      }
    };

    for (const msg of chatMessages) {
      if (isProcessLogMessage(msg.type)) {
        currentGroup.push(msg);
      } else {
        flushGroup();
        segments.push({
          type: 'single',
          key: msg.id,
          messages: [msg],
        });
      }
    }
    flushGroup();

    return segments;
  }, [chatMessages]);

  return (
    <div className="app-container">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Conversation Sidebar */}
      <aside className={`app-sidebar ${sidebarOpen ? 'is-open' : ''}`}>
        <ConversationList
          onSelectConversation={(id) => { handleLoadConversation(id); setSidebarOpen(false); }}
          onCreateNew={() => { handleCreateNewConversation(); setSidebarOpen(false); }}
          currentConversationId={currentConversationId || undefined}
        />
      </aside>

      {/* Main Content */}
      <div className="app-main">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            <button className="header-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)} title="Menu">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>
            <div className="header-content">
              <h1>MarketMind AI</h1>
              <p>Trợ lý nghiên cứu thị trường thông minh</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="header-icon-btn" onClick={toggleTheme} title={theme === 'dark' ? 'Light mode' : 'Dark mode'}>
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <button className="header-reset" onClick={handleReset} title="Cuộc hội thoại mới">
              Mới
            </button>
            <div className="header-user">
              <span className="header-user-name">{userName}</span>
              <button className="header-logout" onClick={handleLogout} title="Đăng xuất">
                Đăng xuất
              </button>
            </div>
          </div>
        </header>

        {/* Chat area */}
        <main className="chat-area">
          {/* Top loading progress bar */}
          {isLoading && (
            <div className="loading-progress-bar">
              <div className="loading-progress-bar-fill" />
            </div>
          )}
          <div className="chat-messages">
            {/* Welcome Hero */}
            {showWelcomeHero && (
              <div className="welcome-hero">
                <h2 className="welcome-hero-title">Chào mừng đến với MarketMind AI</h2>
                <p className="welcome-hero-desc">
                  Trợ lý AI giúp bạn nghiên cứu thị trường, phân tích đối thủ, và xây dựng chiến lược marketing — tất cả chỉ bằng một cuộc trò chuyện.
                </p>
                <div className="welcome-features">
                  <div className="welcome-feature">
                    <div><strong>Nghiên cứu thị trường</strong><br/>Phân tích sâu từ dữ liệu thực tế</div>
                  </div>
                  <div className="welcome-feature">
                    <div><strong>Chiến lược marketing</strong><br/>Tự động lập kế hoạch chi tiết</div>
                  </div>
                  <div className="welcome-feature">
                    <div><strong>Thực thi chiến dịch</strong><br/>Đăng bài tự động lên Discord</div>
                  </div>
                </div>
                <p className="welcome-hero-hint">Thử hỏi một trong các câu gợi ý bên dưới</p>
                <div className="suggestion-chips">
                  {suggestionChips.map((chip, i) => (
                    <button
                      key={i}
                      className="suggestion-chip"
                      onClick={() => handleSend(chip.text)}
                    >
                      {chip.text}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {!showWelcomeHero && groupedMessages.map((segment) => {
              if (segment.type === 'process-log') {
                return (
                  <ProcessLog
                    key={segment.key}
                    messages={segment.messages}
                    isLoading={isLoading}
                    onClarificationConfirm={() => {}}
                    onMarketingFormSubmit={handleMarketingFormSubmit}
                    onStartCampaign={handleStartCampaign}
                    onAcceptStageBProposal={handleAcceptStageBProposal}
                    onAcceptStageCProposal={handleAcceptStageCProposal}
                    onAcceptStageCScheduleProposal={handleAcceptStageCScheduleProposal}
                  />
                );
              }
              return (
                <ChatMessageBubble
                  key={segment.messages[0].id}
                  message={segment.messages[0]}
                  isLoading={isLoading}
                  onClarificationConfirm={() => {}}
                  onMarketingFormSubmit={handleMarketingFormSubmit}
                  onStartCampaign={handleStartCampaign}
                  onAcceptStageBProposal={handleAcceptStageBProposal}
                  onAcceptStageCProposal={handleAcceptStageCProposal}
                  onAcceptStageCScheduleProposal={handleAcceptStageCScheduleProposal}
                />
              );
            })}

            {isLoading && !waitingMarketingForm && (
              <div className="chat-row chat-row--assistant">
                <div className="chat-avatar chat-avatar--assistant">AI</div>
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
        <div className={`input-bar-inner ${isLoading ? 'is-loading' : ''}`}>
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? 'Đang xử lý yêu cầu...' : 'Nhập yêu cầu nghiên cứu của bạn...'}
            disabled={isLoading}
            rows={1}
          />
          <button
            className={`send-btn ${isLoading ? 'is-loading' : ''}`}
            onClick={() => handleSend()}
            disabled={isLoading || !inputValue.trim()}
            title={isLoading ? 'Processing...' : 'Send'}
          >
            {isLoading ? (
              <span className="send-btn-spinner" />
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>
        <div className="input-footer">
          <small className="input-hint">
            {isLoading ? (
              <span className="input-loading-hint">
                <span className="input-loading-spinner" />
                Processing your request...
              </span>
            ) : (
              <>Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line</>
            )}
          </small>
          <ModelSelector
            currentProvider={selectedLLMProvider}
            onProviderChange={setSelectedLLMProvider}
          />
        </div>
      </footer>
      </div>
    </div>
  );
}

export default App;