# 1. Tên đề tài

**Xây dựng hệ thống trợ lý Marketing thông minh sử dụng GenAI và Agentic AI**

---

# 2. Mục tiêu tổng quát

Dự án nhằm xây dựng một hệ thống trợ lý Marketing thông minh hoạt động trên nền tảng web, ứng dụng công nghệ Generative AI (GenAI) kết hợp với Agentic AI để hỗ trợ tự động hóa và tối ưu hóa các hoạt động marketing số.

Hệ thống có khả năng tiếp nhận yêu cầu từ người dùng, phân tích thông tin sản phẩm, nghiên cứu thị trường, xây dựng chiến lược marketing, tạo nội dung quảng cáo và hỗ trợ triển khai chiến dịch trên các nền tảng trực tuyến như Facebook, Shopee, TikTok và Gmail.

---

# 3. Mục tiêu cụ thể

## 3.1. Xây dựng giao diện hệ thống

* Phát triển một ứng dụng web đơn giản với giao diện thân thiện, hỗ trợ tương tác dạng hội thoại (chat-based interface).
* Cho phép người dùng đăng nhập và cấp quyền truy cập đến các nền tảng cần thiết như Facebook, Shopee, TikTok, Gmail (mô phỏng hoặc tích hợp API).
* Hỗ trợ người dùng tải lên dữ liệu đầu vào bao gồm:

  * Thông tin sản phẩm
  * Hình ảnh
  * Tài liệu liên quan

---

## 3.2. Xây dựng luồng tương tác thông minh

* Hệ thống cung cấp hai chế độ hoạt động:

  * Luồng xây dựng chiến dịch marketing theo từng bước
  * Chat trực tiếp với AI

* Trong luồng theo bước, hệ thống sẽ:

  * Thu thập thông tin từ người dùng (sản phẩm, mục tiêu, đối tượng khách hàng, ngân sách,...)
  * Lưu trữ thông tin để đảm bảo tính nhất quán trong quá trình xử lý

---

## 3.3. Xây dựng hệ thống Agentic AI

Hệ thống sử dụng mô hình đa tác nhân (multi-agent system) với một Supervisor điều phối và các Agent chuyên biệt:

### • Supervisor Agent

* Phân tích yêu cầu người dùng
* Phân chia nhiệm vụ cho các agent con
* Theo dõi tiến trình xử lý

---

### • Agent 1 – Phân tích thị trường

* Thu thập và phân tích xu hướng từ các nền tảng (Shopee, Facebook, TikTok, Internet)
* Phân tích đối thủ cạnh tranh
* Phân tích khách hàng mục tiêu
* Xuất báo cáo nghiên cứu thị trường

---

### • Agent 2 – Xây dựng chiến lược

* Đề xuất chiến lược marketing tổng thể
* Xây dựng kế hoạch triển khai (kênh, nội dung, thời gian)
* Tương tác với người dùng để phê duyệt hoặc điều chỉnh chiến lược

---

### • Agent 3 – Tạo nội dung quảng cáo

* Sinh nội dung quảng cáo (bài viết, hình ảnh, video,...) bằng GenAI
* Đề xuất nội dung phù hợp với từng nền tảng
* Hỗ trợ đăng bài quảng cáo (sau khi được người dùng phê duyệt)

---

### • Agent 4 – Quản lý và tối ưu

* Theo dõi và quản lý nội dung quảng cáo đã tạo
* Hỗ trợ điều chỉnh và tối ưu chiến dịch (mô phỏng)
* Quản lý lịch đăng bài và nội dung

---

## 3.4. Xây dựng hệ thống xử lý và hiển thị

* Thiết kế hệ thống hoạt động theo dạng pipeline:

  * Nhận input → phân tích → lập kế hoạch → thực thi → trả kết quả
* Hiển thị tiến trình xử lý theo dạng chat (streaming), cho phép người dùng theo dõi hệ thống đang thực hiện bước nào

---

## 3.5. Các chức năng chính của hệ thống

### • Nghiên cứu và phân tích thị trường

* Tạo báo cáo về thị trường, đối thủ, xu hướng
* Phân tích hành vi và insight khách hàng

### • Xây dựng chiến lược marketing

* Đề xuất kế hoạch marketing tổng thể
* Xây dựng chiến lược nội dung và kênh truyền thông

### • Tạo nội dung quảng cáo

* Sinh bài viết quảng cáo
* Tạo nội dung truyền thông (poster, video, mô tả sản phẩm,...)

### • Hỗ trợ triển khai chiến dịch

* Đề xuất đăng bài trên các nền tảng
* Hỗ trợ quản lý nội dung và lịch đăng

---

# 4. Phạm vi dự án

* Hệ thống tập trung vào việc mô phỏng và hỗ trợ quá trình marketing, không yêu cầu tích hợp đầy đủ API chính thức của các nền tảng (có thể sử dụng mock API).
* Nội dung tạo ra bởi AI mang tính hỗ trợ, không thay thế hoàn toàn chuyên gia marketing.
* Các chức năng phân tích và tối ưu chiến dịch có thể được triển khai ở mức cơ bản hoặc mô phỏng.

---

# 5. Kết quả mong đợi

* Xây dựng được một hệ thống trợ lý marketing hoạt động trên nền web
* Triển khai thành công mô hình Agentic AI với nhiều tác nhân phối hợp
* Tạo ra nội dung marketing tự động có chất lượng
* Hỗ trợ người dùng xây dựng và triển khai chiến dịch marketing hiệu quả hơn

---
