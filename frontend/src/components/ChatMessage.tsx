import { useState, useEffect, useCallback } from 'react';
import type { ChatMessage, ResearchRequest, ClarificationData, SearchSource, ContentBrief, ResearchReport } from '../types';
import { parseMarkdown, renderMarkdown } from '../utils/markdownParser';
import { CollapsibleCard } from './CollapsibleCard';
import { StrategyBubble } from './StrategyBubble';
import { ContentBriefEditor } from './ContentBriefEditor';
import { CampaignResultsBubble } from './CampaignResultsBubble';
import { ScheduleEditor } from './ScheduleEditor';
import { ScheduleManager } from './ScheduleManager';

interface ChatMessageProps {
  message: ChatMessage;
  isLoading?: boolean;
  onClarificationConfirm?: (overrides: Partial<ResearchRequest>) => void;
  onMarketingFormSubmit?: (formData: ResearchRequest) => void;
  onStartCampaign?: (approvedBriefs: ContentBrief[]) => void;
  onAcceptStageBProposal?: (reportData: ResearchReport, mongodbId?: string) => void;
  onAcceptStageCProposal?: (briefs: ContentBrief[]) => void;
  onAcceptStageCScheduleProposal?: (briefs: ContentBrief[], times: string[], mongodbId?: string) => void;
}

