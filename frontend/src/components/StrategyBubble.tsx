import type { StageBOutput } from '../types';
import { CollapsibleCard } from './CollapsibleCard';

interface StrategyBubbleProps {
  data: StageBOutput;
}

export function StrategyBubble({ data }: StrategyBubbleProps) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="chat-avatar chat-avatar--assistant">🎯</div>
      <div className="chat-bubble chat-bubble--card chat-bubble--strategy">
        <CollapsibleCard
          title="Chiến Lược Marketing"
          summary="SWOT • USP • Persona • Content Pillars • Campaign Plan"
          icon="🎯"
          accentColor="var(--accent-strategy, #10b981)"
        >
          <div className="strategy-detail">
            {/* SWOT Matrix */}
            <section className="strategy-section">
              <h4>📊 Phân Tích SWOT</h4>
              <div className="swot-grid">
                <div className="swot-quadrant swot-strengths">
                  <div className="swot-label">💪 Điểm Mạnh</div>
                  <ul>{data.swot.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
                <div className="swot-quadrant swot-weaknesses">
                  <div className="swot-label">⚠️ Điểm Yếu</div>
                  <ul>{data.swot.weaknesses.map((w, i) => <li key={i}>{w}</li>)}</ul>
                </div>
                <div className="swot-quadrant swot-opportunities">
                  <div className="swot-label">🌟 Cơ Hội</div>
                  <ul>{data.swot.opportunities.map((o, i) => <li key={i}>{o}</li>)}</ul>
                </div>
                <div className="swot-quadrant swot-threats">
                  <div className="swot-label">⚡ Thách Thức</div>
                  <ul>{data.swot.threats.map((t, i) => <li key={i}>{t}</li>)}</ul>
                </div>
              </div>
            </section>

            {/* USP */}
            <section className="strategy-section">
              <h4>🎯 Unique Selling Proposition</h4>
              <div className="usp-callout">
                <p className="usp-statement">"{data.usp.usp_statement}"</p>
                <div className="usp-points">
                  {data.usp.supporting_points.map((p, i) => (
                    <span key={i} className="usp-point">✓ {p}</span>
                  ))}
                </div>
                {data.usp.competitive_advantage && (
                  <p className="usp-advantage">
                    <strong>🏆 Lợi thế:</strong> {data.usp.competitive_advantage}
                  </p>
                )}
              </div>
            </section>

            {/* Persona */}
            <section className="strategy-section">
              <h4>👤 Buyer Persona</h4>
              <div className="persona-card">
                <div className="persona-header">
                  <span className="persona-avatar">👤</span>
                  <div>
                    <strong className="persona-name">{data.persona.name}</strong>
                    <span className="persona-age">{data.persona.age_range} tuổi</span>
                  </div>
                </div>
                <div className="persona-details">
                  <div className="persona-detail-group">
                    <span className="persona-detail-label">💬 Discord:</span>
                    <p>{data.persona.discord_behavior}</p>
                  </div>
                  <div className="persona-tags">
                    <span className="persona-detail-label">❤️ Sở thích:</span>
                    <div className="tag-list">
                      {data.persona.interests.map((i, idx) => (
                        <span key={idx} className="tag tag--interest">{i}</span>
                      ))}
                    </div>
                  </div>
                  <div className="persona-tags">
                    <span className="persona-detail-label">😣 Pain points:</span>
                    <div className="tag-list">
                      {data.persona.pain_points.map((p, idx) => (
                        <span key={idx} className="tag tag--pain">{p}</span>
                      ))}
                    </div>
                  </div>
                  <div className="persona-tags">
                    <span className="persona-detail-label">📱 Content ưa thích:</span>
                    <div className="tag-list">
                      {data.persona.preferred_content_types.map((ct, idx) => (
                        <span key={idx} className="tag tag--content">{ct}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Content Pillars */}
            <section className="strategy-section">
              <h4>📌 Content Pillars ({data.content_pillars.length})</h4>
              <div className="pillars-grid">
                {data.content_pillars.map((pillar, i) => (
                  <div key={i} className="pillar-card">
                    <div className="pillar-header">
                      <span className="pillar-emoji">{pillar.emoji}</span>
                      <strong>{pillar.name}</strong>
                    </div>
                    <p className="pillar-desc">{pillar.description}</p>
                    <div className="pillar-topics">
                      {pillar.example_topics.map((t, j) => (
                        <span key={j} className="pillar-topic">• {t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Campaign Plan */}
            <section className="strategy-section">
              <h4>📅 Kế Hoạch Chiến Dịch</h4>
              <div className="campaign-overview">
                <div className="campaign-stats">
                  <div className="campaign-stat">
                    <span className="campaign-stat-num">{data.campaign_plan.duration_days}</span>
                    <span className="campaign-stat-label">Ngày</span>
                  </div>
                  <div className="campaign-stat">
                    <span className="campaign-stat-num">{data.campaign_plan.schedule.length}</span>
                    <span className="campaign-stat-label">Bài đăng</span>
                  </div>
                  <div className="campaign-stat">
                    <span className="campaign-stat-num">{data.campaign_plan.posting_frequency}</span>
                    <span className="campaign-stat-label">Tần suất</span>
                  </div>
                </div>
                {data.campaign_plan.campaign_goal && (
                  <p className="campaign-goal">🎯 {data.campaign_plan.campaign_goal}</p>
                )}
                <div className="campaign-schedule">
                  {data.campaign_plan.schedule.map((entry, i) => (
                    <div key={i} className="schedule-entry">
                      <span className="schedule-day">Ngày {entry.day}</span>
                      <span className="schedule-time">🕐 {entry.time}</span>
                      <span className="schedule-type">{entry.content_type}</span>
                      <span className="schedule-pillar">{entry.pillar_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </CollapsibleCard>
      </div>
    </div>
  );
}
