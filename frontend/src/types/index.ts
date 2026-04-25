// Research Request Types
export interface ResearchRequest {
  user_prompt: string; // Required: user's research requirement
  nganh_hang?: string;
  thi_truong_muc_tieu?: string;
  phan_khuc_quan_tam?: string[];
  doi_thu_seed?: string[];
  khung_thoi_gian?: string;
  muc_tieu_nghien_cuu?: string[];
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

// Streaming Response Types
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
}

// UI State Types
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
