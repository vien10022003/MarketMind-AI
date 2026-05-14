import { useState, useEffect, useCallback } from 'react';
import type { ResearchRequest, ClarificationData } from '../types';

interface ResearchFormProps {
  onSubmit: (request: ResearchRequest) => void;
  isLoading: boolean;
  clarification?: ClarificationData;
  onClarificationConfirm?: (overrides: Partial<ResearchRequest>) => void;
}

export function ResearchForm({ 
  onSubmit, 
  isLoading, 
  clarification,
  onClarificationConfirm 
}: ResearchFormProps) {
  const [userPrompt, setUserPrompt] = useState<string>('');
  const [clarificationOverrides, setClarificationOverrides] = useState<Partial<ResearchRequest>>({});
  const [autoConfirmCountdown, setAutoConfirmCountdown] = useState<number>(0);

  useEffect(() => {
    if (clarification?.auto_proceeding && autoConfirmCountdown === 0) {
      setAutoConfirmCountdown(5);
    }
  }, [clarification?.auto_proceeding]);

  useEffect(() => {
    if (autoConfirmCountdown <= 0) return;
    
    const timeout = setTimeout(() => {
      setAutoConfirmCountdown((prev) => prev - 1);
    }, 1000);

    return () => clearTimeout(timeout);
  }, [autoConfirmCountdown]);

  useEffect(() => {
    if (autoConfirmCountdown === 1 && clarification && onClarificationConfirm) {
      handleConfirmClarification();
    }
  }, [autoConfirmCountdown]);

  const handleSubmitPrompt = (e: React.FormEvent) => {
    e.preventDefault();

    if (!userPrompt.trim()) {
      alert('Vui lòng nhập yêu cầu nghiên cứu của bạn');
      return;
    }

    const request: ResearchRequest = {
      user_prompt: userPrompt,
    };

    onSubmit(request);
  };

  const handleConfirmClarification = useCallback(() => {
    if (clarification && onClarificationConfirm) {
      const finalInput: Partial<ResearchRequest> = {
        ...clarification.clarified_input,
        ...clarificationOverrides,
      };
      onClarificationConfirm(finalInput);
      setClarificationOverrides({});
      setAutoConfirmCountdown(0);
    }
  }, [clarification, onClarificationConfirm, clarificationOverrides]);

  const handleOverrideChange = (field: keyof ResearchRequest, value: any) => {
    setClarificationOverrides((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Show clarification UI if available
  if (clarification) {
    return (
      <div className="research-form clarification-mode">
        <h2>📋 LLM Đã Phân Tích Yêu Cầu</h2>
        
        <div className="detected-info-box">
          <h3>✅ Thông Tin Phát Hiện</h3>
          <p>{clarification.detected_info}</p>
        </div>

        {clarification.questions_for_user.length > 0 && (
          <div className="questions-section">
            <h3>❓ Các Câu Hỏi Cần Xác Nhận</h3>
            <div className="questions-list">
              {clarification.questions_for_user.map((question, idx) => (
                <div key={idx} className="question-item">
                  <p className="question-text">• {question}</p>
                </div>
              ))}
            </div>

            <div className="override-section">
              <h3>🎯 Thông Tin Được Đề Xuất (Có Thể Sửa)</h3>
              
              <div className="override-group">
                <label htmlFor="override-ban-chat">Bản Chất Sản Phẩm:</label>
                <textarea
                  id="override-ban-chat"
                  defaultValue={clarification.clarified_input.ban_chat_san_pham}
                  onChange={(e) => handleOverrideChange('ban_chat_san_pham', e.target.value)}
                  className="override-input"
                  rows={4}
                  placeholder={"- Tên sản phẩm, danh mục, mô tả ngắn gọn (nó là gì? dùng để làm gì?)\n- Tính năng nổi bật và lợi ích thực tế mang lại cho người dùng\n- Điểm khác biệt so với các sản phẩm cùng loại (USP)"}
                />
                {clarification.explanations.ban_chat_san_pham && (
                  <small className="explanation">💡 {clarification.explanations.ban_chat_san_pham}</small>
                )}
              </div>

              <div className="override-group">
                <label htmlFor="override-khach-hang">Khách Hàng Mục Tiêu:</label>
                <textarea
                  id="override-khach-hang"
                  defaultValue={clarification.clarified_input.khach_hang_muc_tieu}
                  onChange={(e) => handleOverrideChange('khach_hang_muc_tieu', e.target.value)}
                  className="override-input"
                  rows={4}
                  placeholder={"- Họ là ai? (độ tuổi, giới tính, nghề nghiệp, khu vực địa lý...)\n- Nhu cầu, nỗi đau (pain points) hoặc mong muốn họ đang gặp phải\n- Thói quen tiêu dùng và kênh thông tin họ thường tiếp cận"}
                />
                {clarification.explanations.khach_hang_muc_tieu && (
                  <small className="explanation">💡 {clarification.explanations.khach_hang_muc_tieu}</small>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="suggested-info-box">
          <h3>💡 Thông Tin Đã Chuẩn Bị</h3>
          <ul>
            <li><strong>Bản chất sản phẩm:</strong> {clarificationOverrides.ban_chat_san_pham || clarification.clarified_input.ban_chat_san_pham}</li>
            <li><strong>Khách hàng mục tiêu:</strong> {clarificationOverrides.khach_hang_muc_tieu || clarification.clarified_input.khach_hang_muc_tieu}</li>
            {(clarificationOverrides.gia_tri_cot_loi || clarification.clarified_input.gia_tri_cot_loi) && (
              <li><strong>Giá trị cốt lõi:</strong> {clarificationOverrides.gia_tri_cot_loi || clarification.clarified_input.gia_tri_cot_loi}</li>
            )}
            {(clarificationOverrides.gia_ca_chinh_sach || clarification.clarified_input.gia_ca_chinh_sach) && (
              <li><strong>Giá cả & Chính sách:</strong> {clarificationOverrides.gia_ca_chinh_sach || clarification.clarified_input.gia_ca_chinh_sach}</li>
            )}
          </ul>
        </div>

        <div className="clarification-actions">
          <button 
            onClick={() => handleConfirmClarification()}
            className="confirm-btn"
            disabled={isLoading || autoConfirmCountdown > 0}
          >
            {autoConfirmCountdown > 0 
              ? `⏱️ Bắt Đầu Trong ${autoConfirmCountdown}s...` 
              : '✅ Xác Nhận & Bắt Đầu Nghiên Cứu'}
          </button>
          {clarification.auto_proceeding && (
            <p className="auto-proceed-note">🤖 Sẽ tự động bắt đầu nếu không có lỗi...</p>
          )}
        </div>

        {clarification.note && (
          <div className="clarification-note">
            <small>{clarification.note}</small>
          </div>
        )}
      </div>
    );
  }

  // Show simple prompt input if no clarification yet
  return (
    <div className="research-form prompt-mode">
      <h2>🎯 Nghiên Cứu Thị Trường</h2>
      <form onSubmit={handleSubmitPrompt}>
        <div className="form-group">
          <label htmlFor="user_prompt">Mô Tả Yêu Cầu Của Bạn *</label>
          <textarea
            id="user_prompt"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="VD: Tôi muốn nghiên cứu thị trường mỹ phẩm thuần chay ở Việt Nam, tập trung vào phân khúc Gen Z. Hãy phân tích xu hướng, đối thủ chính như Cocoon, The Body Shop, và hành vi mua hàng của người tiêu dùng."
            disabled={isLoading}
            rows={6}
            className="prompt-textarea"
          />
          <small>
            Mô tả chi tiết những gì bạn muốn nghiên cứu. LLM sẽ phân tích và hỏi những thông tin cụ thể nếu cần.
          </small>
        </div>

        <button 
          type="submit" 
          disabled={isLoading} 
          className="submit-btn"
        >
          {isLoading ? '⏳ Đang phân tích...' : '🚀 Phân Tích & Bắt Đầu'}
        </button>
      </form>

      <div className="example-prompts">
        <h3>💡 Ví Dụ Yêu Cầu</h3>
        <ul>
          <li>Tôi muốn biết thị trường thương mại điện tử thế nào ở Việt Nam năm 2025</li>
          <li>Phân tích ngành fintech ở TP.HCM, tập trung vào startup, người dùng trẻ</li>
          <li>Nghiên cứu xu hướng fashion bền vững tại các nước Đông Nam Á</li>
        </ul>
      </div>
    </div>
  );
}
