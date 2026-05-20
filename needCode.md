Dưới đây là bảng ánh xạ chi tiết giữa các mục trong báo cáo và thông tin cần trích xuất từ code, kèm hướng dẫn cụ thể để bạn giao nhiệm vụ cho người phụ trách kỹ thuật. Bạn có thể copy nguyên phần này làm yêu cầu công việc.
📘 CHƯƠNG I: TỔNG QUAN LÝ THUYẾT
(Chủ yếu là tài liệu tham khảo, nhưng cần ví dụ từ code để minh họa thực tế)
Mục
Thông tin cần lấy từ code
Định dạng yêu cầu
1.5 Function Calling
- Định nghĩa tool/function (JSON schema)
- Cách đăng ký tool vào LLM
- Ví dụ prompt hệ thống kích hoạt calling
File config/code định nghĩa tool, đoạn tools=[...] hoặc @tool decorator, log mẫu
1.6 Chat Template
- Cấu trúc tin nhắn (system/user/assistant)
- Cách định dạng context/history
- Prompt wrapper/role mapping
Code xử lý messages, template string, ví dụ request/response JSON
1.7 Fine-tuning LLM
- Dataset format (JSONL/parquet)
- Hyperparameters (lr, epochs, batch_size, max_seq_len)
- Base model & framework (LoRA, QLoRA, SFT, vLLM...)
Script fine-tuning, file config training, 3-5 dòng dataset mẫu, log training
🛠️ CHƯƠNG II: THIẾT KẾ & GIẢI PHÁP
(Trọng tâm kỹ thuật, cần trích xuất cấu trúc & luồng xử lý từ code)
Mục
Thông tin cần lấy từ code
Định dạng yêu cầu
2.2 Kiến trúc tổng thể
- Danh sách module/agent
- Luồng dữ liệu (input → agent → tool → output)
- Thành phần hạ tầng (DB, cache, queue, API gateway)
Sơ đồ component (có thể vẽ từ code), danh sách endpoint, file docker-compose hoặc deployment config
2.3 Lựa chọn công nghệ
- Thư viện/framework chính (LangChain, LlamaIndex, FastAPI, CrewAI, AutoGen...)
- Phiên bản phụ thuộc
- Môi trường chạy (GPU/CPU, cloud, local)
requirements.txt, package.json, pyproject.toml, Dockerfile, output pip freeze
2.4 Thiết kế module/agent
- Code routing/chọn agent
- Quản lý context & memory (vector DB, sliding window, session)
- Input/output spec của từng agent
Cấu trúc thư mục agent, đoạn code orchestrator, ví dụ state management, schema output
2.5 Giải pháp kỹ thuật
- Xử lý lỗi function calling (retry, fallback, validation)
- Giới hạn context/token, cắt ngắn prompt
- Rate limiting, caching, batch processing
Code try/except, middleware, utility function xử lý prompt, config cache/rate-limit
📊 CHƯƠNG III: THỰC NGHIỆM & KẾT QUẢ
(Cần số liệu đo lường thực tế từ code/logs)
Mục
Thông tin cần lấy từ code
Định dạng yêu cầu
3.1 Kiểm tra function calling
- Số lượng test case, độ chính xác (% gọi đúng tool, % sai schema)
- Log trace mẫu (thành công/thất bại)
- Nguyên nhân lỗi phổ biến
File test script, report JSON/CSV, 3 log trace mẫu, bảng tổng hợp kết quả
3.2 Đánh giá hiệu năng
- Latency trung bình/95p (ms)
- Throughput (req/s)
- Token usage (input/output)
- CPU/RAM/GPU utilization, memory leak (nếu có)
Output script benchmark (Locust, k6, custom), log monitoring, bảng số liệu
3.3 Giao diện ứng dụng
- Luồng API gọi từ UI
- State management (session, loading, error)
- Component routing
File route/API call trong frontend, ví dụ request/response, mô tả ngắn cách UI trigger agent
3.4 Kết luận & hướng phát triển
- Giới hạn hiện tại trong code (hardcode, tool thiếu, context limit, chưa hỗ trợ multi-modal...)
- Đề xuất refactor/dọc roadmap
Comment TODO/FIXME, danh sách feature backlog, đoạn code cần tối ưu