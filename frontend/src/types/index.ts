// Conversation History Types
export interface ConversationTurn {
  role: 'user' | 'assistant';
  content: string;
}

// Search Source (from Tavily)
export interface SearchSource {
  title: string;
  url: string;
  snippet: string;
}

// Research Request Types
export interface ResearchRequest {
  user_prompt: string; // Required: user's research requirement
  conversation_history?: ConversationTurn[]; // Recent Q&A pairs for context
  llm_provider?: 'llama' | 'gemini-2.5' | 'gemini-3.1'; // LLM provider selection
  ban_chat_san_pham?: string;
  khach_hang_muc_tieu?: string;
  gia_tri_cot_loi?: string;
  gia_ca_chinh_sach?: string;
}

// Plan Types
export interface Plan {
  research_questions: string[];
  hypotheses: string[];
  steps: string[];
  success_criteria: string[];
}

// Evidence Types
export interface Evidence {
  title: string;
  url: string;
  snippet: string;
  published_date: string | null;
  source_score: number;
}

export interface EvidenceCount {
  raw: number;
  filtered: number;
}

// ReAct Summary Types
export interface IntermediateStep {
  step: number;
  action: "search" | "refine_query" | "summarize";
  query: string;
  result_count: number;
  reason: string;
}

export interface ReactSummary {
  tool_calls: number;
  total_evidence_collected: number;
  intermediate_steps: IntermediateStep[];
}

// Citation Types
export interface Citation {
  title: string;
  url: string;
  snippet: string;
  published_date: string | null;
  source_score: number;
}

// Research Report Types
export interface ResearchReport {
  tong_quan_thi_truong: string;
  phan_tich_doi_thu: string;
  xu_huong_nganh: string;
  phan_khuc_va_insight_khach_hang: string;
  citations: Citation[];
}

// ─── Stage B Types ──────────────────────────────────────────────────

export interface SWOTAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface USPResult {
  usp_statement: string;
  supporting_points: string[];
  competitive_advantage: string;
}

export interface BuyerPersona {
  name: string;
  age_range: string;
  interests: string[];
  pain_points: string[];
  discord_behavior: string;
  preferred_content_types: string[];
  goals: string[];
}

export interface ContentPillar {
  name: string;
  description: string;
  example_topics: string[];
  emoji: string;
}

export interface ScheduleEntry {
  day: number;
  time: string;
  content_type: string;
  pillar_name: string;
}

export interface CampaignPlan {
  duration_days: number;
  posting_frequency: string;
  content_types: string[];
  schedule: ScheduleEntry[];
  campaign_goal: string;
}

export interface ContentBrief {
  id: string;
  title: string;
  caption: string;
  image_prompt: string;
  content_type: string;
  pillar: string;
  scheduled_day: number;
  scheduled_time: string;
  status: 'pending' | 'approved' | 'rejected' | 'edited';
  embed_color: number;
}

export interface StageBOutput {
  swot: SWOTAnalysis;
  usp: USPResult;
  persona: BuyerPersona;
  content_pillars: ContentPillar[];
  campaign_plan: CampaignPlan;
  content_briefs: ContentBrief[];
}

// ─── Stage C Types ──────────────────────────────────────────────────

export interface ExecutionResult {
  brief_id: string;
  brief_title: string;
  status: 'success' | 'failed' | 'skipped' | 'pending' | 'scheduled';
  image_url?: string;
  image_skipped: boolean;
  discord_sent: boolean;
  error?: string;
  scheduled_post_time?: string;
  posted_at?: string;
  created_at: string;
}

export interface CampaignLog {
  campaign_id: string;
  mongodb_stage_a_id?: string;
  results: ExecutionResult[];
  total_briefs: number;
  total_posted: number;
  total_scheduled?: number;
  total_failed: number;
  total_skipped: number;
  execution_mode?: 'immediate' | 'scheduled';
  started_at: string;
  completed_at?: string;
}

export interface ScheduledCampaign {
  campaign_id: string;
  mongodb_stage_a_id?: string;
  total_briefs: number;
  total_posted: number;
  total_scheduled: number;
  total_failed: number;
  status: 'scheduled' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  execution_results?: ExecutionResult[];
}

export interface SchedulerStatus {
  running: boolean;
  pending_briefs: number;
  check_interval: number;
}

// ─── Streaming Response Types ───────────────────────────────────────

