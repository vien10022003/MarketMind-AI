# Implementation Plan: Authentication & Data Personalization (No Firebase Auth)

Dựa trên phản hồi của bạn: 
1. Bạn sẽ xóa data cũ, nên không cần lo về dữ liệu "mồ côi".
2. Bạn **KHÔNG muốn dùng Firebase Auth** để tránh rườm rà trong việc setup.

Dưới đây là 2 phương án ĐƠN GIẢN NHẤT để thay thế Firebase Auth:

## Phương án 1: Google Login Trực tiếp (Không qua Firebase Auth)
Sử dụng thư viện `@react-oauth/google` trên Frontend và `google-auth` trên Backend.
- **Ưu điểm:** Vẫn có nút "Đăng nhập bằng Google", rất tiện cho người dùng. Không cần file `.json` cấu hình phức tạp trên Backend.
- **Nhược điểm:** Bạn vẫn bắt buộc phải vào Google Cloud Console để tạo một cái `Client ID` (để Google cho phép trang web của bạn hiển thị nút Đăng nhập).

## Phương án 2: Đăng nhập Bằng Tên đăng nhập/Mật khẩu lưu thẳng vào MongoDB (Zero Setup)
Tự code một hệ thống đăng nhập đơn giản:
- **Ưu điểm:** **Không cần setup bất kỳ dịch vụ bên ngoài nào** (Không Google Cloud, Không Firebase). Hệ thống tự tạo collection `users` trong MongoDB để lưu tài khoản. Mật khẩu được mã hóa (băm) bảo mật.
- **Nhược điểm:** Không có nút "Đăng nhập bằng Google" nhanh chóng, người dùng phải gõ tên đăng nhập và mật khẩu.

---
> [!IMPORTANT]
> **User Review Required:** Bạn muốn tôi làm theo **Phương án 1** (Chịu khó tạo Google Client ID) hay **Phương án 2** (Không setup gì cả, chỉ dùng MongoDB)? 
> Hoặc tôi có thể làm **CẢ HAI** (Vừa có Google, vừa có form đăng ký). Nhưng nếu làm cả hai thì bạn vẫn phải tạo Google Client ID.
> Trả lời từ user: làm cả 2 và tồi sẽ cung cấp Client ID trong env

## Proposed Changes (Giả sử làm cả hai hoặc Phương án 2)

### Frontend (`frontend/src/`)
- Cài đặt thư viện: `npm install @react-oauth/google` (Nếu chọn PA1).
- **[NEW]** `src/components/AuthPage.tsx`: Giao diện form đăng nhập đơn giản.
- **[NEW]** `src/services/authService.ts`: Lưu Token vào `localStorage` và xử lý API login.
- **[MODIFY]** `src/App.tsx`: Chặn màn hình nếu chưa có Token trong `localStorage`.
- **[MODIFY]** `src/services/researchService.ts`: Đính kèm Bearer Token vào header.

### Backend (`backend/`)
- Cài đặt thư viện: `pip install PyJWT passlib` (để tạo token và mã hóa mật khẩu) và `google-auth` (nếu dùng Google).
- **[NEW]** `backend/auth_routes.py`: Chứa API `/api/auth/login` và `/api/auth/register`. Nó sẽ tạo một JWT Token (chuỗi mã hóa) có hạn 30 ngày và gửi về cho React.
- **[NEW]** `backend/auth_middleware.py`: Chứa decorator `@require_auth` để giải mã JWT Token, kiểm tra tính hợp lệ và lấy `user_id`.
- **[MODIFY]** `backend/stage_a/flask_api.py`: Gắn `@require_auth` vào các API lấy/tạo dữ liệu.
- **[MODIFY]** `backend/conversation_manager.py` & `backend/stage_c/campaign_scheduler.py`: Thêm bộ lọc `user_id` vào mọi câu truy vấn MongoDB để đảm bảo "dữ liệu của ai người nấy thấy".
