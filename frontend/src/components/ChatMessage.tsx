import { useState, useEffect, useCallback } from 'react';
import type { ChatMessage, ResearchRequest, ClarificationData } from '../types';
import { CollapsibleCard } from './CollapsibleCard';

interface ChatMessageProps {
  message: ChatMessage;
  isLoading?: boolean;
  onClarificationConfirm?: (overrides: Partial<ResearchRequest>) => void;
}

export function ChatMessageBubble({ message, isLoading, onClarificationConfirm }: ChatMessageProps) {
  switch (message.type) {
    case 'user':
      return <UserBubble content={message.content} />;
    case 'assistant':
      return <AssistantBubble content={message.content} />;
    case 'status':
      return <StatusMessage content={message.content} />;
    case 'clarification':
      return (
        <ClarificationBubble
          data={message.clarificationData!}
          isLoading={isLoading}
          onConfirm={onClarificationConfirm}
        />
      );
    case 'plan':
      return <PlanBubble data={message.planData!} content={message.content} />;
    case 'react_summary':
      return <ReactSummaryBubble data={message.reactSummaryData!} content={message.content} />;
    case 'evidence':
      return (
        <EvidenceBubble
          data={message.evidenceData!}
          count={message.evidenceCountData}
          content={message.content}
        />
      );
    case 'report':
      return <ReportBubble data={message.reportData!} mongodbId={message.mongodbId} />;
    case 'error':
      return <ErrorBubble content={message.content} />;
    case 'completed':
      return <CompletedBubble content={message.content} mongodbId={message.mongodbId} />;
    default:
      return <StatusMessage content={message.content} />;
  }
}

/* ────── User Bubble ────── */
function UserBubble({ content }: { content: string }) {
  return (
    <div className="chat-row chat-row--user">
      <div className="chat-bubble chat-bubble--user">
        <p>{content}</p>
      </div>
      <div className="chat-avatar chat-avatar--user">👤</div>
    </div>
  );
}

/* ────── Assistant Bubble ────── */
function AssistantBubble({ content }: { content: string }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🤖</div>
      <div className="chat-bubble chat-bubble--assistant">
        <p>{content}</p>
      </div>
    </div>
  );
}

/* ────── Status Message ────── */
function StatusMessage({ content }: { content: string }) {
  return (
    <div className="chat-row chat-row--status">
      <div className="chat-status">
        <span className="status-dot" />
        <span>{content}</span>
      </div>
    </div>
  );
}

/* ────── Error Bubble ────── */
function ErrorBubble({ content }: { content: string }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">⚠️</div>
      <div className="chat-bubble chat-bubble--error">
        <p>❌ {content}</p>
      </div>
    </div>
  );
}

/* ────── Completed Bubble ────── */
function CompletedBubble({ content, mongodbId }: { content: string; mongodbId?: string }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">✅</div>
      <div className="chat-bubble chat-bubble--completed">
        <p>{content}</p>
        {mongodbId && (
          <span className="completed-id">ID: {mongodbId}</span>
        )}
      </div>
    </div>
  );
}

/* ────── Clarification Bubble ────── */
function ClarificationBubble({
  data,
  isLoading,
  onConfirm,
}: {
  data: ClarificationData;
  isLoading?: boolean;
  onConfirm?: (overrides: Partial<ResearchRequest>) => void;
}) {
  const [overrides, setOverrides] = useState<Partial<ResearchRequest>>({});
  const [countdown, setCountdown] = useState(data.auto_proceeding ? 5 : 0);

  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  const handleConfirm = useCallback(() => {
    if (onConfirm) {
      onConfirm({ ...data.clarified_input, ...overrides });
    }
  }, [onConfirm, data.clarified_input, overrides]);

  useEffect(() => {
    if (countdown === 1 && onConfirm) handleConfirm();
  }, [countdown, handleConfirm, onConfirm]);

  const handleChange = (field: keyof ResearchRequest, value: string) => {
    setOverrides((p) => ({ ...p, [field]: value }));
  };

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📋</div>
      <div className="chat-bubble chat-bubble--clarification">
        <div className="clarify-detected">
          <span className="clarify-badge">✅ Phát hiện</span>
          <p>{typeof data.detected_info === 'object' ? JSON.stringify(data.detected_info) : String(data.detected_info || '')}</p>
        </div>

        {data.questions_for_user.length > 0 && (
          <div className="clarify-questions">
            <span className="clarify-badge clarify-badge--warn">❓ Câu hỏi</span>
            {data.questions_for_user.map((q, i) => (
              <p key={i} className="clarify-q">• {q}</p>
            ))}
          </div>
        )}

        <div className="clarify-fields">
          <div className="clarify-field">
            <label>Ngành hàng</label>
            <input
              type="text"
              defaultValue={data.clarified_input.nganh_hang}
              onChange={(e) => handleChange('nganh_hang', e.target.value)}
            />
            {data.explanations?.nganh_hang && (
              <small>💡 {data.explanations.nganh_hang}</small>
            )}
          </div>
          <div className="clarify-field">
            <label>Thị trường mục tiêu</label>
            <input
              type="text"
              defaultValue={data.clarified_input.thi_truong_muc_tieu}
              onChange={(e) => handleChange('thi_truong_muc_tieu', e.target.value)}
            />
            {data.explanations?.thi_truong_muc_tieu && (
              <small>💡 {data.explanations.thi_truong_muc_tieu}</small>
            )}
          </div>
        </div>

        <button
          className="clarify-confirm-btn"
          onClick={handleConfirm}
          disabled={isLoading || countdown > 0}
        >
          {countdown > 0
            ? `⏱️ Tự động tiếp tục trong ${countdown}s...`
            : '✅ Xác Nhận & Tiếp Tục'}
        </button>

        {data.note && <small className="clarify-note">{data.note}</small>}
      </div>
    </div>
  );
}

