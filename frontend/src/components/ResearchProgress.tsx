import { config } from '../config';

interface ResearchProgressProps {
  messages: string[];
  isLoading: boolean;
}

export function ResearchProgress({ messages, isLoading }: ResearchProgressProps) {
  return (
    <div className="research-progress">
      <h3>Tiến Độ Xử Lý</h3>
      <div 
        className="progress-container"
        style={{ maxHeight: `${config.ui.progressMaxHeight}px` }}
      >
        {messages.length === 0 && !isLoading && <p className="empty-state">Chưa có dữ liệu</p>}

        {messages.map((message, index) => (
          <div key={index} className="progress-message">
            <span className="message-icon">📌</span>
            <span className="message-text">{message}</span>
          </div>
        ))}

        {isLoading && <div className="loading-spinner">⏳ Đang xử lý...</div>}
      </div>
    </div>
  );
}