export function ChatMessageBubble({ message, isLoading, onClarificationConfirm, onMarketingFormSubmit, onStartCampaign, onAcceptStageBProposal, onAcceptStageCProposal, onAcceptStageCScheduleProposal }: ChatMessageProps) {
  switch (message.type) {
    case 'user':
      return <UserBubble content={message.content} />;
    case 'assistant':
      return <AssistantBubble content={message.content} />;
    case 'status':
      return <StatusMessage content={message.content} />;
    case 'knowledge':
      return <KnowledgeBubble content={message.content} sources={message.knowledgeData?.sources || []} />;
    case 'marketing_form':
      return (
        <MarketingFormBubble
          content={message.content}
          detectedPrompt={message.marketingFormData?.detected_prompt || ''}
          isLoading={isLoading}
          onSubmit={onMarketingFormSubmit}
        />
      );
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
    // Stage B
    case 'strategy':
      return message.strategyData ? <StrategyBubble data={message.strategyData} /> : <StatusMessage content={message.content} />;
    case 'content_briefs':
      return message.contentBriefsData ? (
        <ContentBriefEditor
          briefs={message.contentBriefsData}
          isLoading={isLoading}
          onStartCampaign={onStartCampaign}
        />
      ) : <StatusMessage content={message.content} />;
    // Stage B Proposal
    case 'stage_b_proposal':
      return (
        <StageBProposalBubble
          content={message.content}
          reportData={message.stageBProposalData?.reportData}
          mongodbId={message.stageBProposalData?.mongodbId}
          onAccept={onAcceptStageBProposal}
        />
      );
    // Stage C Proposal
    case 'stage_c_proposal':
      return (
        <StageCProposalBubble
          content={message.content}
          briefs={message.stageCProposalData?.briefs || []}
          onAccept={onAcceptStageCProposal}
        />
      );
    // Stage C Scheduled Proposal
    case 'stage_c_schedule_proposal':
      return (
        <StageCScheduleProposalBubble
          content={message.content}
          briefs={message.stageCScheduleProposalData?.briefs || []}
          mongodbId={message.stageCScheduleProposalData?.mongodbId}
          isLoading={isLoading}
          onAccept={onAcceptStageCScheduleProposal}
        />
      );
    // Stage C
    case 'campaign_results':
      return message.campaignLogData ? <CampaignResultsBubble data={message.campaignLogData} /> : <StatusMessage content={message.content} />;
    // Schedule Manager
    case 'schedule_manager':
      return <ScheduleManagerBubble />;
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

  // Provide safe defaults and convert objects to strings
  const questions = (data?.questions_for_user || []).map(q =>
    typeof q === 'string' ? q : JSON.stringify(q)
  );

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📋</div>
      <div className="chat-bubble chat-bubble--clarification">
        <div className="clarify-detected">
          <span className="clarify-badge">✅ Phát hiện</span>
          <p>{typeof data.detected_info === 'object' ? JSON.stringify(data.detected_info) : String(data.detected_info || '')}</p>
        </div>

        {questions.length > 0 && (
          <div className="clarify-questions">
            <span className="clarify-badge clarify-badge--warn">❓ Câu hỏi</span>
            {questions.map((q, i) => (
              <p key={i} className="clarify-q">• {q}</p>
            ))}
          </div>
        )}

        <div className="clarify-fields">
          <div className="clarify-field">
            <label>Bản chất sản phẩm</label>
            <textarea
              defaultValue={data.clarified_input.ban_chat_san_pham}
              onChange={(e) => handleChange('ban_chat_san_pham', e.target.value)}
              rows={4}
              placeholder={"- Tên sản phẩm, danh mục, mô tả ngắn gọn (nó là gì? dùng để làm gì?)\n- Tính năng nổi bật và lợi ích thực tế mang lại cho người dùng\n- Điểm khác biệt so với các sản phẩm cùng loại (USP)"}
            />
            {data.explanations?.ban_chat_san_pham && (
              <small>💡 {data.explanations.ban_chat_san_pham}</small>
            )}
          </div>
          <div className="clarify-field">
            <label>Khách hàng mục tiêu</label>
            <textarea
              defaultValue={data.clarified_input.khach_hang_muc_tieu}
              onChange={(e) => handleChange('khach_hang_muc_tieu', e.target.value)}
              rows={4}
              placeholder={"- Họ là ai? (độ tuổi, giới tính, nghề nghiệp, khu vực địa lý...)\n- Nhu cầu hoặc mong muốn họ đang gặp phải\n- Thói quen tiêu dùng và kênh thông tin họ thường tiếp cận"}
            />
            {data.explanations?.khach_hang_muc_tieu && (
              <small>💡 {data.explanations.khach_hang_muc_tieu}</small>
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
  // Provide defaults for potentially undefined arrays
  const research_questions = (data?.research_questions || []).map(item =>
    typeof item === 'string' ? item : JSON.stringify(item)
  );
  const hypotheses = (data?.hypotheses || []).map(item =>
    typeof item === 'string' ? item : JSON.stringify(item)
  );
  const steps = (data?.steps || []).map(item =>
    typeof item === 'string' ? item : JSON.stringify(item)
  );
  const success_criteria = (data?.success_criteria || []).map(item =>
    typeof item === 'string' ? item : JSON.stringify(item)
  );

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
              <ul>{research_questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
            </div>
            <div className="plan-group">
              <h4>Giả Thuyết</h4>
              <ul>{hypotheses.map((h, i) => <li key={i}>{h}</li>)}</ul>
            </div>
            <div className="plan-group">
              <h4>Các Bước Thực Hiện</h4>
              <ol>{steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
            </div>
            <div className="plan-group">
              <h4>Tiêu Chí Thành Công</h4>
              <ul>{success_criteria.map((c, i) => <li key={i}>{c}</li>)}</ul>
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
  const evidenceData = data || [];
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
            {evidenceData.map((item, i) => (
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
  // Provide safe defaults
  const tong_quan = data?.tong_quan_thi_truong || '';
  const phan_tich = data?.phan_tich_doi_thu || '';
  const xu_huong = data?.xu_huong_nganh || '';
  const phan_khuc = data?.phan_khuc_va_insight_khach_hang || '';
  const citations = data?.citations || [];
  
  // Truncate to ~120 chars for preview
  const preview = tong_quan.slice(0, 120) + (tong_quan.length > 120 ? '…' : '');

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
              <div className="report-text">
                {renderMarkdown(parseMarkdown(tong_quan))}
              </div>
            </section>

            <section className="report-section-inner">
              <h4>🎯 Phân Tích Đối Thủ</h4>
              <div className="report-text">
                {renderMarkdown(parseMarkdown(phan_tich))}
              </div>
            </section>

            <section className="report-section-inner">
              <h4>📈 Xu Hướng Ngành</h4>
              <div className="report-text">
                {renderMarkdown(parseMarkdown(xu_huong))}
              </div>
            </section>

            <section className="report-section-inner">
              <h4>👥 Phân Khúc & Insight</h4>
              <div className="report-text">
                {renderMarkdown(parseMarkdown(phan_khuc))}
              </div>
            </section>

            {citations && citations.length > 0 && (
              <section className="report-section-inner">
                <h4>📚 Nguồn Tham Khảo ({citations.length})</h4>
                <div className="citations-grid">
                  {citations.map((c, i) => (
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

/* ────── Knowledge Bubble ────── */
function KnowledgeBubble({ content, sources }: { content: string; sources: SearchSource[] }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🧠</div>
      <div className="chat-bubble chat-bubble--knowledge">
        <div className="knowledge-answer">
          {content.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
        {sources.length > 0 && (
          <CollapsibleCard
            title={`Nguồn tham khảo (${sources.length})`}
            summary="Nhấn để xem các nguồn đã sử dụng"
            icon="🔗"
            accentColor="var(--accent-knowledge, #8b5cf6)"
          >
            <div className="knowledge-sources">
              {sources.map((src, i) => (
                <div key={i} className="knowledge-source-item">
                  <a href={src.url} target="_blank" rel="noopener noreferrer">
                    {src.title || src.url}
                  </a>
                  {src.snippet && <p className="knowledge-source-snippet">{src.snippet}</p>}
                </div>
              ))}
            </div>
          </CollapsibleCard>
        )}
      </div>
    </div>
  );
}

/* ────── Marketing Form Bubble ────── */
function MarketingFormBubble({
  content,
  detectedPrompt,
  isLoading,
  onSubmit,
}: {
  content: string;
  detectedPrompt: string;
  isLoading?: boolean;
  onSubmit?: (formData: ResearchRequest) => void;
}) {
  const [formData, setFormData] = useState({
    user_prompt: detectedPrompt,
    ban_chat_san_pham: '',
    khach_hang_muc_tieu: '',
    gia_tri_cot_loi: '',
    gia_ca_chinh_sach: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    if (!onSubmit) return;
    onSubmit({
      user_prompt: formData.user_prompt,
      ban_chat_san_pham: formData.ban_chat_san_pham || undefined,
      khach_hang_muc_tieu: formData.khach_hang_muc_tieu || undefined,
      gia_tri_cot_loi: formData.gia_tri_cot_loi || undefined,
      gia_ca_chinh_sach: formData.gia_ca_chinh_sach || undefined,
    });
  };

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📊</div>
      <div className="chat-bubble chat-bubble--marketing-form">
        <div className="mkt-form-header">
          <span className="mkt-form-badge">📋 Nghiên cứu thị trường</span>
          <p>{content}</p>
        </div>

        <div className="mkt-form-fields">
          <div className="mkt-form-field">
            <label>Yêu cầu nghiên cứu</label>
            <textarea
              value={formData.user_prompt}
              onChange={(e) => handleChange('user_prompt', e.target.value)}
              rows={2}
              placeholder="Mô tả yêu cầu nghiên cứu..."
            />
          </div>

          <div className="mkt-form-field">
            <label>Bản chất sản phẩm</label>
            <textarea
              value={formData.ban_chat_san_pham}
              onChange={(e) => handleChange('ban_chat_san_pham', e.target.value)}
              rows={4}
              placeholder={"- Tên sản phẩm, danh mục, mô tả ngắn gọn (nó là gì? dùng để làm gì?)\n- Tính năng nổi bật và lợi ích thực tế mang lại cho người dùng\n- Điểm khác biệt so với các sản phẩm cùng loại (USP)"}
            />
          </div>

          <div className="mkt-form-field">
            <label>Khách hàng mục tiêu</label>
            <textarea
              value={formData.khach_hang_muc_tieu}
              onChange={(e) => handleChange('khach_hang_muc_tieu', e.target.value)}
              rows={4}
              placeholder={"- Họ là ai? (độ tuổi, giới tính, nghề nghiệp, khu vực địa lý...)\n- Nhu cầu, nỗi đau (pain points) hoặc mong muốn họ đang gặp phải\n- Thói quen tiêu dùng và kênh thông tin họ thường tiếp cận"}
            />
          </div>

          <div className="mkt-form-field">
            <label>Giá trị cốt lõi & Lý do mua hàng</label>
            <textarea
              value={formData.gia_tri_cot_loi}
              onChange={(e) => handleChange('gia_tri_cot_loi', e.target.value)}
              rows={4}
              placeholder={"- Sản phẩm giải quyết vấn đề gì mà đối thủ chưa làm tốt?\n- Lợi ích cảm xúc hoặc lý tính khách hàng nhận được\n- Bằng chứng xã hội (review, chứng nhận, case study...) nếu có"}
            />
          </div>

          <div className="mkt-form-field">
            <label>Giá cả & Chính sách</label>
            <textarea
              value={formData.gia_ca_chinh_sach}
              onChange={(e) => handleChange('gia_ca_chinh_sach', e.target.value)}
              rows={4}
              placeholder={"- Mức giá bán, phương thức thanh toán\n- Chính sách bảo hành, đổi trả, khuyến mãi\n- Giá trị cảm nhận so với giá tiền (value for money)"}
            />
          </div>
        </div>

        <button
          className="mkt-form-submit"
          onClick={handleSubmit}
          disabled={isLoading || !formData.user_prompt.trim()}
        >
          🚀 Bắt Đầu Nghiên Cứu
        </button>
      </div>
    </div>
  );
}

/* ────── Stage B Proposal Bubble ────── */
function StageBProposalBubble({
  content,
  reportData,
  mongodbId,
  onAccept,
}: {
  content: string;
  reportData?: ResearchReport;
  mongodbId?: string;
  onAccept?: (reportData: ResearchReport, mongodbId?: string) => void;
}) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📊</div>
      <div className="chat-bubble chat-bubble--proposal">
        <p>{content}</p>
        <div className="proposal-actions">
          <button
            className="proposal-btn proposal-btn--accept"
            onClick={() => reportData && onAccept?.(reportData, mongodbId)}
          >
            ✅ Lập Chiến Lược Marketing
          </button>
          <button className="proposal-btn proposal-btn--decline">❌ Không, cảm ơn</button>
        </div>
      </div>
    </div>
  );
}

/* ────── Stage C Proposal Bubble ────── */
function StageCProposalBubble({
  content,
  briefs,
  onAccept,
}: {
  content: string;
  briefs: ContentBrief[];
  onAccept?: (briefs: ContentBrief[]) => void;
}) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🎯</div>
      <div className="chat-bubble chat-bubble--proposal">
        <p>{content}</p>
        <div className="proposal-actions">
          <button
            className="proposal-btn proposal-btn--accept"
            onClick={() => onAccept?.(briefs)}
          >
            🚀 Thực Thi Chiến Dịch
          </button>
          <button className="proposal-btn proposal-btn--decline">❌ Chỉnh Sửa Trước</button>
        </div>
      </div>
    </div>
  );
}

/* ────── Stage C Scheduled Proposal Bubble ────── */
function StageCScheduleProposalBubble({
  content,
  briefs,
  mongodbId,
  isLoading,
  onAccept,
}: {
  content: string;
  briefs: ContentBrief[];
  mongodbId?: string;
  isLoading?: boolean;
  onAccept?: (briefs: ContentBrief[], times: string[], mongodbId?: string) => void;
}) {
  const [showScheduler, setShowScheduler] = useState(false);

  const handleSchedule = (times: string[]) => {
    onAccept?.(briefs, times, mongodbId);
    setShowScheduler(false);
  };

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📅</div>
      <div className="chat-bubble chat-bubble--proposal">
        <p>{content}</p>
        {!showScheduler && (
          <div className="proposal-actions">
            <button
              className="proposal-btn proposal-btn--accept"
              onClick={() => setShowScheduler(true)}
              disabled={isLoading}
            >
              📅 Lên Lịch
            </button>
            <button className="proposal-btn proposal-btn--decline">❌ Hủy</button>
          </div>
        )}
        {showScheduler && (
          <ScheduleEditor
            briefs={briefs}
            onSchedule={handleSchedule}
            onCancel={() => setShowScheduler(false)}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
}

/* ────── Schedule Manager Bubble ────── */
function ScheduleManagerBubble() {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📊</div>
      <div className="chat-bubble chat-bubble--card">
        <ScheduleManager />
      </div>
    </div>
  );
}