/* ────── Plan Bubble ────── */
function PlanBubble({ data, content }: { data: import('../types').Plan; content: string }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📋</div>
      <div className="chat-bubble chat-bubble--card">
        <CollapsibleCard
          title="Kế Hoạch Nghiên Cứu"
          summary={content}
          icon="📋"
          accentColor="var(--accent-plan)"
        >
          <div className="plan-detail">
            <div className="plan-group">
              <h4>Câu Hỏi Nghiên Cứu</h4>
              <ul>{data.research_questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
            </div>
            <div className="plan-group">
              <h4>Giả Thuyết</h4>
              <ul>{data.hypotheses.map((h, i) => <li key={i}>{h}</li>)}</ul>
            </div>
            <div className="plan-group">
              <h4>Các Bước Thực Hiện</h4>
              <ol>{data.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
            </div>
            <div className="plan-group">
              <h4>Tiêu Chí Thành Công</h4>
              <ul>{data.success_criteria.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}

/* ────── React Summary Bubble ────── */
function ReactSummaryBubble({ data, content }: { data: import('../types').ReactSummary; content: string }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🔍</div>
      <div className="chat-bubble chat-bubble--card">
        <CollapsibleCard
          title="Quá Trình Thu Thập Dữ Liệu"
          summary={content}
          icon="🔍"
          accentColor="var(--accent-react)"
        >
          <div className="react-detail">
            <div className="react-stats-grid">
              <div className="react-stat">
                <span className="react-stat-num">{data.tool_calls}</span>
                <span className="react-stat-label">Lần tìm kiếm</span>
              </div>
              <div className="react-stat">
                <span className="react-stat-num">{data.total_evidence_collected}</span>
                <span className="react-stat-label">Dữ liệu thu được</span>
              </div>
            </div>
            {data.intermediate_steps && data.intermediate_steps.length > 0 && (
              <div className="react-steps">
                {data.intermediate_steps.map((step, i) => (
                  <div key={i} className="react-step-item">
                    <strong>Bước {step.step}:</strong> {step.action}
                    <br />
                    <span className="react-step-meta">
                      Truy vấn: {step.query} | Kết quả: {step.result_count}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}

/* ────── Evidence Bubble ────── */
function EvidenceBubble({
  data,
  count,
  content,
}: {
  data: import('../types').Evidence[];
  count?: import('../types').EvidenceCount;
  content: string;
}) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📚</div>
      <div className="chat-bubble chat-bubble--card">
        <CollapsibleCard
          title="Nguồn Dữ Liệu Thu Thập"
          summary={count ? `${count.filtered} hợp lệ / ${count.raw} tổng — ${content}` : content}
          icon="📚"
          accentColor="var(--accent-evidence)"
        >
          <div className="evidence-detail">
            {data.map((item, i) => (
              <div key={i} className="ev-item">
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  {item.title}
                </a>
                <p className="ev-snippet">{item.snippet}</p>
                <div className="ev-meta">
                  {item.published_date && <span>📅 {item.published_date}</span>}
                  <span>⭐ {(item.source_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}

/* ────── Report Bubble ────── */
function ReportBubble({
  data,
  mongodbId,
}: {
  data: import('../types').ResearchReport;
  mongodbId?: string;
}) {
  // Truncate to ~120 chars for preview
  const preview = data.tong_quan_thi_truong?.slice(0, 120) + '…';

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📊</div>
      <div className="chat-bubble chat-bubble--card">
        <CollapsibleCard
          title="Báo Cáo Nghiên Cứu Thị Trường"
          summary={preview}
          icon="📊"
          accentColor="var(--accent-report)"
        >
          <div className="report-detail">
            {mongodbId && (
              <div className="report-id-badge">ID: {mongodbId}</div>
            )}

            <section className="report-section-inner">
              <h4>📊 Tổng Quan Thị Trường</h4>
              <div className="report-text">{data.tong_quan_thi_truong}</div>
            </section>

            <section className="report-section-inner">
              <h4>🎯 Phân Tích Đối Thủ</h4>
              <div className="report-text">{data.phan_tich_doi_thu}</div>
            </section>

            <section className="report-section-inner">
              <h4>📈 Xu Hướng Ngành</h4>
              <div className="report-text">{data.xu_huong_nganh}</div>
            </section>

            <section className="report-section-inner">
              <h4>👥 Phân Khúc & Insight</h4>
              <div className="report-text">{data.phan_khuc_va_insight_khach_hang}</div>
            </section>

            {data.citations && data.citations.length > 0 && (
              <section className="report-section-inner">
                <h4>📚 Nguồn Tham Khảo ({data.citations.length})</h4>
                <div className="citations-grid">
                  {data.citations.map((c, i) => (
                    <div key={i} className="cite-card">
                      <a href={c.url} target="_blank" rel="noopener noreferrer">{c.title}</a>
                      <p>{c.snippet}</p>
                      <div className="cite-meta">
                        {c.published_date && <span>📅 {c.published_date}</span>}
                        <span>⭐ {(c.source_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}
