# Cấu trúc Cơ sở dữ liệu MarketMind AI (MongoDB)

Hệ thống MarketMind AI sử dụng MongoDB làm cơ sở dữ liệu chính. Dưới đây là các Collection (Bảng) được định nghĩa trong mã nguồn và giải thích chi tiết ý nghĩa của từng trường dữ liệu.

---

## 1. Collection: `users`
Lưu trữ thông tin xác thực của người dùng và các API Keys cá nhân.

- **`_id`**: *(ObjectId)* ID duy nhất do MongoDB tự tạo.
- **`username`**: *(string)* Tên đăng nhập của người dùng.
- **`password`**: *(string)* Mật khẩu đã được băm (hashed) để bảo mật.
- **`role`**: *(string)* Vai trò của người dùng (ví dụ: `"admin"` hoặc `"user"`).
- **`created_at`**: *(datetime)* Thời điểm tài khoản được tạo.
- **`api_keys`**: *(object)* Chứa các thông tin cấu hình và API key cá nhân hóa. Tất cả đều được mã hóa (AES) trước khi lưu.
  - **`gemini_api_key`**: *(string)* Key của Google Gemini do người dùng tự cung cấp.
  - **`image_gen_api_key`**: *(string)* Key dùng cho việc tạo ảnh.
  - **`discord_webhooks`**: *(array)* Danh sách các webhook Discord tùy chỉnh, mỗi mục chứa `id`, `name`, `url` và `created_at`.

---

## 2. Collection: `conversations`
Lưu trữ toàn bộ lịch sử trò chuyện (chat history) và metadata của tiến trình làm việc (pipeline).

- **`_id`**: *(ObjectId)* ID nội bộ của MongoDB.
- **`conversation_id`**: *(string)* ID định danh cuộc trò chuyện (thường là UUID), dùng để query nhanh.
- **`user_id`**: *(string)* Khóa ngoại trỏ đến ID người dùng trong collection `users` (dành cho multi-user).
- **`title`**: *(string)* Tiêu đề cuộc hội thoại (do LLM tự tạo ra dựa trên prompt đầu tiên).
- **`messages`**: *(array)* Mảng chứa chuỗi tin nhắn trong cuộc hội thoại theo thứ tự. Mỗi tin nhắn là một object:
  - **`id`**: *(string)* ID tin nhắn.
  - **`type`**: *(string)* Loại tin nhắn (ví dụ: `"user"`, `"assistant"`, `"status"`, `"report"`, `"strategy"`...).
  - **`content`**: *(string)* Nội dung văn bản của tin nhắn.
  - **`timestamp`**: *(string)* Thời gian tạo tin nhắn (ISO 8601).
  - **`mongodbId`**: *(string)* (Optional) Trỏ đến ID của báo cáo/chiến lược nếu tin nhắn chứa kết quả chuyên sâu.
  - **`...Data`**: *(object)* (Optional) Dữ liệu dạng JSON đi kèm tùy thuộc vào `type` (ví dụ `reportData`, `planData`, `clarificationData`).
- **`created_at`, `updated_at`, `last_message_at`**: *(string)* Các mốc thời gian của cuộc hội thoại.
- **`message_count`**: *(int)* Tổng số tin nhắn.
- **`stage_a_data`, `stage_b_data`, `stage_c_data`**: *(object)* Chứa dữ liệu ngữ cảnh (context) hoặc bản nháp của từng giai đoạn.

---

## 3. Collection: `stage_a_reports`
Lưu trữ kết quả xuất ra từ Giai đoạn A (Nghiên cứu thị trường).

- **`_id`**: *(ObjectId)* ID báo cáo.
- **`user_id`**: *(string)* Tham chiếu đến `users`.
- **`timestamp`**: *(string)* Thời gian hoàn thành báo cáo.
- **`input_config`**: *(object)* Chứa các thông tin đầu vào, yêu cầu, prompt hoặc nội dung Marketing Form mà người dùng cung cấp.
- **`report`**: *(object)* Dữ liệu báo cáo nghiên cứu đã tổng hợp và format:
  - **`tong_quan_thi_truong`**: *(string)* Phân tích tổng quan.
  - **`phan_tich_doi_thu`**: *(string)* Nhận định đối thủ cạnh tranh.
  - **`xu_huong_nganh`**: *(string)* Xu hướng thị trường.
  - **`phan_khuc_va_insight_khach_hang`**: *(string)* Đặc điểm và insight khách hàng mục tiêu.
  - **`citations`**: *(array)* Các nguồn tham khảo, chứng cứ (URL, trích dẫn) được thu thập từ quá trình tìm kiếm.
- **`metrics`**: *(object)* Lưu số liệu đo lường hiệu năng của LLM Agent (số lần gọi tool, số chứng cứ thu được).

---

## 4. Collection: `stage_b_strategies`
Lưu trữ kết quả xuất ra từ Giai đoạn B (Xây dựng chiến lược Marketing) sau khi người dùng phê duyệt.

- **`_id`**: *(ObjectId)* ID chiến lược.
- **`timestamp`**: *(string)* Thời gian lưu chiến lược.
- **`mongodb_stage_a_id`**: *(string)* Khóa ngoại liên kết tới bản báo cáo gốc trong `stage_a_reports`.
- **`strategy`**: *(object)* Nội dung chi tiết của bản chiến lược marketing (phân tích SWOT, thông điệp USP, kênh triển khai, v.v.).
- **`approved_briefs`**: *(array)* Danh sách các bản tóm tắt nội dung bài đăng (Content Briefs) đã được người dùng chỉnh sửa và đồng ý phê duyệt.

---

## 5. Collection: `campaign_logs`
Lưu trữ nhật ký thực thi chiến dịch ở Giai đoạn C (Tự động đăng bài qua webhook/mạng xã hội).

- **`_id`**: *(ObjectId)* ID log chiến dịch.
- **`campaign_id`**: *(string)* ID của đợt chạy chiến dịch.
- **`timestamp`**: *(string)* Thời gian thực thi.
- **`status`**: *(string)* Trạng thái hiện tại của tiến trình (`"running"`, `"completed"`, `"failed"`).
- **`total_posts`**: *(int)* Tổng số lượng bài đăng (briefs) cần thực thi.
- **`successful_posts`**: *(int)* Số bài đăng thành công.
- **`failed_posts`**: *(int)* Số bài đăng bị lỗi.
- **`platform_results`**: *(object)* Kết quả chi tiết theo từng nền tảng (ví dụ kết quả đăng lên Discord).
- **`errors`**: *(array)* Danh sách các chi tiết lỗi nảy sinh (nếu có) để phục vụ debug.
- **`mongodb_stage_a_id`**: *(string)* Khóa ngoại trỏ ngược về báo cáo Stage A (giúp truy vết dữ liệu của toàn bộ campaign từ gốc đến ngọn).
