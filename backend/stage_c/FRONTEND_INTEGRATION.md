"""
Frontend Integration Guide - Scheduled Stage C Posting

This document explains how to integrate scheduled posting UI into the frontend.
"""

# ============================================================================
# STEP 1: UPDATE researchService.ts
# ============================================================================

# Add method to call Stage C with scheduled mode:

async callStageCCampaignScheduled(
    input: {
        approved_briefs: ContentBrief[];
        scheduled_times: string[];  // ISO 8601 datetimes
        mongodb_stage_a_id?: string;
    },
    onStreamMessage: (msg: StreamMessage) => void,
    onError: (msg: string) => void,
) {
    const url = `${getBackendUrl()}/stage-c/campaign-scheduled`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                approved_briefs: input.approved_briefs,
                scheduled_times: input.scheduled_times,
                mongodb_stage_a_id: input.mongodb_stage_a_id,
            }),
        });

        // Handle streaming response
        const reader = response.body?.getReader();
        if (!reader) return;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = new TextDecoder().decode(value);
            const messages = text.split('\n').filter(m => m.trim());

            for (const line of messages) {
                try {
                    const message = JSON.parse(line);
                    onStreamMessage(message);
                } catch {
                    console.error('Failed to parse stream message:', line);
                }
            }
        }
    } catch (error) {
        onError(`Scheduled campaign error: ${error}`);
    }
}

# ============================================================================
# STEP 2: CREATE SCHEDULE EDITOR COMPONENT
# ============================================================================

# src/components/ScheduleEditor.tsx

import { ContentBrief } from '../types';
import './ScheduleEditor.css';

interface ScheduleEditorProps {
  briefs: ContentBrief[];
  onSchedule: (times: string[]) => void;
  onCancel: () => void;
}

export function ScheduleEditor({ briefs, onSchedule, onCancel }: ScheduleEditorProps) {
  const [times, setTimes] = useState<string[]>(
    briefs.map((_, i) => {
      const date = new Date();
      date.setHours(date.getHours() + i + 1, 0, 0, 0);
      return date.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm
    })
  );

  const handleTimeChange = (index: number, value: string) => {
    const newTimes = [...times];
    newTimes[index] = value;
    setTimes(newTimes);
  };

  const handleSchedule = () => {
    // Convert to ISO 8601 format
    const isoTimes = times.map(t => new Date(t).toISOString());
    onSchedule(isoTimes);
  };

  return (
    <div className="schedule-editor">
      <h3>📅 Lên lịch đăng bài</h3>
      <div className="schedule-list">
        {briefs.map((brief, idx) => (
          <div key={idx} className="schedule-item">
            <label>
              <span className="brief-title">{brief.title || `Bài đăng ${idx + 1}`}</span>
              <input
                type="datetime-local"
                value={times[idx]}
                onChange={(e) => handleTimeChange(idx, e.target.value)}
              />
            </label>
          </div>
        ))}
      </div>
      <div className="schedule-actions">
        <button onClick={handleSchedule} className="btn-primary">
          ✅ Lên lịch ({briefs.length} bài)
        </button>
        <button onClick={onCancel} className="btn-secondary">
          ❌ Hủy
        </button>
      </div>
    </div>
  );
}

# ============================================================================
# STEP 3: UPDATE ChatMessage COMPONENT
# ============================================================================

# Add handling for stage_c_schedule_proposal message type:

} else if (message.type === 'stage_c_schedule_proposal') {
  return (
    <div className="chat-bubble schedule-proposal">
      <p>{message.content}</p>
      <div className="proposal-actions">
        <button 
          onClick={() => setShowScheduleEditor(true)}
          className="btn-primary"
        >
          📅 Lên lịch
        </button>
        <button 
          onClick={() => handleAcceptStageCProposal(message.stageCProposalData?.briefs || [])}
          className="btn-secondary"
        >
          ⚡ Đăng ngay
        </button>
      </div>
      {showScheduleEditor && (
        <ScheduleEditor
          briefs={message.stageCProposalData?.briefs || []}
          onSchedule={handleScheduleSubmit}
          onCancel={() => setShowScheduleEditor(false)}
        />
      )}
    </div>
  );
}

