import { useState, useEffect } from 'react';
import { researchService } from '../services/researchService';
import './ConversationList.css';

interface ConversationListProps {
  onSelectConversation: (conversationId: string) => void;
  onCreateNew: () => void;
  currentConversationId?: string;
}

interface Conversation {
  _id: string;
  conversation_id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export function ConversationList({ onSelectConversation, onCreateNew, currentConversationId }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoading(true);
    const data = await researchService.listConversations(0, 10);
    setConversations(data.conversations || []);
    setLoading(false);
  };

  const handleDelete = async (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    if (window.confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) {
      await researchService.deleteConversation(conversationId);
      loadConversations();
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString('vi-VN');
  };

  return (
    <div className="conversation-list">
      <button className="conversation-new-btn" onClick={onCreateNew}>
        ✨ Cuộc Hội Thoại Mới
      </button>

      <button
        className="conversation-toggle"
        onClick={() => setExpanded(!expanded)}
        title={expanded ? 'Ẩn' : 'Hiện'}
      >
        {expanded ? '▼' : '▶'} Lịch Sử ({conversations.length})
      </button>

      {expanded && (
        <div className="conversation-list-container">
          {loading ? (
            <div className="conversation-loading">Đang tải...</div>
          ) : conversations.length === 0 ? (
            <div className="conversation-empty">Chưa có cuộc hội thoại</div>
          ) : (
            <div className="conversation-items">
              {conversations.map((conv) => (
                <div
                  key={conv.conversation_id}
                  className={`conversation-item ${currentConversationId === conv.conversation_id ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conv.conversation_id)}
                >
                  <div className="conversation-info">
                    <div className="conversation-title">{conv.title}</div>
                    <div className="conversation-meta">
                      {conv.message_count} tin nhắn • {formatDate(conv.updated_at)}
                    </div>
                  </div>
                  <button
                    className="conversation-delete"
                    onClick={(e) => handleDelete(e, conv.conversation_id)}
                    title="Xóa"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
