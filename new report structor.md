📑 CẤU TRÚC MỤC LỤC ĐỀ XUẤT (CÓ BỔ SUNG UML)
CHƯƠNG I: TỔNG QUAN LÝ THUYẾT
(Giữ nguyên như cũ - tập trung vào lý thuyết GenAI, Agentic AI, LLM...)
CHƯƠNG II: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG 🆕 (Trọng tâm vẽ biểu đồ)
2.1 Phân tích yêu cầu hệ thống

    2.1.3 Đặc tả Use Case & Biểu đồ Use Case (Mới)
2.2 Thiết kế kiến trúc tổng thể

    2.2.3 Biểu đồ triển khai (Deployment Diagram) (Mới)
2.3 Thiết kế chi tiết (Detailed Design)

    2.3.3 Biểu đồ tuần tự (Sequence Diagrams) cho các luồng chính (Mới)
    2.3.4 Thiết kế các Agent/Tools (Class/Component Diagram) (Mới)
2.4 Lựa chọn công nghệ

🛠️ HƯỚNG DẪN TRÍCH XUẤT THÔNG TIN TỪ CODE ĐỂ VẼ UML
Bạn có thể giao nhiệm vụ cho người phụ trách code theo bảng sau để họ cung cấp nguyên liệu vẽ biểu đồ:
Loại biểu đồ
Mục đích trong báo cáo
Thông tin cần trích xuất từ Code/Logs
Gợi ý công cụ vẽ
Use Case Diagram
Mô tả ai (Actor) làm gì với hệ thống
- Danh sách Actor: User, Admin, External APIs (Google Search, CRM...)
- Danh sách tính năng (Use Cases): "Tạo content", "Phân tích sentiment", "Lên lịch đăng bài"
- Mối quan hệ: include (VD: đăng bài phải login), extend (VD: lỗi thì gửi alert)
Draw.io, StarUML, PlantUML
Sequence Diagram (Quan trọng nhất với Agentic AI)
Mô tả luồng tương tác thời gian thực giữa User ↔ AI ↔ Tools
- Trace log của 1 request hoàn chỉnh: User Input → Router → LLM → [Decision: Call Tool X] → Tool Execution → LLM Summarize → Response.
- Xác định rõ các bước async/wait (chờ tool chạy).
- Các trường hợp fallback (khi LLM gọi sai tool thì hệ thống xử lý thế nào).
Mermaid.js (dễ vẽ từ text), PlantUML
Class/Component Diagram
Mô tả cấu trúc code, các module/agent
- Cấu trúc thư mục agents/, tools/, core/.
- Các Class chính: BaseAgent, MarketingTool, MemoryManager.
- Quan hệ: Agent nào sở hữu (has-a) những Tool nào?
Pyreverse (auto-gen từ Python code), StarUML
Deployment Diagram
Mô tả hạ tầng chạy thực tế
- File docker-compose.yml, k8s manifests.
- Danh sách service: Frontend, API Server, LLM Inference, Vector DB, Cache (Redis).
- Cổng kết nối (ports) và giao tiếp nội bộ.
Draw.io, Lucidchart
Activity Diagram
Mô tả luồng xử lý nghiệp vụ phức tạp
- Logic điều hướng (routing logic): Khi nào dùng Agent A, khi nào dùng Agent B?
- Flowchart xử lý lỗi hoặc duyệt nội dung (approval workflow).
Draw.io, Visio