# ============================================================================
# STEP 4: ADD SCHEDULE MANAGER COMPONENT
# ============================================================================

# src/components/ScheduleManager.tsx

import { useState, useEffect } from 'react';

interface Campaign {
  campaign_id: string;
  total_briefs: number;
  total_posted: number;
  total_scheduled: number;
  status: string;
  created_at: string;
}

export function ScheduleManager() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/stage-c/scheduler/campaigns');
      const data = await response.json();
      if (data.success) {
        setCampaigns(data.data.campaigns);
      }
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCampaigns();
    const interval = setInterval(loadCampaigns, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="schedule-manager">
      <h3>📊 Quản lý lịch đăng</h3>
      {loading && <p>Đang tải...</p>}
      <div className="campaigns-list">
        {campaigns.map(campaign => (
          <div key={campaign.campaign_id} className="campaign-card">
            <h4>{campaign.campaign_id}</h4>
            <div className="stats">
              <span>Tổng: {campaign.total_briefs}</span>
              <span className="success">✅ Đã đăng: {campaign.total_posted}</span>
              <span className="pending">⏳ Chưa đăng: {campaign.total_scheduled}</span>
            </div>
            <span className={`status status-${campaign.status}`}>
              {campaign.status === 'scheduled' ? '📅 Lên lịch' : 'Hoàn tất'}
            </span>
            <button 
              onClick={() => window.open(`/schedule/${campaign.campaign_id}`)}
              className="btn-small"
            >
              Chi tiết
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

# ============================================================================
# STEP 5: ADD CSS STYLING
# ============================================================================

/* src/components/ScheduleEditor.css */

.schedule-editor {
  border: 2px solid #5865F2;
  border-radius: 8px;
  padding: 16px;
  background: #f8f9fa;
  margin: 16px 0;
}

.schedule-editor h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.schedule-item label {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4px;
}

.brief-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.schedule-item input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.schedule-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background: #5865F2;
  color: white;
}

.btn-primary:hover {
  background: #4752C4;
}

.btn-secondary {
  background: #ccc;
  color: #333;
}

.btn-secondary:hover {
  background: #bbb;
}

/* Schedule Manager */

.schedule-manager {
  padding: 16px;
  background: white;
  border-radius: 8px;
  margin: 16px 0;
}

.campaigns-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.campaign-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  background: #f8f9fa;
}

.campaign-card h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  margin: 8px 0;
}

.stats .success {
  color: #27ae60;
}

.stats .pending {
  color: #f39c12;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin: 8px 0;
}

.status-scheduled {
  background: #fff3cd;
  color: #856404;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.btn-small {
  background: #5865F2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 8px;
}

.btn-small:hover {
  background: #4752C4;
}

# ============================================================================
# STEP 6: USAGE IN APP.tsx
# ============================================================================

# In App.tsx, add the schedule manager to the UI:

import { ScheduleManager } from './components/ScheduleManager';

function App() {
  // ... existing code ...

  return (
    <div className="app-container">
      {/* ... existing header and chat ... */}
      
      {/* Add schedule manager sidebar or modal */}
      {showScheduleManager && (
        <aside className="schedule-sidebar">
          <ScheduleManager />
        </aside>
      )}
      
      {/* ... footer ... */}
    </div>
  );
}

# ============================================================================
# STEP 7: BACKEND ENDPOINT FOR SCHEDULED POSTING
# ============================================================================

# In your Flask app (flask_api.py):

@app.route('/stage-c/campaign-scheduled', methods=['POST'])
def stage_c_campaign_scheduled():
    """Execute Stage C with scheduled posting"""
    data = request.get_json()
    
    from stage_c.data_models_c import StageCInput
    from stage_c.discord_publisher import run_stage_c_pipeline
    
    try:
        stage_c_input = StageCInput(
            approved_briefs=data.get('approved_briefs', []),
            execution_mode='scheduled',
            scheduled_times=data.get('scheduled_times', []),
            mongodb_stage_a_id=data.get('mongodb_stage_a_id'),
        )
        
        def generate():
            for event in run_stage_c_pipeline(stage_c_input):
                yield json.dumps(event) + '\n'
        
        return Response(
            generate(),
            content_type='application/x-ndjson'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
