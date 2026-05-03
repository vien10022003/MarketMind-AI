import type { CampaignLog } from '../types';
import { CollapsibleCard } from './CollapsibleCard';

interface CampaignResultsBubbleProps {
  data: CampaignLog;
}

export function CampaignResultsBubble({ data }: CampaignResultsBubbleProps) {
  const successRate = data.total_briefs > 0
    ? Math.round((data.total_posted / data.total_briefs) * 100)
    : 0;

  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🚀</div>
      <div className="chat-bubble chat-bubble--card chat-bubble--campaign">
        <CollapsibleCard
          title="Kết Quả Chiến Dịch"
          summary={`${data.total_posted}/${data.total_briefs} bài đã đăng (${successRate}%)`}
          icon="🚀"
          accentColor="var(--accent-campaign, #f59e0b)"
        >
          <div className="campaign-results-detail">
            {/* Summary Stats */}
            <div className="campaign-results-stats">
              <div className="cr-stat cr-stat--success">
                <span className="cr-stat-num">{data.total_posted}</span>
                <span className="cr-stat-label">✅ Thành công</span>
              </div>
              <div className="cr-stat cr-stat--failed">
                <span className="cr-stat-num">{data.total_failed}</span>
                <span className="cr-stat-label">❌ Thất bại</span>
              </div>
              <div className="cr-stat cr-stat--skipped">
                <span className="cr-stat-num">{data.total_skipped}</span>
                <span className="cr-stat-label">⏭️ Bỏ qua</span>
              </div>
              <div className="cr-stat cr-stat--rate">
                <span className="cr-stat-num">{successRate}%</span>
                <span className="cr-stat-label">📊 Tỷ lệ</span>
              </div>
            </div>

            {/* Individual Results */}
            <div className="campaign-results-list">
              {data.results.map((result, i) => (
                <div
                  key={i}
                  className={`cr-item cr-item--${result.status}`}
                >
                  <div className="cr-item-header">
                    <span className="cr-item-status">
                      {result.status === 'success' ? '✅' : result.status === 'failed' ? '❌' : '⏭️'}
                    </span>
                    <strong className="cr-item-title">{result.brief_title}</strong>
                  </div>

                  <div className="cr-item-details">
                    {result.image_url && (
                      <div className="cr-item-image">
                        <img
                          src={result.image_url}
                          alt={result.brief_title}
                          loading="lazy"
                        />
                      </div>
                    )}
                    {result.image_skipped && (
                      <span className="cr-item-note">🖼️ Ảnh bị bỏ qua</span>
                    )}
                    <div className="cr-item-meta">
                      <span>
                        {result.discord_sent ? '📤 Discord: Đã gửi' : '📤 Discord: Chưa gửi'}
                      </span>
                      {result.error && (
                        <span className="cr-item-error">⚠️ {result.error}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Campaign ID */}
            <div className="campaign-results-footer">
              <span className="cr-campaign-id">
                Campaign ID: {data.campaign_id}
              </span>
              {data.completed_at && (
                <span className="cr-completed-at">
                  Hoàn thành: {new Date(data.completed_at).toLocaleString('vi-VN')}
                </span>
              )}
            </div>
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}
