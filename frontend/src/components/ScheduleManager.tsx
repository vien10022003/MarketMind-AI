import { useState, useEffect } from 'react';
import type { ScheduledCampaign, SchedulerStatus } from '../types';
import { getApiUrl } from '../config';
import './ScheduleManager.css';

interface ScheduleManagerProps {
  onViewCampaign?: (campaignId: string) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function ScheduleManager({ onViewCampaign, autoRefresh = true, refreshInterval = 10000 }: ScheduleManagerProps) {
  const [campaigns, setCampaigns] = useState<ScheduledCampaign[]>([]);
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const backendUrl = getApiUrl('');
      
      // Load campaigns
      const campaignsRes = await fetch(`${backendUrl}/api/stage-c/scheduler/campaigns`);
      if (campaignsRes.ok) {
        const data = await campaignsRes.json();
        if (data.success) {
          setCampaigns(data.data.campaigns);
        }
      }

      // Load scheduler status
      const statusRes = await fetch(`${backendUrl}/api/stage-c/scheduler/status`);
      if (statusRes.ok) {
        const data = await statusRes.json();
        if (data.success) {
          setStatus(data.data);
        }
      }

      setError(null);
    } catch (err) {
      setError(`Lỗi tải dữ liệu: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    
    if (!autoRefresh) return;

    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return '#f39c12';
      case 'completed':
        return '#27ae60';
      case 'failed':
        return '#e74c3c';
      default:
        return '#95a5a6';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'scheduled':
        return '📅 Lên lịch';
      case 'completed':
        return '✅ Hoàn tất';
      case 'failed':
        return '❌ Thất bại';
      default:
        return '❓ Không xác định';
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('vi-VN');
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="schedule-manager">
      <div className="schedule-manager-header">
        <h3>📊 Quản lý lịch đăng</h3>
        <button
          onClick={loadData}
          disabled={loading}
          className="refresh-btn"
          title="Làm mới dữ liệu"
        >
          {loading ? '⏳' : '🔄'}
        </button>
      </div>

      {/* Scheduler Status */}
      {status && (
        <div className="scheduler-status">
          <div className="status-item">
            <span className="status-label">Trạng thái:</span>
            <span className={`status-value ${status.running ? 'running' : 'stopped'}`}>
              {status.running ? '🟢 Đang chạy' : '🔴 Dừng'}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Bài chờ đăng:</span>
            <span className="status-value">{status.pending_briefs}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Kiểm tra mỗi:</span>
            <span className="status-value">{status.check_interval}s</span>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Campaigns List */}
      <div className="campaigns-container">
        {campaigns.length === 0 ? (
          <div className="empty-state">
            <p>📭 Chưa có chiến dịch nào được lên lịch</p>
            <p className="empty-hint">Hãy chọn "📅 Lên lịch" từ Stage C để bắt đầu</p>
          </div>
        ) : (
          <div className="campaigns-list">
            {campaigns.map(campaign => (
              <div
                key={campaign.campaign_id}
                className={`campaign-card ${campaign.status}`}
              >
                <div className="campaign-header" onClick={() => setExpandedId(expandedId === campaign.campaign_id ? null : campaign.campaign_id)}>
                  <div className="campaign-title-section">
                    <h4>{campaign.campaign_id}</h4>
                    <span
                      className="campaign-status"
                      style={{ backgroundColor: getStatusColor(campaign.status) }}
                    >
                      {getStatusLabel(campaign.status)}
                    </span>
                  </div>
                  <span className="expand-icon">
                    {expandedId === campaign.campaign_id ? '▼' : '▶'}
                  </span>
                </div>

                <div className="campaign-stats">
                  <div className="stat">
                    <span className="stat-label">Tổng cộng</span>
                    <span className="stat-value">{campaign.total_briefs}</span>
                  </div>
                  <div className="stat success">
                    <span className="stat-label">✅ Đã đăng</span>
                    <span className="stat-value">{campaign.total_posted}</span>
                  </div>
                  <div className="stat pending">
                    <span className="stat-label">⏳ Chờ đăng</span>
                    <span className="stat-value">{campaign.total_scheduled}</span>
                  </div>
                  {campaign.total_failed > 0 && (
                    <div className="stat error">
                      <span className="stat-label">❌ Thất bại</span>
                      <span className="stat-value">{campaign.total_failed}</span>
                    </div>
                  )}
                </div>

                {/* Expanded Details */}
                {expandedId === campaign.campaign_id && (
                  <div className="campaign-details">
                    <div className="detail-row">
                      <span className="detail-label">Tạo lúc:</span>
                      <span className="detail-value">{formatDate(campaign.created_at)}</span>
                    </div>
                    {campaign.completed_at && (
                      <div className="detail-row">
                        <span className="detail-label">Hoàn tất lúc:</span>
                        <span className="detail-value">{formatDate(campaign.completed_at)}</span>
                      </div>
                    )}
                    {campaign.execution_results && campaign.execution_results.length > 0 && (
                      <div className="results-section">
                        <h5>Kết quả thực thi</h5>
                        <div className="results-list">
                          {campaign.execution_results.map((result, idx) => (
                            <div key={idx} className={`result-item ${result.status}`}>
                              <div className="result-title">
                                {result.status === 'success' && '✅'}
                                {result.status === 'failed' && '❌'}
                                {result.status === 'scheduled' && '⏳'}
                                {result.status === 'pending' && '⏸️'}
                                {' '}
                                {result.brief_title}
                              </div>
                              {result.scheduled_post_time && (
                                <div className="result-meta">
                                  <span>📅 Lên lịch: {formatDate(result.scheduled_post_time)}</span>
                                </div>
                              )}
                              {result.posted_at && (
                                <div className="result-meta">
                                  <span>📤 Đã đăng: {formatDate(result.posted_at)}</span>
                                </div>
                              )}
                              {result.error && (
                                <div className="result-error">{result.error}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="detail-actions">
                      {onViewCampaign && (
                        <button
                          onClick={() => onViewCampaign(campaign.campaign_id)}
                          className="detail-btn"
                        >
                          📖 Xem chi tiết
                        </button>
                      )}
                      <button
                        onClick={loadData}
                        className="detail-btn-secondary"
                      >
                        🔄 Làm mới
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="schedule-manager-footer">
        <small>🔄 Tự động cập nhật mỗi {refreshInterval / 1000}s</small>
      </div>
    </div>
  );
}
