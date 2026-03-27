// Research Request Types
export interface ResearchRequest {
  nganh_hang: string;
  thi_truong_muc_tieu: string;
  phan_khuc_quan_tam?: string[];
  doi_thu_seed?: string[];
  khung_thoi_gian?: string;
  muc_tieu_nghien_cuu?: string[];
}

// Streaming Response Types
export type StreamStatus = "starting" | "progress" | "completed" | "error";

export interface StreamMessage {
  status: StreamStatus;
  message: string;
  plan_summary?: Record<string, unknown>;
  mongodb_id?: string;
  report?: ResearchReport;
}

// Research Report Types
export interface Citation {
  title: string;
  url: string;
  snippet: string;
  published_date: string;
  source_score: number;
}

export interface ResearchReport {
  tong_quan_thi_truong: string;
  phan_tich_doi_thu: string;
  xu_huong_nganh: string;
  phan_khuc_va_insight_khach_hang: string;
  citations: Citation[];
}

// UI State Types
export interface UIState {
  isLoading: boolean;
  messages: string[];
  report?: ResearchReport;
  error?: string;
  mongodbId?: string;
}
