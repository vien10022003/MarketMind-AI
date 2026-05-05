import { useState, useEffect } from 'react';
import { researchService } from '../services/researchService';
import './CampaignDashboard.css';

interface Campaign {
  _id: string;
  campaign_id: string;
  status: string;
  execution_mode: string;
  total_briefs: number;
  total_posted: number;
  total_scheduled: number;
  total_failed: number;
  started_at: string;
  completed_at?: string;
  execution_results?: any[];
}

export function CampaignDashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('all');

  useEffect(() => {
    loadCampaigns();
    // Auto-refresh every 2 minutes (120000 ms)
    const interval = setInterval(loadCampaigns, 120000);
    return () => clearInterval(interval);
  }, [filterStatus]);

  const loadCampaigns = async () => {
    setLoading(true);
    let allCampaigns: Campaign[] = [];

    // Load active campaigns
    const activeCampaigns = await researchService.getScheduledCampaigns('scheduled');
    allCampaigns = [...(activeCampaigns || [])];

    // Load completed campaigns
    const completedCampaigns = await researchService.getScheduledCampaigns('completed');
    allCampaigns = [...allCampaigns, ...(completedCampaigns || [])];

    setCampaigns(allCampaigns);
    setLoading(false);
  };

  const getFilteredCampaigns = () => {
    if (filterStatus === 'all') return campaigns;
    if (filterStatus === 'active') return campaigns.filter(c => c.status === 'scheduled');
    return campaigns.filter(c => c.status === 'completed');
  };

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
        return '⏳ Đang Chờ';
      case 'completed':
        return '✅ Hoàn Tất';
      case 'failed':
        return '❌ Lỗi';
      default:
        return status;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('vi-VN');
  };

  const filtered = getFilteredCampaigns();

  return (
    <div className="campaign-dashboard">
      <div className="dashboard-header">
        <h2>📊 Quản Lý Chiến Dịch</h2>
        <button className="refresh-btn" onClick={loadCampaigns} disabled={loading} title="Làm mới">
          🔄
        </button>
      </div>

      <div className="dashboard-tabs">
        <button
          className={`tab ${filterStatus === 'all' ? 'active' : ''}`}
          onClick={() => setFilterStatus('all')}
        >
          Tất Cả ({campaigns.length})
        </button>
        <button
          className={`tab ${filterStatus === 'active' ? 'active' : ''}`}
          onClick={() => setFilterStatus('active')}
        >
          Đang Hoạt Động ({campaigns.filter(c => c.status === 'scheduled').length})
        </button>
        <button
          className={`tab ${filterStatus === 'completed' ? 'active' : ''}`}
          onClick={() => setFilterStatus('completed')}
        >
          Đã Kết Thúc ({campaigns.filter(c => c.status === 'completed').length})
        </button>
      </div>

      <div className="campaigns-list">
        {loading ? (
          <div className="dashboard-loading">Đang tải...</div>
        ) : filtered.length === 0 ? (
          <div className="dashboard-empty">
            {filterStatus === 'all' ? 'Chưa có chiến dịch nào' : `Không có chiến dịch ${filterStatus === 'active' ? 'đang hoạt động' : 'đã kết thúc'}`}
          </div>
        ) : (
          filtered.map((campaign) => (
            <div key={campaign._id} className="campaign-card">
              <div className="campaign-header" onClick={() => setExpandedId(expandedId === campaign._id ? null : campaign._id)}>
                <div className="campaign-info">
                  <div className="campaign-title">
                    {expandedId === campaign._id ? '▼' : '▶'} {campaign.campaign_id}
                  </div>
                  <div className="campaign-meta">
                    <span className="status-badge" style={{ background: getStatusColor(campaign.status) }}>
                      {getStatusLabel(campaign.status)}
                    </span>
                    <span className="mode-badge">
                      {campaign.execution_mode === 'scheduled' ? '📅' : '⚡'} {campaign.execution_mode}
                    </span>
                    <span className="date">
                      {formatDate(campaign.started_at)}
                    </span>
                  </div>
                </div>
              </div>

              {expandedId === campaign._id && (
                <div className="campaign-details">
                  <div className="stats-grid">
                    <div className="stat">
                      <div className="stat-value">{campaign.total_briefs}</div>
                      <div className="stat-label">Tổng Bài</div>
                    </div>
                    <div className="stat">
                      <div className="stat-value" style={{ color: '#27ae60' }}>
                        {campaign.total_posted}
                      </div>
                      <div className="stat-label">Đã Post</div>
                    </div>
                    <div className="stat">
                      <div className="stat-value" style={{ color: '#f39c12' }}>
                        {campaign.total_scheduled}
                      </div>
                      <div className="stat-label">Chờ Post</div>
                    </div>
                    <div className="stat">
                      <div className="stat-value" style={{ color: '#e74c3c' }}>
                        {campaign.total_failed}
                      </div>
                      <div className="stat-label">Lỗi</div>
                    </div>
                  </div>

                  {campaign.execution_results && campaign.execution_results.length > 0 && (
                    <div className="results-section">
                      <h4>Chi Tiết Bài Đăng</h4>
                      <div className="results-list">
                        {campaign.execution_results.map((result, idx) => (
                          <div key={idx} className="result-item">
                            <div className="result-title">{result.brief_title || `Bài ${idx + 1}`}</div>
                            <div className="result-status">
                              <span
                                className="status-dot"
                                style={{ background: result.status === 'success' ? '#27ae60' : '#e74c3c' }}
                              />
                              {result.status === 'success' ? '✅ Thành công' : '❌ Lỗi'}
                            </div>
                            {result.posted_at && (
                              <div className="result-time">
                                Posted: {formatDate(result.posted_at)}
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

                  {campaign.completed_at && (
                    <div className="completed-info">
                      Hoàn tất: {formatDate(campaign.completed_at)}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
