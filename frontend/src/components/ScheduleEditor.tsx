import { useState } from 'react';
import type { ContentBrief } from '../types';
import './ScheduleEditor.css';

interface ScheduleEditorProps {
  briefs: ContentBrief[];
  onSchedule: (times: string[]) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ScheduleEditor({ briefs, onSchedule, onCancel, isLoading }: ScheduleEditorProps) {
  // Initialize with times spaced 1 hour apart starting from tomorrow 9 AM
  const getDefaultTimes = () => {
    return briefs.map((_, i) => {
      const date = new Date();
      date.setDate(date.getDate() + 1); // Tomorrow
      date.setHours(9 + i, 0, 0, 0); // 9 AM, then 10 AM, etc.
      return date.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm format
    });
  };

  const [times, setTimes] = useState<string[]>(getDefaultTimes());

  const handleTimeChange = (index: number, value: string) => {
    const newTimes = [...times];
    newTimes[index] = value;
    setTimes(newTimes);
  };

  const handleSchedule = () => {
    // Convert to ISO 8601 format
    const isoTimes = times.map(t => {
      if (!t) return '';
      const date = new Date(t);
      return date.toISOString();
    });
    onSchedule(isoTimes);
  };

  const isValid = times.every(t => t && t.trim() !== '');

  return (
    <div className="schedule-editor">
      <div className="schedule-header">
        <h3>📅 Lên lịch đăng bài</h3>
        <p className="schedule-subtitle">Chọn thời gian cụ thể cho mỗi bài đăng</p>
      </div>

      <div className="schedule-list">
        {briefs.map((brief, idx) => (
          <div key={idx} className="schedule-item">
            <div className="schedule-item-header">
              <span className="schedule-index">#{idx + 1}</span>
              <span className="brief-title">{brief.title || `Bài đăng ${idx + 1}`}</span>
              <span className="brief-pillar">📍 {brief.pillar}</span>
            </div>
            <div className="schedule-item-content">
              <input
                type="datetime-local"
                value={times[idx]}
                onChange={(e) => handleTimeChange(idx, e.target.value)}
                disabled={isLoading}
                className="schedule-datetime-input"
              />
              {brief.caption && (
                <p className="brief-caption">{brief.caption.substring(0, 60)}...</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="schedule-actions">
        <button
          onClick={handleSchedule}
          disabled={!isValid || isLoading}
          className="btn-primary schedule-btn"
        >
          {isLoading ? '⏳ Đang lên lịch...' : `✅ Lên lịch (${briefs.length} bài)`}
        </button>
        <button
          onClick={onCancel}
          disabled={isLoading}
          className="btn-secondary schedule-btn"
        >
          ❌ Hủy
        </button>
      </div>

      <div className="schedule-tips">
        <p className="tip-title">💡 Mẹo:</p>
        <ul>
          <li>Cách nhau ít nhất 30 phút để tránh vượt quá giới hạn Discord</li>
          <li>Lịch được lưu theo giờ UTC (Koordinated Universal Time)</li>
          <li>Bạn có thể theo dõi trạng thái chiến dịch trong quản lý lịch</li>
        </ul>
      </div>
    </div>
  );
}
