import { useState, useEffect } from 'react';
import type { ContentBrief } from '../types';
import { apiKeyService, decryptValue } from '../services/apiKeyService';

interface ContentBriefEditorProps {
  briefs: ContentBrief[];
  isLoading?: boolean;
  onApproveAll?: (briefs: ContentBrief[]) => void;
  onStartCampaign?: (approvedBriefs: ContentBrief[], webhookUrl?: string) => void;
}

export function ContentBriefEditor({
  briefs: initialBriefs,
  isLoading,
  onApproveAll,
  onStartCampaign,
}: ContentBriefEditorProps) {
  const [briefs, setBriefs] = useState<ContentBrief[]>(
    initialBriefs.map((b) => ({ ...b }))
  );
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [webhooks, setWebhooks] = useState<import('../services/apiKeyService').DiscordWebhook[]>([]);
  const [selectedWebhookId, setSelectedWebhookId] = useState('default');
  const [loadingWebhooks, setLoadingWebhooks] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoadingWebhooks(true);
      const whs = await apiKeyService.getDiscordWebhooks();
      setWebhooks(whs);
      setLoadingWebhooks(false);
    };
    load();
  }, []);

  const updateBrief = (id: string, updates: Partial<ContentBrief>) => {
    setBriefs((prev) =>
      prev.map((b) => (b.id === id ? { ...b, ...updates } : b))
    );
  };

  const handleApprove = (id: string) => {
    updateBrief(id, { status: 'approved' });
  };

  const handleReject = (id: string) => {
    updateBrief(id, { status: 'rejected' });
  };

  const handleEdit = (id: string) => {
    setEditingId(editingId === id ? null : id);
    if (editingId !== id) {
      updateBrief(id, { status: 'edited' });
    }
  };

  const handleApproveAll = () => {
    const updated = briefs.map((b) =>
      b.status !== 'rejected' ? { ...b, status: 'approved' as const } : b
    );
    setBriefs(updated);
    onApproveAll?.(updated);
  };

  const handleStartCampaign = async () => {
    const approved = briefs.filter(
      (b) => b.status === 'approved' || b.status === 'edited'
    );
    let webhookUrl: string | undefined;
    if (selectedWebhookId !== 'default') {
      const selected = webhooks.find(w => w.id === selectedWebhookId);
      if (selected?.url_encrypted) {
        webhookUrl = await decryptValue(selected.url_encrypted);
      }
    }
    onStartCampaign?.(approved, webhookUrl);
  };

  const approvedCount = briefs.filter(
    (b) => b.status === 'approved' || b.status === 'edited'
  ).length;

  const statusConfig: Record<string, { emoji: string; label: string; cls: string }> = {
    pending: { emoji: '⏳', label: 'Chờ duyệt', cls: 'brief-status--pending' },
    approved: { emoji: '✅', label: 'Đã duyệt', cls: 'brief-status--approved' },
    rejected: { emoji: '❌', label: 'Từ chối', cls: 'brief-status--rejected' },
    edited: { emoji: '✏️', label: 'Đã sửa', cls: 'brief-status--edited' },
  };

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">📝</div>
      <div className="chat-bubble chat-bubble--card chat-bubble--briefs">
        <div className="briefs-header">
          <h3>📝 Content Briefs ({briefs.length})</h3>
          <p>Xem xét, chỉnh sửa và phê duyệt các bài đăng Discord.</p>
          
          {/* Webhook selector */}
          {!loadingWebhooks && webhooks.length > 1 && (
            <div style={{ margin: '15px 0 10px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary, #aaa)', whiteSpace: 'nowrap' }}>📡 Đăng lên Webhook:</label>
              <select
                value={selectedWebhookId}
                onChange={(e) => setSelectedWebhookId(e.target.value)}
                style={{
                  flex: 1,
                  maxWidth: '300px',
                  background: 'rgba(100, 100, 100, 0.3)',
                  border: '1.5px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: 'var(--text-primary, #fff)',
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  outline: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(100, 200, 255, 0.6)';
                  e.currentTarget.style.background = 'rgba(100, 120, 150, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                  e.currentTarget.style.background = 'rgba(100, 100, 100, 0.3)';
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(100, 200, 255, 0.8)';
                  e.currentTarget.style.background = 'rgba(100, 120, 150, 0.5)';
                  e.currentTarget.style.boxShadow = '0 0 8px rgba(100, 200, 255, 0.4)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                  e.currentTarget.style.background = 'rgba(100, 100, 100, 0.3)';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
                }}
              >
                {webhooks.map(wh => (
                  <option key={wh.id} value={wh.id} style={{ background: '#222', color: '#fff' }}>
                    {wh.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="briefs-actions-top">
            <button
              className="btn btn--approve-all"
              onClick={handleApproveAll}
              disabled={isLoading}
            >
              ✅ Duyệt Tất Cả
            </button>
            <button
              className="btn btn--start-campaign"
              onClick={handleStartCampaign}
              disabled={isLoading || approvedCount === 0}
            >
              🚀 Thực Thi ({approvedCount}/{briefs.length})
            </button>
          </div>
        </div>

        <div className="briefs-list">
          {briefs.map((brief) => {
            const st = statusConfig[brief.status] || statusConfig.pending;
            const isEditing = editingId === brief.id;

            return (
              <div
                key={brief.id}
                className={`brief-card ${st.cls}`}
                style={{ borderLeftColor: `#${brief.embed_color.toString(16).padStart(6, '0')}` }}
              >
                <div className="brief-card-header">
                  <div className="brief-card-meta">
                    <span className="brief-day">📅 Ngày {brief.scheduled_day}</span>
                    <span className="brief-time">🕐 {brief.scheduled_time}</span>
                    <span className="brief-pillar-tag">{brief.pillar}</span>
                    <span className="brief-type-tag">{brief.content_type}</span>
                  </div>
                  <span className={`brief-status-badge ${st.cls}`}>
                    {st.emoji} {st.label}
                  </span>
                </div>

                {isEditing ? (
                  <div className="brief-edit-form">
                    <div className="brief-edit-field">
                      <label>Tiêu đề</label>
                      <input
                        type="text"
                        value={brief.title}
                        onChange={(e) => updateBrief(brief.id, { title: e.target.value })}
                      />
                    </div>
                    <div className="brief-edit-field">
                      <label>Caption</label>
                      <textarea
                        value={brief.caption}
                        onChange={(e) => updateBrief(brief.id, { caption: e.target.value })}
                        rows={3}
                      />
                    </div>
                    <div className="brief-edit-field">
                      <label>Image Prompt</label>
                      <textarea
                        value={brief.image_prompt}
                        onChange={(e) => updateBrief(brief.id, { image_prompt: e.target.value })}
                        rows={2}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="brief-card-body">
                    <h4 className="brief-title">{brief.title}</h4>
                    <p className="brief-caption">{brief.caption}</p>
                    <div className="brief-image-prompt">
                      <span className="brief-prompt-label">🎨 Image:</span>
                      <span className="brief-prompt-text">{brief.image_prompt}</span>
                    </div>
                  </div>
                )}

                <div className="brief-card-actions">
                  <button
                    className="btn-brief btn-brief--approve"
                    onClick={() => handleApprove(brief.id)}
                    disabled={brief.status === 'approved'}
                  >
                    ✅ Duyệt
                  </button>
                  <button
                    className="btn-brief btn-brief--edit"
                    onClick={() => handleEdit(brief.id)}
                  >
                    {isEditing ? '💾 Lưu' : '✏️ Sửa'}
                  </button>
                  <button
                    className="btn-brief btn-brief--reject"
                    onClick={() => handleReject(brief.id)}
                    disabled={brief.status === 'rejected'}
                  >
                    ❌ Từ chối
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