export type StreamStatus =
  | "starting"
  | "progress"
  | "clarification_provided"
  | "plan_completed"
  | "react_completed"
  | "evidence_ready"
  | "report_ready"
  | "completed"
  | "chat_response"
  | "knowledge_searching"
  | "knowledge_response"
  | "show_marketing_form"
  // Stage B
  | "stage_b_starting"
  | "swot_completed"
  | "usp_completed"
  | "persona_completed"
  | "pillars_completed"
  | "campaign_plan_completed"
  | "briefs_generated"
  | "stage_b_completed"
  // Stage C - Immediate
  | "stage_c_starting"
  | "brief_executing"
  | "image_generating"
  | "image_generated"
  | "discord_posting"
  | "discord_posted"
  | "discord_post_failed"
  | "stage_c_completed"
  // Stage C - Scheduled
  | "stage_c_schedule_proposal"
  | "error";

export interface ClarificationData {
  detected_info: string;
  questions_for_user: string[];
  clarified_input: ResearchRequest;
  explanations: Record<string, string>;
  auto_proceeding: boolean;
  note: string;
}

export interface StreamMessage {
  status: StreamStatus;
  message: string;
  plan?: Plan;
  react_summary?: ReactSummary;
  evidence?: Evidence[];
  evidence_count?: EvidenceCount;
  report?: ResearchReport;
  markdown_report?: string;
  mongodb_id?: string;
  detected_info?: string;
  questions_for_user?: string[];
  clarified_input?: ResearchRequest;
  explanations?: Record<string, string>;
  auto_proceeding?: boolean;
  note?: string;
  // Knowledge path
  sources?: SearchSource[];
  // Marketing form path
  detected_prompt?: string;
  // Stage B fields
  swot?: SWOTAnalysis;
  usp?: USPResult;
  persona?: BuyerPersona;
  content_pillars?: ContentPillar[];
  campaign_plan?: CampaignPlan;
  content_briefs?: ContentBrief[];
  strategy?: StageBOutput;
  // Stage C fields
  brief_index?: number;
  image_url?: string;
  result?: ExecutionResult;
  campaign_log?: CampaignLog;
}

// ─── Chat Message Types ─────────────────────────────────────────────

export type ChatMessageType =
  | 'user'
  | 'assistant'
  | 'status'
  | 'clarification'
  | 'plan'
  | 'react_summary'
  | 'evidence'
  | 'report'
  | 'error'
  | 'completed'
  | 'knowledge'
  | 'marketing_form'
  | 'research_suggestion'
  | 'stage_b_proposal'
  // Stage B
  | 'strategy'
  | 'content_briefs'
  | 'stage_c_proposal'
  // Stage C
  | 'stage_c_schedule_proposal'
  | 'campaign_results'
  | 'schedule_manager';

export interface ChatMessage {
  id: string;
  type: ChatMessageType;
  content: string;
  timestamp: Date;
  // Typed payload depending on message type
  clarificationData?: ClarificationData;
  planData?: Plan;
  reactSummaryData?: ReactSummary;
  evidenceData?: Evidence[];
  evidenceCountData?: EvidenceCount;
  reportData?: ResearchReport;
  mongodbId?: string;
  // Knowledge path
  knowledgeData?: {
    answer: string;
    sources: SearchSource[];
  };
  // Marketing form path
  marketingFormData?: {
    detected_prompt: string;
  };
  // Research suggestion button
  researchSuggestionData?: {
    buttonText?: string;
  };
  // Stage B proposal
  stageBProposalData?: {
    reportData: ResearchReport;
    mongodbId?: string;
  };
  // Stage B
  strategyData?: StageBOutput;
  contentBriefsData?: ContentBrief[];
  // Stage C proposal
  stageCProposalData?: {
    briefs: ContentBrief[];
  };
  // Stage C scheduled proposal
  stageCScheduleProposalData?: {
    briefs: ContentBrief[];
    mongodbId?: string;
  };
  // Stage C
  campaignLogData?: CampaignLog;
  // Schedule manager
  scheduleManagerData?: {
    campaigns: ScheduledCampaign[];
    status: SchedulerStatus;
  };
}

// UI State Types (kept for compatibility)
export interface UIState {
  isLoading: boolean;
  messages: string[];
  clarification?: ClarificationData;
  plan?: Plan;
  reactSummary?: ReactSummary;
  evidence?: Evidence[];
  evidenceCount?: EvidenceCount;
  report?: ResearchReport;
  markdownReport?: string;
  chatResponse?: string;
  error?: string;
  mongodbId?: string;
}
