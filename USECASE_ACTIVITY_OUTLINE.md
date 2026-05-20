# DÀN Ý BÁO CÁO PHẦN 2.1.3 VÀ 2.1.4

## 2.1.3 ĐẶC TẢ USE CASE & BIỂU ĐỒ USE CASE

### 2.1.3.1 Danh sách Actors (Người thực hiện)

| Actor | Mô tả | Vai trò |
|-------|-------|--------|
| **User (Người dùng)** | Người dùng bình thường, nhân viên marketing | - Tạo yêu cầu nghiên cứu<br>- Xem báo cáo<br>- Duyệt chiến lược<br>- Thực thi chiến dịch<br>- Quản lý lịch sử hội thoại |
| **Admin** | Quản trị viên hệ thống | - Quản lý người dùng<br>- Xem analytics<br>- Cấu hình hệ thống<br>- Quản lý integrations |
| **Tavily Search API** | Dịch vụ tìm kiếm web | - Cung cấp dữ liệu thị trường<br>- Tìm kiếm thông tin sản phẩm<br>- Phân tích đối thủ |
| **DALL-E / Stable Diffusion** | Dịch vụ tạo hình ảnh AI | - Tạo hình ảnh quảng cáo<br>- Tối ưu hóa hình ảnh |
| **Social Media APIs** | Facebook, Shopee, TikTok, Discord | - Đăng bài content<br>- Thu thập analytics<br>- Scheduling posts |
| **LLM (Llama 3 / Gemini)** | Large Language Model | - Phân tích yêu cầu<br>- Tạo kế hoạch<br>- Tổng hợp báo cáo<br>- Tạo content |

### 2.1.3.2 Danh sách Use Cases (Tính năng chính)

#### **NHÓM 1: AUTHENTICATION & CONVERSATION** (Cơ bản)

| # | Use Case | Actor | Mô tả |
|---|----------|-------|-------|
| UC-1 | **Đăng ký / Đăng nhập** | User | Người dùng tạo tài khoản và xác thực thông tin |
| UC-2 | **Tạo cuộc hội thoại mới** | User | Bắt đầu một session nghiên cứu mới |
| UC-3 | **Xem lịch sử hội thoại** | User | Truy cập các cuộc hội thoại trước đó |
| UC-4 | **Lưu / Tải chiến lược** | User | Lưu kết quả Stage B để sử dụng sau |
| UC-5 | **Xóa cuộc hội thoại** | User | Xóa dữ liệu cũ không cần thiết |

#### **NHÓM 2: STAGE A - RESEARCH** (Nghiên cứu thị trường)

| # | Use Case | Actor | Mô tả |
|---|----------|-------|-------|
| UC-6 | **Gửi yêu cầu nghiên cứu** | User | Nhập yêu cầu bằng tự nhiên, hệ thống phân tích ý định |
| UC-7 | **Hệ thống yêu cầu làm rõ** | User, LLM | Nếu yêu cầu chưa đủ rõ, LLM hỏi thêm chi tiết |
| UC-8 | **Chạy Research Pipeline** | LLM, Tavily | Thực hiện Stage A: Plan → ReAct → Evidence Processing → Synthesis |
| UC-9 | **Tìm kiếm thị trường** | Tavily API | Tìm kiếm dữ liệu về sản phẩm, thị trường, xu hướng |
| UC-10 | **Phân tích đối thủ cạnh tranh** | LLM, Tavily | Xác định và phân tích các đối thủ chính |
| UC-11 | **Xác định khách hàng mục tiêu** | LLM | Phân tích và mô tả khách hàng tiềm năng |
| UC-12 | **Tổng hợp báo cáo Market Research** | LLM | Tạo báo cáo chi tiết với suy luận, dữ liệu, kết luận |
| UC-13 | **Lưu báo cáo vào MongoDB** | System | Lưu báo cáo để sử dụng ở Stage B/C |

#### **NHÓM 3: STAGE B - STRATEGY** (Lập chiến lược)

| # | Use Case | Actor | Mô tả |
|---|----------|-------|-------|
| UC-14 | **Chuyển sang Strategy Generation** | User | Nhấn nút "Tạo chiến lược" sau khi có báo cáo Stage A |
| UC-15 | **Phân tích SWOT** | LLM | Xác định Strengths, Weaknesses, Opportunities, Threats |
| UC-16 | **Trích xuất Unique Selling Proposition** | LLM | Xác định điểm bán hàng độc nhất |
| UC-17 | **Xây dựng Buyer Persona** | LLM | Tạo mô tả chi tiết khách hàng lý tưởng |
| UC-18 | **Định nghĩa Content Pillars** | LLM | Xác định 4-5 chủ đề nội dung chính |
| UC-19 | **Lập kế hoạch chiến dịch** | LLM | Xác định timeline, ngân sách, kênh phân phối |
| UC-20 | **Tạo Content Briefs** | LLM | Sinh ra 5-10 brief cho từng nền tảng (Facebook, Shopee, Discord) |
| UC-21 | **Người dùng duyệt briefs** | User | Xem, chỉnh sửa, duyệt hoặc từ chối từng brief |
| UC-22 | **Lưu chiến lược đã duyệt** | System | Lưu vào MongoDB để Stage C sử dụng |

#### **NHÓM 4: STAGE C - CAMPAIGN EXECUTION** (Thực thi chiến dịch)

| # | Use Case | Actor | Mô tả |
|---|----------|-------|-------|
| UC-23 | **Thực thi chiến dịch ngay** | User, LLM, Social APIs | Đăng bài content tất cả briefs được duyệt |
| UC-24 | **Tạo hình ảnh quảng cáo** | DALL-E / Stable Diffusion | Tạo hình ảnh AI dựa trên mô tả brief |
| UC-25 | **Đăng bài lên Facebook** | Facebook API | Publish content + hình ảnh lên Facebook |
| UC-26 | **Đăng bài lên Shopee** | Shopee API | Publish content lên Shopee campaign |
| UC-27 | **Gửi thông báo lên Discord** | Discord Webhook | Gửi kết quả chiến dịch vào Discord channel |
| UC-28 | **Lập lịch đăng bài** | User, Scheduler | Chọn thời gian đăng bài cụ thể thay vì ngay |
| UC-29 | **Theo dõi hiệu suất chiến dịch** | System | Ghi nhận số bài đăng thành công, URL bài viết |
| UC-30 | **Hiển thị kết quả chiến dịch** | System | Trả về danh sách bài đăng với links và stats |

#### **NHÓM 5: ADVANCED FEATURES** (Tính năng nâng cao)

| # | Use Case | Actor | Mô tả |
|---|----------|-------|-------|
| UC-31 | **Multi-turn Conversation** | User, LLM | Người dùng có thể hỏi thêm, làm rõ, điều chỉnh |
| UC-32 | **Chọn mô hình LLM** | User | Chọn giữa Llama, Gemini 2.5, Gemini 3.1 |
| UC-33 | **Xem campaign history** | User | Xem danh sách các chiến dịch đã thực thi |
| UC-34 | **Export báo cáo** | User | Xuất báo cáo dưới dạng PDF, JSON |
| UC-35 | **Real-time streaming** | System | Trả về kết quả theo từng bước (streaming response) |

### 2.1.3.3 Kịch Bản Chính cho từng Use Case - STAGE A

---

## **UC-6: GỬI YÊU CẦU NGHIÊN CỨU**

| Trường | Chi tiết |
|--------|---------|
| **Tên Use Case** | Send Market Research Request |
| **Mã** | UC-6 |
| **Actor chính** | User |
| **Actor phụ** | Frontend, Backend Auth |
| **Điều kiện tiên quyết** | • User đã xác thực thành công (UC-1)<br>• Có JWT token hợp lệ<br>• Conversation session khả dụng (UC-2)<br>• Kết nối internet ổn định |
| **Kịch bản chính** | **1. User nhập yêu cầu**<br>   - User mở giao diện Chat<br>   - Nhập câu hỏi/yêu cầu vào textarea<br>   - Ví dụ: "Tôi muốn mở cửa hàng bán trà sữa tại Hà Nội. Hãy phân tích thị trường, đối thủ, và khách hàng tiềm năng."<br><br>**2. Frontend gửi request**<br>   - User nhấn nút "Send" (hoặc Shift+Enter)<br>   - Frontend xây dựng request payload:<br>   ```json<br>   {<br>     "user_prompt": "Tôi muốn mở cửa hàng bán trà sữa...",<br>     "conversation_history": [...],<br>     "llm_provider": "llama"<br>   }<br>   ```<br>   - POST `/api/research/stage_a` với JWT token<br>   - Thiết lập SSE (Server-Sent Events) listener<br><br>**3. Backend nhận request (trong flask_api.py)**<br>   - `@app.route('/api/research/stage_a', methods=['POST'])`<br>   - Verify JWT token từ header<br>   - Extract `user_prompt` từ request body<br>   - Khởi tạo generator function: `run_stage_a_pipeline_generator()`<br>   - Return Response với content-type: `application/x-ndjson`<br><br>**4. System tự động phân tích ý định (Intent Routing)**<br>   - LLM phân loại: Chat / Knowledge / Research?<br>   - Ví dụ: "Tôi muốn mở cửa hàng..." → Classify as **Research**<br>   - Send streaming event:<br>   ```json<br>   {"status": "progress", "message": "Phân tích ý định: Research"}<br>   ```<br><br>**5. Frontend nhận progress event**<br>   - Parser NDJSON line-by-line<br>   - Hiển thị status message: "Phân tích ý định: Research"<br>   - Show typing indicator<br><br>**6. Quyết định: Cần làm rõ yêu cầu?**<br>   - LLM evaluates: Yêu cầu đủ chi tiết?<br>   - Nếu YES → Tiếp tục UC-8 (Research Pipeline)<br>   - Nếu NO → Trigger UC-7 (Clarification) |
| **Kịch bản ngoại lệ** | **E1: Yêu cầu rỗng**<br>   - Frontend validation: `inputValue.trim() === ""`<br>   - Disable send button, hiển thị placeholder hint<br>   - No request sent to backend<br><br>**E2: JWT token hết hạn**<br>   - Backend: 401 Unauthorized<br>   - Response: `{"status": "error", "message": "Token expired"}`<br>   - Frontend: Redirect to login page (AuthPage)<br>   - User must re-authenticate (UC-1)<br><br>**E3: Network timeout**<br>   - Frontend fetch timeout > 10min<br>   - Show error: "Kết nối bị gián đoạn"<br>   - Allow user to retry<br><br>**E4: Backend server error**<br>   - Backend returns 500<br>   - Response: `{"status": "error", "message": "Server error"}`<br>   - Frontend: Show error bubble + retry button |
| **Ràng buộc kỹ thuật** | • Max length: 5000 characters<br>• Timeout: 600 seconds (10 min)<br>• Content-Type: application/json<br>• Auth: Bearer {JWT_TOKEN}<br>• Streaming format: NDJSON<br>• Supported LLM: llama, gemini-2.5, gemini-3.1 |
| **Dữ liệu input** | `{user_prompt: string, conversation_history?: Array, llm_provider: string}` |
| **Dữ liệu output** | Streaming NDJSON events:<br>• `{status: "progress", message: string}`<br>• Triggers UC-7 hoặc UC-8 tiếp theo |
| **Thời gian thực thi** | ~500ms (intent classification only) |

---

## **UC-8: THỰC THI RESEARCH PIPELINE (Stage A)**

| Trường | Chi tiết |
|--------|---------|
| **Tên Use Case** | Execute Stage A Research Pipeline |
| **Mã** | UC-8 |
| **Actor chính** | LLM (Llama 3.8B / Gemini) |
| **Actor phụ** | Tavily Search API, MongoDB, User |
| **Điều kiện tiên quyết** | • UC-6 đã hoàn tất (User gửi yêu cầu)<br>• Yêu cầu intent = "research"<br>• Yêu cầu đã được làm rõ (UC-7 nếu cần)<br>• LLM provider khả dụng<br>• Tavily API keys valid |
| **Kịch bản chính** | **BƯỚC 1: INTENT ROUTING & VALIDATION**<br>```<br>User: "Tôi muốn mở cửa hàng bán trà sữa tại Hà Nội..."<br>```<br>1.1. Backend nhận request từ UC-6<br>1.2. LLM phân tích: Intention = "market_research"<br>1.3. Extract key info:<br>   - Product: "trà sữa" (bubble tea)<br>   - Location: "Hà Nội" (Hanoi)<br>   - Objective: "mở cửa hàng" (open shop)<br>1.4. Send streaming: `{status: "progress", message: "1. Phân tích yêu cầu: Nghiên cứu thị trường trà sữa tại Hà Nội"}`<br><br>**BƯỚC 2: PLANNING (Lập kế hoạch)**<br>2.1. LLM tạo research plan với 5-7 research questions:<br>```json<br>{<br>  "research_questions": [<br>    "Quy mô và tăng trưởng thị trường trà sữa ở Hà Nội?",<br>    "Các cửa hàng competitors chính là ai?",<br>    "Giá trung bình và phân khúc khách hàng?",<br>    "Xu hướng consumer behavior hiện tại?",<br>    "Vị trí tốt nhất để mở cửa hàng?",<br>    "Yêu cầu giấy phép và chi phí khởi động?"<br>  ],<br>  "search_steps": 6,<br>  "hypotheses": [<br>    "Thị trường trà sữa đang tăng trưởng 15-20%/năm",<br>    "Khách hàng chủ yếu: Gen Z + millennial (18-35 tuổi)",<br>    "Mức giá cạnh tranh: 25,000-35,000 VND/ly"<br>  ]<br>}<br>```<br>2.2. Send streaming: `{status: "plan_completed", plan: {...}}`<br><br>**BƯỚC 3: ReAct LOOP (Reasoning + Acting)**<br>3.1. FOR i = 1 TO max_iterations (typically 6-10):<br><br>   **Iteration 1: Current market size**<br>   - LLM Thought: "Cần tìm dữ liệu về quy mô thị trường trà sữa Hà Nội"<br>   - Action: Call Tavily with query: "Quy mô thị trường trà sữa Hà Nội 2025 2026"<br>   - Tavily returns: 5-10 search results<br>   - Results:<br>     ```<br>     [1] Report: "Vietnamese bubble tea market grows 18% YoY" (relevance: 0.92)<br>     [2] News: "Hanoi bubble tea shop sales boom in 2025" (relevance: 0.88)<br>     [3] Article: "Trà sữa - xu hướng tiêu dùng mới..." (relevance: 0.85)<br>     ```<br>   - LLM processes: Market size ~$45M/year, growth rate 18%<br>   - Send streaming: `{status: "react_completed", react_summary: {iteration: 1, findings: "..."}}`<br><br>   **Iteration 2: Competitor analysis**<br>   - Action: Call Tavily: "Các cửa hàng trà sữa nổi tiếng Hà Nội Highlands Urban Station"<br>   - Results: Top competitors identified<br>   - LLM analyzes: 15+ major competitors, price range 25-40k VND<br>   - Send streaming event<br><br>   **Iteration 3-6: Continue searching**<br>   - Customer demographics, trends, location analysis, regulations, startup costs<br>   - Each iteration: Query → Search → Process → Send event<br><br>3.2. Loop exits when:<br>   - All research questions answered<br>   - OR max iterations reached<br>   - OR user satisfaction threshold met<br><br>**BƯỚC 4: EVIDENCE PROCESSING**<br>4.1. Collect all search results (typically 40-50 from 6 iterations)<br>4.2. Normalize and clean:<br>   - Remove duplicates (same URL or content)<br>   - Remove low-quality sources (relevance < 0.7)<br>   - Filter outdated info<br>4.3. Organize by category:<br>   - Market trends: 8 sources<br>   - Competitor analysis: 12 sources<br>   - Customer insights: 10 sources<br>   - Regulations/costs: 6 sources<br>4.4. Final evidence pool: ~25-30 high-quality sources<br>4.5. Send streaming: `{status: "evidence_ready", evidence_count: {total: 28, valid: 25, filtered_out: 3}}`<br><br>**BƯỚC 5: SYNTHESIS (Tổng hợp báo cáo)**<br>5.1. LLM tạo comprehensive report:<br>```json<br>{<br>  "tong_quan_thi_truong": {<br>    "size": "$45M/year",<br>    "growth_rate": "18% CAGR",<br>    "forecast_2027": "$53M",<br>    "key_drivers": ["Gen Z consumption", "Premium bubble tea trend"]<br>  },<br>  "phan_tich_doi_thu": {<br>    "major_competitors": [<br>      {"name": "Highlands Coffee", "market_share": "22%", "positioning": "Premium"},<br>      {"name": "Urban Station", "market_share": "18%", "positioning": "Trendy"},<br>      {"name": "The Alley", "market_share": "15%", "positioning": "Premium quality"}<br>    ],<br>    "competitive_analysis": "...",<br>    "weakness_opportunities": "..."<br>  },<br>  "khach_hang_muc_tieu": {<br>    "primary": {"age": "18-35", "income": "10-20M VND/month", "behavior": "Digital native, trend-focused"},<br>    "secondary": {"age": "35-50", "income": "20M+ VND/month", "behavior": "Quality-conscious"}<br>  },<br>  "vi_tri_kinh_doanh": {<br>    "best_locations": ["Ba Đình", "Hoàn Kiếm", "Hai Bà Trưng"],<br>    "reasoning": "High foot traffic, target demographic concentration"<br>  },<br>  "khoi_dong_chi_phi": {<br>    "equipment": "50-100M VND",<br>    "location_rent": "20-50M VND/month",<br>    "licenses_permits": "5-10M VND",<br>    "initial_inventory": "10-15M VND"<br>  }<br>}<br>```<br>5.2. Send streaming: `{status: "report_ready", report: {...}}`<br><br>**BƯỚC 6: SAVE & COMPLETE**<br>6.1. Backend lưu report vào MongoDB:<br>   - Collection: `stage_a_reports`<br>   - Document structure:<br>   ```json<br>   {<br>     "_id": ObjectId("..."),<br>     "user_id": "user123",<br>     "conversation_id": "conv_abc123",<br>     "created_at": "2026-05-19T10:30:00Z",<br>     "ttl": 2592000,  // 30 days expiry<br>     "research_query": "Tôi muốn mở cửa hàng bán trà sữa...",<br>     "report_data": {...},<br>     "sources_count": 25,<br>     "processing_time_ms": 245000  // 4 min<br>   }<br>   ```<br>6.2. Generate `mongodb_id` = `ObjectId` của document<br>6.3. Send final streaming event:<br>   ```json<br>   {<br>     "status": "completed",<br>     "message": "✅ Nghiên cứu hoàn tất! Báo cáo đã được lưu.",<br>     "mongodb_id": "507f1f77bcf86cd799439011",<br>     "report": {...},<br>     "processing_time": "4m 5s",<br>     "sources_used": 25<br>   }<br>   ```<br>6.4. Close SSE connection |
| **Kịch bản ngoại lệ** | **E1: LLM initialization fails**<br>   - Cause: GPU out of memory, LLM model not loaded<br>   - Response: `{status: "error", message: "Không thể khởi tạo LLM"}`<br>   - User can retry or choose different LLM provider<br><br>**E2: Tavily API timeout (iteration N)**<br>   - Cause: Network timeout hoặc API overloaded<br>   - Handling: Retry search query 3 times, then skip to next iteration<br>   - LLM uses cached results from previous iterations<br>   - Send: `{status: "warning", message: "Tìm kiếm iteration 3 timeout, tiếp tục với dữ liệu có sẵn"}`<br><br>**E3: Insufficient evidence**<br>   - Cause: All Tavily searches return low relevance results<br>   - Handling: Exit loop early, use whatever evidence collected<br>   - LLM creates report with caveat: "Limited data availability"<br>   - Send: `{status: "warning", message: "Dữ liệu hạn chế, báo cáo được tạo từ 12 sources"}`<br><br>**E4: MongoDB save fails**<br>   - Cause: Database connection error<br>   - Handling: Log error, return report data anyway<br>   - Report still shown to user, but not persisted<br>   - Send: `{status: "warning", message: "Báo cáo không thể lưu tạm thời"}`<br><br>**E5: Execution timeout (> 10 min)**<br>   - Cause: Too complex query or network issues<br>   - Handling: Return partial report with completed iterations<br>   - Send: `{status: "completed_partial", message: "Timeout - báo cáo từ 4/6 steps"}` |
| **Ràng buộc kỹ thuật** | • Max execution time: 10 minutes<br>• Max Tavily searches per request: 50<br>• Evidence relevance threshold: 0.7<br>• Min evidence items for report: 10<br>• Max iterations: 10<br>• Streaming format: NDJSON, 1 event per line<br>• GPU memory: Monitor and clear cache after each major step<br>• MongoDB TTL index: 30 days |
| **Dữ liệu input** | `{user_prompt: string, conversation_history: Array, llm_provider: string}` |
| **Dữ liệu output** | Streaming NDJSON:<br>1. `{status: "progress", message: string}`<br>2. `{status: "plan_completed", plan: Object}`<br>3. `{status: "react_completed", react_summary: Object}` (multiple)<br>4. `{status: "evidence_ready", evidence_count: Object}`<br>5. `{status: "report_ready", report: Object}`<br>6. `{status: "completed", mongodb_id: string, report: Object}` |
| **Thời gian thực thi** | 2-5 phút (tùy độ phức tạp + số Tavily searches) |

---

## **UC-9: TÌM KIẾM & THU THẬP DỮ LIỆU**

| Trường | Chi tiết |
|--------|---------|
| **Tên Use Case** | Market Research Data Collection via Tavily |
| **Mã** | UC-9 |
| **Actor chính** | Tavily Search API |
| **Actor phụ** | LLM (queries), System (processing) |
| **Điều kiện tiên quyết** | • UC-8 đang chạy ReAct loop<br>• LLM đã lập kế hoạch (UC-8 step 2)<br>• Tavily API keys được cấu hình<br>• Internet connection available |
| **Kịch bản chính** | **1. LLM tạo search queries**<br>   Từ research plan, LLM tạo concrete queries:<br>   ```<br>   Query 1: "Quy mô thị trường trà sữa Hà Nội 2025 2026"<br>   Query 2: "Cửa hàng trà sữa nổi tiếng Hà Nội Highlands Urban Station"<br>   Query 3: "Khách hàng trà sữa Việt Nam tâm lý tiêu dùng"<br>   Query 4: "Giá trung bình trà sữa Hà Nội 2025"<br>   Query 5: "Giấy phép kinh doanh cửa hàng trà sữa Hà Nội"<br>   Query 6: "Vị trí kinh doanh tốt Hà Nội trà sữa coffee"<br>   ```<br><br>**2. Frontend sends search query to backend**<br>   (via streaming, LLM decides query content)<br><br>**3. Backend calls Tavily API**<br>   ```python<br>   # Trong UC-8 step 3<br>   results = tavily_client.search(<br>       query="Quy mô thị trường trà sữa Hà Nội...",<br>       include_answer=True,<br>       max_results=10,<br>       search_depth="advanced"<br>   )<br>   ```<br><br>**4. Tavily returns search results**<br>   ```json<br>   {<br>     "answer": "Vietnamese bubble tea market is estimated...",<br>     "results": [<br>       {<br>         "title": "Vietnamese Bubble Tea Market grows 18% YoY",<br>         "url": "https://market-research.example.com/...",<br>         "content": "The bubble tea market in Vietnam...",<br>         "raw_content": "Full HTML/text"<br>       },<br>       {...}  // 9 more results<br>     ],<br>     "response_time": 1.2  // seconds<br>   }<br>   ```<br><br>**5. System processes results**<br>   5.1. Extract key info from each result<br>   5.2. Calculate relevance score (0-1):<br>       ```<br>       - keyword matching: 0-0.5<br>       - source authority: +0-0.3<br>       - freshness (published date): +0-0.2<br>       = final score: 0.85<br>       ```<br>   5.3. Filter: Keep only relevance ≥ 0.7<br>   5.4. Valid results: 8 out of 10<br>       Filtered out: 2 (low relevance)<br>   5.5. Store results temporarily in context<br><br>**6. LLM processes and learns**<br>   6.1. Read the 8 results<br>   6.2. Extract key findings:<br>       - Market size: $45M/year<br>       - Growth: 18% CAGR<br>       - Top 3 competitors: Highlands, Urban Station, The Alley<br>       - Price range: 25-40k VND<br>   6.3. Decide: Does this answer research question?<br>   6.4. If YES → Next question (Loop to next iteration)<br>       If NO → Refine query and retry Tavily<br><br>**7. Repeat until all questions answered**<br>   - Iteration 1-6 follows same pattern<br>   - Total Tavily calls: ~6-8<br>   - Total results collected: 40-80<br>   - Valid results after filtering: 25-30 |
| **Kịch bản ngoại lệ** | **E1: Tavily API returns no results**<br>   - Cause: Query too specific or no data exists<br>   - Handling: LLM reformulates query more broadly<br>   - Retry with: "bubble tea market Hanoi Vietnam"<br>   - If still no results → Mark question as "insufficient data"<br><br>**E2: Tavily timeout (>30 seconds)**<br>   - Cause: API overloaded or network delay<br>   - Handling: Retry 3 times with exponential backoff<br>   - If still timeout → Skip this query, continue with next<br>   - Log warning: "Query timeout - using cached results"<br><br>**E3: Results with invalid URLs**<br>   - Cause: Dead links or malformed URLs<br>   - Handling: Filter out, don't include in evidence<br>   - Count as attempted but failed<br><br>**E4: Duplicate results**<br>   - Cause: Same content from different sources<br>   - Handling: Keep only first occurrence<br>   - De-duplication: Content hash comparison |
| **Ràng buộc kỹ thuật** | • Max results per query: 10<br>• Max queries per request: 50<br>• Search timeout: 30 seconds per query<br>• Relevance threshold: 0.7<br>• Min keyword length: 3 chars<br>• Max keyword length: 200 chars<br>• Caching: Cache results for 24 hours<br>• Rate limiting: 100 requests/min (Tavily limit) |
| **Dữ liệu input** | `{search_query: string}` |
| **Dữ liệu output** | `{results: [{title, url, content, relevance_score}], total_results: number, valid_results: number}` |
| **Thời gian thực thi** | 1-5 seconds per query (depending on complexity) |

---

## **UC-10: PHÂN TÍCH ĐỐI THỦ CẠNH TRANH**

| Trường | Chi tiết |
|--------|---------|
| **Tên Use Case** | Competitive Analysis |
| **Mã** | UC-10 |
| **Actor chính** | LLM (Llama/Gemini) |
| **Actor phụ** | Tavily (search competitor info), MongoDB (storage) |
| **Điều kiện tiên quyết** | • UC-8 ReAct loop running<br>• UC-9 has returned competitor data<br>• LLM context loaded with market info |
| **Kịch bản chính** | **1. LLM identifies competitors**<br>   From Tavily search results, LLM extracts:<br>   - **Direct competitors** (same product, same location):<br>     * Highlands Coffee (trà sữa + coffee)<br>     * Urban Station (trà sữa + bánh)<br>     * The Alley (premium trà sữa)<br>     * Gong Cha (franchise bubble tea)<br>   - **Indirect competitors** (substitute products):<br>     * Coffee shops (Cà Phê Phin, Cộng, La Cafe)<br>     * Smoothie bars (Jus by Julie)<br>     * Energy drink vendors<br><br>**2. Collect competitor data from Tavily**<br>   For each competitor, search:<br>   ```<br>   Query: "Highlands Coffee menu prices locations Hanoi"<br>   Query: "Urban Station review customer feedback"<br>   Query: "The Alley bubble tea business model"<br>   Query: "Gong Cha franchise cost Vietnam"<br>   ```<br>   Results: 20-30 sources about competitors<br><br>**3. LLM analyzes each competitor**<br>   For **Highlands Coffee**:<br>   ```json<br>   {<br>     "name": "Highlands Coffee",<br>     "market_position": "Premium coffee & bubble tea",<br>     "estimated_market_share": "22%",<br>     "price_range": "30-45K VND",<br>     "target_audience": ["Office workers", "Students", "Tourists"],<br>     "strengths": [<br>       "Strong brand recognition",<br>       "Multiple locations (50+ in Hanoi)",<br>       "Quality control",<br>       "Loyalty program"<br>     ],<br>     "weaknesses": [<br>       "Higher prices",<br>       "Slower service during peak hours",<br>       "Less trendy positioning"<br>     ],<br>     "unique_features": [<br>       "Coffee specialty",<br>       "Interior design",<br>       "Private events space"<br>     ],<br>     "competitive_threat": "HIGH",<br>     "recommendation": "Differentiate on trendy product mix + aggressive location strategy"<br>   }<br>   ```<br><br>   For **Urban Station**:<br>   ```json<br>   {<br>     "name": "Urban Station",<br>     "market_position": "Trendy bubble tea + pastry",<br>     "estimated_market_share": "18%",<br>     "price_range": "25-35K VND",<br>     "target_audience": ["Gen Z", "Social media users"],<br>     "strengths": [<br>       "Trendy image, heavy social media presence",<br>       "Pastry combo appeals to younger demographic",<br>       "Fast service",<br>       "Instagram-worthy aesthetic"<br>     ],<br>     "weaknesses": [<br>       "Limited menu variety",<br>       "Inconsistent quality across branches",<br>       "High rent locations"<br>     ],<br>     "unique_features": ["Pastry pairing", "Modern interior"],<br>     "competitive_threat": "HIGH",<br>     "recommendation": "Match on aesthetics, exceed on product quality"<br>   }<br>   ```<br><br>   Similar analysis for The Alley, Gong Cha, etc.<br><br>**4. Create competitive matrix**<br>   ```<br>   ┌─────────────────────────────────────────┐<br>   │ COMPETITIVE POSITIONING MATRIX          │<br>   │                                         │<br>   │ Price (X-axis: Low ← → High)           │<br>   │ Quality (Y-axis: Low ← → High)         │<br>   │                                         │<br>   │     Gong Cha     │  Highlands Coffee  │<br>   │        ●         │        ●           │<br>   │                  │                     │<br>   │   The Alley      │  Urban Station     │<br>   │        ●         │        ●           │<br>   │                  │   [OUR NEW SHOP]   │<br>   │                  │        ?            │<br>   └─────────────────────────────────────────┘<br>   ```<br><br>**5. Identify competitive advantages**<br>   Options for new shop:<br>   - Option A: **Premium quality + High service** (like The Alley)<br>     - Price: 35-45K VND<br>     - Positioning: Premium, Instagram-worthy<br>     - Risk: Difficult to compete with established brands<br><br>   - Option B: **Value + Trendy** (between Urban Station & Gong Cha)<br>     - Price: 25-30K VND<br>     - Positioning: Affordable + Instagram-worthy<br>     - Advantage: Underserved niche<br><br>   - Option C: **High quality + Unique menu** (innovation)<br>     - Price: 30-40K VND<br>     - Positioning: Unique flavors, local ingredients<br>     - Advantage: Product differentiation<br><br>**6. SWOT analysis for new competitor**<br>   ```json<br>   {<br>     "market_gaps": [<br>       "Affordable premium positioning (25-30K)",<br>       "Health-conscious options",<br>       "Local flavor innovation"<br>     ],<br>     "competitor_weaknesses_we_can_exploit": [<br>       "Highlands: Slow service → We offer fast ordering",<br>       "Urban: Inconsistent quality → We ensure quality control",<br>       "The Alley: Expensive → We offer better value"<br>     ],<br>     "market_consolidation_threat": [<br>       "Big chains expanding (Gong Cha, Kung Fu)",<br>       "Coffee shops entering bubble tea market",<br>       "Online delivery platforms (Now, Grab Food)"<br>     ]<br>   }<br>   ```<br><br>**7. Store analysis in LLM context**<br>   - Used for Stage B strategy creation<br>   - Referenced for pricing decisions<br>   - Guides marketing positioning |
| **Kịch bản ngoại lệ** | **E1: No competitor data found**<br>   - Cause: Market is very new or no search results<br>   - Handling: Use generic market assumptions<br>   - Message: "Dữ liệu đối thủ hạn chế"<br><br>**E2: Competitor data outdated**<br>   - Cause: Prices/locations changed since publication<br>   - Handling: Flag as "potentially outdated"<br>   - User warned in report: "Kiểm tra giá hiện tại"<br><br>**E3: Private company (no public data)**<br>   - Cause: Small shops don't publish financial info<br>   - Handling: Use indirect signals (foot traffic, social media followers)<br>   - Estimate based on comparable benchmarks |
| **Ràng buộc kỹ thuật** | • Min competitors to analyze: 3<br>• Max competitors: 20<br>• Min data sources per competitor: 2<br>• Relevance threshold: 0.65 (slightly lower than general research)<br>• Analysis timeout: 5 minutes |
| **Dữ liệu input** | `{market_segment: string, location: string, product_category: string}` |
| **Dữ liệu output** | `{competitors: [{name, position, strengths, weaknesses, threat_level}], positioning_matrix: Object, market_gaps: Array}` |
| **Thời gian thực thi** | 1-2 phút (1-2 Tavily searches + LLM analysis) |

---

## **UC-12: TỔNG HỢP BÁO CÁO MARKET RESEARCH**

| Trường | Chi tiết |
|--------|---------|
| **Tên Use Case** | Synthesize Comprehensive Market Research Report |
| **Mã** | UC-12 |
| **Actor chính** | LLM (Report generation) |
| **Actor phụ** | Evidence pool (UC-9), Competitor analysis (UC-10), MongoDB (storage) |
| **Điều kiện tiên quyết** | • UC-8 ReAct loop completed<br>• UC-9 collected 25+ evidence items<br>• UC-10 completed competitor analysis<br>• LLM has full context of research |
| **Kịch bản chính** | **1. LLM reviews all collected evidence**<br>   Input: 25-30 sources covering:<br>   - Market trends (8 sources)<br>   - Competitor profiles (12 sources)<br>   - Customer data (10 sources)<br>   - Regulatory/cost info (6 sources)<br><br>**2. LLM creates structured report**<br>   ```json<br>   {<br>     "report_title": "Báo Cáo Nghiên Cứu Thị Trường Trà Sữa Tại Hà Nội 2026",<br>     "generated_at": "2026-05-19T10:45:00Z",<br>     "report_sections": {<br>       "1_tong_quan_thi_truong": {<br>         "title": "1. Tổng Quan Thị Trường",<br>         "content": "Thị trường trà sữa Hà Nội đang trải qua giai đoạn phát triển mạnh mẽ...",<br>         "key_metrics": {<br>           "market_size_2025": "$45M",<br>           "growth_rate": "18% CAGR",<br>           "forecast_2027": "$53M",<br>           "number_of_shops": 450,<br>           "shop_growth_rate": "12% YoY"<br>         },<br>         "sources": [3, 7, 12]  // Reference indices<br>       },<br><br>       "2_trend_va_yeu_to_tac_dong": {<br>         "title": "2. Xu Hướng và Yếu Tố Tác Động",<br>         "trends": [<br>           {<br>             "trend": "Premiumization",<br>             "description": "Khách hàng sẵn sàng trả giá cao cho chất lượng tốt",<br>             "impact": "Cơ hội cho sản phẩm cao cấp"<br>           },<br>           {<br>             "trend": "Health consciousness",<br>             "description": "Tăng nhu cầu về đồ uống ít đường, nguyên liệu tự nhiên",<br>             "impact": "Cơ hội phân khúc healthy options"<br>           },<br>           {<br>             "trend": "Social media driven",<br>             "description": "Gen Z chọn sản phẩm dựa trên Instagram/TikTok presence",<br>             "impact": "Bắt buộc phải có strong social media strategy"<br>           }<br>         ],<br>         "sources": [5, 8, 15]<br>       },<br><br>       "3_phan_tich_doi_thu": {<br>         "title": "3. Phân Tích Đối Thủ Cạnh Tranh",<br>         "major_competitors": [<br>           {<br>             "rank": 1,<br>             "name": "Highlands Coffee",<br>             "market_share": "22%",<br>             "positioning": "Premium + multiple products",<br>             "strengths": ["Brand", "Network", "Quality"],<br>             "weaknesses": ["High price", "Slow service"],<br>             "threat_level": "HIGH"<br>           },<br>           {<br>             "rank": 2,<br>             "name": "Urban Station",<br>             "market_share": "18%",<br>             "positioning": "Trendy bubble tea + pastry",<br>             "strengths": ["Social media", "Aesthetic", "Speed"],<br>             "weaknesses": ["Quality inconsistency", "Limited menu"],<br>             "threat_level": "HIGH"<br>           },<br>           {<br>             "rank": 3,<br>             "name": "The Alley",<br>             "market_share": "15%",<br>             "positioning": "Premium quality",<br>             "strengths": ["High quality", "Premium image"],<br>             "weaknesses": ["Very high price", "Limited locations"],<br>             "threat_level": "MEDIUM"<br>           }<br>         ],<br>         "competitive_positioning": "Currently underserved: affordable premium segment (25-30K VND with high quality)",<br>         "sources": [10, 14, 18, 21]<br>       },<br><br>       "4_khach_hang_muc_tieu": {<br>         "title": "4. Khách Hàng Mục Tiêu",<br>         "primary_segment": {<br>           "name": "Gen Z & Young Millennials",<br>           "age_range": "18-28",<br>           "income_monthly": "10-20M VND",<br>           "characteristics": {<br>             "behavior": "Social media-driven, trend-conscious, quality-aware",<br>             "frequency": "3-5 times/week",<br>             "spending_per_visit": "30-40K VND",<br>             "preferred_time": "Evening, weekends",<br>             "decision_factors": ["Aesthetics", "Social media presence", "Product quality"],<br>             "pain_points": ["Too expensive", "Long wait", "Inconsistent quality"]<br>           },<br>           "market_size": "~2.5M in Hanoi",<br>           "penetration": "~15%" // Only 15% regular bubble tea customers<br>         },<br>         "secondary_segment": {<br>           "name": "Office workers",<br>           "age_range": "28-40",<br>           "income_monthly": "20-40M VND",<br>           "characteristics": {<br>             "frequency": "1-2 times/week",<br>             "spending_per_visit": "40-50K VND",<br>             "decision_factors": ["Quality", "Convenience", "Health aspects"],<br>             "prefer_time": "Morning, work breaks"<br>           },<br>           "market_size": "~1.8M in Hanoi"<br>         },<br>         "sources": [6, 9, 19, 22]<br>       },<br><br>       "5_vi_tri_va_phan_bo": {<br>         "title": "5. Vị Trí & Phân Bố Kinh Doanh",<br>         "best_locations": [<br>           {<br>             "district": "Ba Đình",<br>             "score": 9.2,<br>             "reason": "High density of Gen Z, near universities, trendy vibe",<br>             "foot_traffic_daily": "3000-5000",<br>             "rent_per_sqm_month": "800-1200K VND",<br>             "specific_areas": ["Tây Hồ area", "Nghi Tàm street"]<br>           },<br>           {<br>             "district": "Hoàn Kiếm",<br>             "score": 8.8,<br>             "reason": "Tourist hub, high footfall, premium positioning",<br>             "foot_traffic_daily": "4000-6000",<br>             "rent_per_sqm_month": "1200-2000K VND",<br>             "specific_areas": ["Old Quarter", "Hoan Kiem Lake area"]<br>           },<br>           {<br>             "district": "Cầu Giấy",<br>             "score": 8.5,<br>             "reason": "Office workers, shopping centers, good accessibility",<br>             "foot_traffic_daily": "2500-4000",<br>             "rent_per_sqm_month": "700-1000K VND",<br>             "specific_areas": ["Tây Sơn", "Trần Duy Hưng"]<br>           }<br>         ],<br>         "locations_to_avoid": [<br>           "Outer districts (low traffic)",<br>           "Saturated markets (too many competitors)"<br>         ],<br>         "sources": [4, 11, 17]<br>       },<br><br>       "6_khoi_dong_chi_phi_va_tai_chinh": {<br>         "title": "6. Chi Phí Khởi Động & Tài Chính",<br>         "startup_costs": {<br>           "equipment": {<br>             "bubble_tea_machine": "30-50M",<br>             "blenders": "5-10M",<br>             "ice_makers": "10-15M",<br>             "POS_system": "3-5M",<br>             "subtotal": "48-80M"<br>           },<br>           "location": {<br>             "deposit": "20-30M",  // 3-6 months rent upfront<br>             "initial_fit_out": "30-50M",<br>             "subtotal": "50-80M"<br>           },<br>           "inventory": {<br>             "initial_stock": "10-15M"<br>           },<br>           "licenses_permits": {<br>             "business_registration": "1-2M",<br>             "food_safety_cert": "2-3M",<br>             "health_permit": "1-2M",<br>             "subtotal": "4-7M"<br>           },<br>           "marketing_launch": "5-10M",<br>           "working_capital": "15-20M",<br>           "total_required": "132-212M VND"<br>         },<br>         "unit_economics": {<br>           "average_selling_price": "32K VND",<br>           "unit_cost": "8K VND",<br>           "gross_margin": "75%",<br>           "daily_target_sales": "200 cups",<br>           "daily_revenue": "6.4M VND",<br>           "monthly_revenue": "192M VND",<br>           "monthly_operational_cost": "60M VND",  // Rent 30M + Labor 20M + Utilities 5M + etc<br>           "monthly_profit": "84M VND",<br>           "breakeven_months": "~2 months"<br>         },<br>         "sources": [2, 13, 20, 24]<br>       },<br><br>       "7_giay_phep_va_quy_dinh": {<br>         "title": "7. Giấy Phép & Quy Định",<br>         "required_licenses": [<br>           "Business Registration Certificate",<br>           "Food Safety & Hygiene Certificate",<br>           "Health Permit from Department of Health",<br>           "Labor Registration (if hiring employees)"<br>         ],<br>         "regulations": [<br>           "Food hygiene standards per Vietnam Food Safety Law",<br>           "Ingredient source traceability",<br>           "Working hours restrictions (typically 6am-11pm)",<br>           "Waste management & environmental compliance"<br>         ],<br>         "approval_timeline": "3-4 weeks",<br>         "sources": [1, 25]<br>       },<br><br>       "8_khuyến_nghi_va_hang_dong": {<br>         "title": "8. Khuyến Nghị & Hành Động",<br>         "recommended_positioning": "Premium-Affordable Bubble Tea: High quality (materials & taste) + Trendy (aesthetics & social media) + Competitive price (25-30K VND)",<br>         "key_success_factors": [<br>           "Strong social media presence (Instagram/TikTok) with daily content",<br>           "Quality consistency across all products",<br>           "Unique flavor innovations (local ingredients, seasonal specials)",<br>           "Fast service during peak hours",<br>           "Strategic location in Gen Z-dense areas"<br>         ],<br>         "immediate_actions": [<br>           "1. Scout top 3-5 locations, negotiate rent",<br>           "2. Source equipment suppliers, get quotes",<br>           "3. Create prototype menu with 15-20 SKUs",<br>           "4. Design brand identity + social media assets",<br>           "5. Apply for licenses immediately (3-4 weeks lead time)",<br>           "6. Develop marketing launch plan"<br>         ],<br>         "timeline": "4-6 months to opening"<br>       }<br>     },<br><br>     "summary_statistics": {<br>       "total_sources_analyzed": 25,<br>       "total_research_duration": "4 minutes 5 seconds",<br>       "tavily_searches_performed": 6,<br>       "tavily_results_collected": 62,<br>       "results_after_filtering": 25,<br>       "evidence_quality_score": 0.82<br>     },<br><br>     "citations": [<br>       "[1] 'Vietnamese Bubble Tea Market grows 18% YoY' - Market Research Org, 2026",<br>       "[3] 'Hanoi bubble tea shop sales boom in 2025' - Vietnam News, 2025",<br>       "... (23 more citations)"<br>     ]<br>   }<br>   ```<br><br>**3. Format report for readability**<br>   - Add section headers with emoji<br>   - Create summary tables<br>   - Highlight key numbers<br>   - Include action items<br><br>**4. Prepare for display to user**<br>   - Create plain text version for chat bubble<br>   - Create detailed JSON version for storage<br>   - Create visualizable sections (tables, metrics)<br><br>**5. Save to MongoDB**<br>   ```python<br>   stage_a_reports.insert_one({<br>       "_id": ObjectId(),<br>       "user_id": "user123",<br>       "conversation_id": "conv_abc123",<br>       "created_at": datetime.now(),<br>       "report_data": report_json,  // Full report<br>       "ttl": 2592000,  // 30 days<br>       "sources_count": 25,<br>       "processing_time_ms": 245000<br>   })<br>   ```<br><br>**6. Stream completion event**<br>   ```json<br>   {<br>     "status": "report_ready",<br>     "message": "✅ Báo cáo sẵn sàng!",<br>     "report": {...}  // Full report object<br>   }<br>   ```<br><br>   Later (after all stages):<br>   ```json<br>   {<br>     "status": "completed",<br>     "message": "Hoàn tất! Bạn muốn lập chiến lược tiếp theo không?",<br>     "mongodb_id": "507f1f77bcf86cd799439011"<br>   }<br>   ``` |
| **Kịch bản ngoại lệ** | **E1: Missing data for certain section**<br>   - Cause: Tavily didn't return data for regulatory section<br>   - Handling: Mark as "Data not available"<br>   - Message: "Thông tin giấy phép cần được xác nhận thêm"<br><br>**E2: Report generation timeout**<br>   - Cause: LLM processing too slow<br>   - Handling: Return partial report with available sections<br>   - Message: "Báo cáo tạo từ 6/8 sections"<br><br>**E3: MongoDB connection error on save**<br>   - Cause: Database unavailable<br>   - Handling: Return report to user anyway<br>   - Message: "Báo cáo hiển thị nhưng không thể lưu tạm thời"<br>   - Data still available in memory for Stage B |
| **Ràng buộc kỹ thuật** | • Report format: Comprehensive JSON object<br>• Min sections: 6 (if data available)<br>• Report size limit: 2MB<br>• Citations required: min 10<br>• Evidence traceability: Include source URLs<br>• MongoDB TTL: 30 days<br>• Generation timeout: 5 minutes |
| **Dữ liệu input** | `{evidence_pool: Array, competitor_analysis: Object, market_data: Object}` |
| **Dữ liệu output** | Comprehensive report object with 8+ sections, citations, key metrics, recommendations |
| **Thời gian thực thi** | 1-2 phút (LLM synthesis) |

---

### 2.1.3.4 Mối quan hệ giữa các Use Cases

#### **INCLUDE (Bao gồm - bắt buộc)**
```
UC-8 (Research Pipeline) INCLUDE UC-9 (Tìm kiếm)
UC-8 INCLUDE UC-10 (Phân tích đối thủ)
UC-8 INCLUDE UC-12 (Tổng hợp báo cáo)

UC-21 (Duyệt briefs) INCLUDE UC-1 (Đăng nhập) - phải xác thực
UC-23 (Thực thi chiến dịch) INCLUDE UC-1 (Đăng nhập)
UC-23 (Thực thi chiến dịch) INCLUDE UC-24 (Tạo hình ảnh)

UC-28 (Lập lịch) INCLUDE UC-21 (Duyệt briefs) - phải duyệt trước
```

#### **EXTEND (Mở rộng - tùy chọn)**
```
UC-6 (Gửi yêu cầu) EXTEND UC-7 (Yêu cầu làm rõ)
  - Nếu yêu cầu không đủ rõ → hỏi thêm

UC-23 (Thực thi) EXTEND UC-27 (Discord notification)
  - Nếu có webhook Discord → gửi thông báo

UC-21 (Duyệt briefs) EXTEND UC-34 (Export)
  - Người dùng có thể export briefs sau khi duyệt

UC-29 (Theo dõi) EXTEND UC-33 (View history)
  - Hiển thị chi tiết stats của chiến dịch
```

### 2.1.3.4 Bảng mô tả Use Cases chi tiết (3 use case quan trọng nhất)

#### **UC-8: Chạy Research Pipeline (Stage A)**

| Thuộc tính | Giá trị |
|-----------|--------|
| **Tên** | Run Stage A Research Pipeline |
| **Actor** | User, LLM, Tavily API |
| **Pre-condition** | User đã đăng nhập, yêu cầu hợp lệ |
| **Trigger** | User gửi yêu cầu nghiên cứu (UC-6) |
| **Main Flow** | 1. LLM nhận yêu cầu<br>2. LLM lập kế hoạch (Planning)<br>3. ReAct loop: LLM gọi Tavily search<br>4. Tavily trả dữ liệu<br>5. LLM xử lý evidence<br>6. LLM tổng hợp báo cáo<br>7. Lưu báo cáo vào MongoDB |
| **Alternative Flow** | Nếu yêu cầu chưa rõ → UC-7 (Clarification) |
| **Post-condition** | Báo cáo Stage A được tạo, user có thể xem |
| **Thời gian** | ~2-5 phút (tùy độ phức tạp) |

#### **UC-20: Tạo Content Briefs (Stage B)**

| Thuộc tính | Giá trị |
|-----------|--------|
| **Tên** | Generate Content Briefs |
| **Actor** | LLM |
| **Pre-condition** | Chiến lược đã được xác định (SWOT, USP, Persona, Pillars) |
| **Trigger** | User nhấn "Tạo Content Briefs" |
| **Main Flow** | 1. LLM nhận: Target audience + Content pillars<br>2. LLM tạo 5-10 briefs<br>3. Mỗi brief bao gồm:<br>   - Platform (Facebook, Shopee, Discord)<br>   - Tiêu đề<br>   - Nội dung<br>   - CTA (Call-to-action)<br>   - Mô tả hình ảnh<br>4. Hiển thị briefs cho user duyệt |
| **Post-condition** | Briefs được hiển thị, user có thể sửa/duyệt |

#### **UC-23: Thực thi Chiến dịch (Stage C)**

| Thuộc tính | Giá trị |
|-----------|--------|
| **Tên** | Execute Campaign (Immediate) |
| **Actor** | User, LLM, Social Media APIs |
| **Pre-condition** | User đã duyệt briefs (UC-21), có hình ảnh |
| **Trigger** | User nhấn "Thực thi ngay" |
| **Main Flow** | 1. Với mỗi brief được duyệt:<br>2. Gọi DALL-E → tạo hình ảnh<br>3. Gọi Facebook API → đăng bài<br>4. Gọi Shopee API → đăng bài<br>5. Gọi Discord → gửi notification<br>6. Ghi lại URL + status<br>7. Trả về danh sách kết quả cho user |
| **Alternative Flow** | Nếu skip_image_generation=true → dùng hình ảnh sẵn |
| **Post-condition** | Bài viết được đăng lên tất cả nền tảng, user thấy kết quả |
| **Thời gian** | ~2-10 phút tùy số briefs |

### 2.1.3.5 Use Case Diagram (PlantUML)

```
@startuml UseCase Diagram
!theme amiga
skinparam backgroundColor #FFFACD

actor User
actor Admin
participant "LLM\n(Llama/Gemini)" as LLM
participant "Tavily\nSearch API" as Search
participant "DALL-E\n/Stable Diff" as ImageGen
participant "Social APIs\n(FB/Shopee/Discord)" as SocialAPI
database MongoDB

rectangle "MarketMind AI System" {
    
    ' ─── Authentication & Conversation ───
    usecase UC1 as "Đăng ký/Đăng nhập"
    usecase UC2 as "Tạo cuộc hội thoại"
    usecase UC3 as "Xem lịch sử"
    usecase UC5 as "Xóa hội thoại"
    
    ' ─── Stage A ───
    usecase UC6 as "Gửi yêu cầu\nRoom A"
    usecase UC7 as "Yêu cầu làm rõ"
    usecase UC8 as "Research Pipeline"
    usecase UC9 as "Tìm kiếm thị trường"
    usecase UC10 as "Phân tích đối thủ"
    usecase UC12 as "Tổng hợp báo cáo"
    
    ' ─── Stage B ───
    usecase UC14 as "Tạo chiến lược"
    usecase UC15 as "Phân tích SWOT"
    usecase UC16 as "Trích USP"
    usecase UC17 as "Xây Persona"
    usecase UC18 as "Định Content Pillars"
    usecase UC19 as "Lập kế hoạch"
    usecase UC20 as "Tạo Briefs"
    usecase UC21 as "Duyệt Briefs"
    
    ' ─── Stage C ───
    usecase UC23 as "Thực thi\nChiến dịch"
    usecase UC24 as "Tạo hình ảnh"
    usecase UC25 as "Đăng Facebook"
    usecase UC26 as "Đăng Shopee"
    usecase UC27 as "Discord Alert"
    usecase UC28 as "Lập lịch"
    usecase UC29 as "Theo dõi kết quả"
    
    ' ─── Advanced ───
    usecase UC31 as "Multi-turn chat"
    usecase UC32 as "Chọn LLM"
    usecase UC33 as "Xem campaign history"
}

' ─── Actor relationships ───
User --> UC1
User --> UC2
User --> UC3
User --> UC5
User --> UC6
User --> UC14
User --> UC21
User --> UC23
User --> UC28
User --> UC31
User --> UC32
User --> UC33

Admin --> UC1

' ─── Include relationships ───
UC1 ..|> UC6 : include
UC1 ..|> UC23 : include
UC6 ..|> UC8 : include

UC8 ..|> UC9 : include
UC8 ..|> UC10 : include
UC8 ..|> UC12 : include

UC23 ..|> UC24 : include
UC23 ..|> UC25 : include
UC23 ..|> UC26 : include

UC21 ..|> UC1 : include
UC28 ..|> UC21 : include

' ─── Extend relationships ───
UC6 --|> UC7 : extend
UC23 --|> UC27 : extend
UC29 --|> UC33 : extend

' ─── Dependencies ───
UC14 --> UC8
UC20 --> UC14
UC21 --> UC20
UC23 --> UC21

' ─── External systems ───
UC9 --> Search
UC24 --> ImageGen
UC25 --> SocialAPI
UC26 --> SocialAPI
UC27 --> SocialAPI
UC12 --> MongoDB

@enduml
```

---



## 2.1.4 BIỂU ĐỒ HOẠT ĐỘNG (ACTIVITY DIAGRAM)

### 2.1.4.1 Tổng quan luồng hoạt động chính

```
┌─────────────────────────────────────────────────────────────┐
│                    USER STARTS REQUEST                      │
│                  (Input research query)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  SYSTEM AUTHENTICATE USER  │
        │  (Check JWT token, roles)  │
        └────┬───────────────────┬───┘
             │ Valid             │ Invalid
             ▼                   ▼
        [Process]            [Error 401]
             │                   │
             └───────┬───────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  INTENT ROUTING (Supervisor)   │
        │  Analyze user message:         │
        │  - Intent: Chat/Knowledge/     │
        │    Research?                   │
        └────┬────────┬─────────┬────────┘
             │        │         │
    Chat     │        │         │ Research
             ▼        ▼         ▼
        [Chat]   [Search]  [Pipeline]
             │        │         │
             └────────┴─────────┘
                      │
            ┌─────────▼────────┐
            │  START STAGE A   │
            │  (Research       │
            │   Pipeline)      │
            └─────────┬────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   PLANNING PHASE            │
        │  LLM lập kế hoạch:          │
        │  - Research questions       │
        │  - Hypotheses               │
        │  - Search steps             │
        └──────────┬──────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │     ReAct LOOP              │
        │  (Reason + Act)             │
        │  ├─ LLM thinks              │
        │  ├─ Call Tavily search      │
        │  ├─ Get results             │
        │  └─ Repeat until done       │
        └──────────┬──────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │  EVIDENCE PROCESSING        │
        │  - Normalize data           │
        │  - Filter relevance         │
        │  - Remove duplicates        │
        └──────────┬──────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │    SYNTHESIS PHASE          │
        │  LLM creates report:        │
        │  - Market overview          │
        │  - Competitor analysis      │
        │  - Target audience          │
        │  - Recommendations          │
        └──────────┬──────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │  SAVE TO MONGODB            │
        │  Store report for Stage B   │
        └──────────┬──────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │  DISPLAY TO USER            │
        │  (Streaming + Final report) │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────┐
        │ User Decision:      │
        │ - Next action?      │
        │ - Generate strategy?│
        │ - Save & exit?      │
        └─────────────────────┘
```

### 2.1.4.2 Chi tiết Activity Diagram - STAGE A (Research)

**Swimlane Version:**

```
┌──────────────┬─────────────┬─────────────┬─────────────────┐
│   User       │   System    │   LLM       │  External API   │
├──────────────┼─────────────┼─────────────┼─────────────────┤
│              │             │             │                 │
│ Input query  │             │             │                 │
│   ────►      │ Validate    │             │                 │
│              │   input     │             │                 │
│              │   ────►     │             │                 │
│              │             │ Understand  │                 │
│              │             │  request    │                 │
│              │             │   ────►     │                 │
│              │             │ (clarify)   │                 │
│              │◄────────────│  (optional) │                 │
│   ◄──────────│ Ask details │             │                 │
│              │             │             │                 │
│ Confirm      │             │             │                 │
│  details     │             │             │                 │
│   ────►      │ Save context│             │                 │
│              │   ────►     │             │                 │
│              │             │ Plan steps  │                 │
│              │             │   ────►     │                 │
│              │             │ [Planning]  │                 │
│              │             │   ────►     │                 │
│   (Waiting)  │ Streaming   │ Loop: Think │                 │
│   ◄──────────│ progress    │ + Act       │                 │
│              │   ◄────────┤   ────►     │ Call Tavily     │
│              │            │            │ Search          │
│              │            │            │ ◄───────────────│
│              │            │ Process    │ Return results  │
│              │            │ evidence   │ ──────────────►│
│              │            │   ────►    │                 │
│              │ Streaming  │ Next       │                 │
│   ◄──────────│ ReAct      │ iteration?  │                 │
│ Step N       │ results ◄──┤   ───┐     │                 │
│              │            │       └────│─── (repeat)     │
│              │            │           ◄│─── (exit loop)  │
│              │            │ Synthesize │                 │
│              │            │ report     │                 │
│              │ Streaming  │   ────►    │                 │
│   ◄──────────│ final ◄────┤ Report     │                 │
│ Report +     │ report     │ ready      │                 │
│ Save option  │   ────►    │            │                 │
│              │ MongoDB    │            │                 │
│              │ save       │            │                 │
│              │ (optional) │            │                 │
│ Done/Next    │   ────►    │ Completed  │                 │
│  ────►       │ (continue  │            │                 │
│              │  to Stage  │            │                 │
│              │  B?)       │            │                 │
└──────────────┴─────────────┴─────────────┴─────────────────┘
```

### 2.1.4.3 Chi tiết Activity Diagram - STAGE B (Strategy)

```
┌────────────────────────────────────────────┐
│         STAGE B: STRATEGY GENERATION        │
│  Input: Stage A Report + User Input        │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │ 1. SWOT ANALYSIS             │
    │ LLM analyzes market data:    │
    │ - Strengths                  │
    │ - Weaknesses                 │
    │ - Opportunities              │
    │ - Threats                    │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 2. USP EXTRACTION            │
    │ Unique Selling Proposition   │
    │ What sets product apart?     │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 3. BUYER PERSONA             │
    │ - Demographics               │
    │ - Pain points                │
    │ - Motivations                │
    │ - Buying behavior            │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 4. CONTENT PILLARS           │
    │ 4-5 main content themes:     │
    │ - Pillar 1: Education        │
    │ - Pillar 2: Entertainment    │
    │ - Pillar 3: Inspiration      │
    │ - Pillar 4: Community        │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 5. CAMPAIGN PLAN             │
    │ - Timeline (weeks/months)    │
    │ - Budget allocation          │
    │ - Channels (FB/Shopee/..)    │
    │ - KPIs to track              │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 6. GENERATE CONTENT BRIEFS   │
    │ For each content pillar:     │
    │ - Title                      │
    │ - Copy                       │
    │ - CTA                        │
    │ - Image description          │
    │ - Platform (FB/Shopee)       │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ 7. PRESENT TO USER           │
    │ - Show strategy summary      │
    │ - Show each brief            │
    │ - Allow editing              │
    └──────────┬───────────────────┘
               │
        ┌──────▼────────┐
        │ User Decision │
        │ - Edit        │
        │ - Approve All │
        │ - Reject      │
        └───────────────┘
```

### 2.1.4.4 Chi tiết Activity Diagram - STAGE C (Campaign Execution)

```
USER APPROVES BRIEFS
         │
         ▼
┌────────────────────────────────────────┐
│   STAGE C: CAMPAIGN EXECUTION          │
│   Input: Approved Content Briefs       │
│   Mode: Immediate OR Scheduled         │
└────────┬───────────────────────────────┘
         │
         ├─ Immediate? ──► [Execute Now]
         │
         └─ Scheduled? ──► [Queue for APScheduler]
                              │
                              ▼
                         [Wait for time]
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  FOR EACH APPROVED BRIEF:              │
         │  ┌─────────────────────────────────┐  │
         │  │ STEP 1: GENERATE IMAGE          │  │
         │  │ Call DALL-E with brief.image_   │  │
         │  │ description                     │  │
         │  │                                 │  │
         │  │ image_url ◄─ DALL-E response  │  │
         │  └──────┬──────────────────────────┘  │
         │         │                             │
         │         ▼                             │
         │  ┌─────────────────────────────────┐  │
         │  │ STEP 2: POST TO FACEBOOK        │  │
         │  │ Call FB API:                    │  │
         │  │ - page_id, message, image_url  │  │
         │  │                                 │  │
         │  │ post_id ◄─ FB API response    │  │
         │  │ post_url = facebook.com/...    │  │
         │  └──────┬──────────────────────────┘  │
         │         │                             │
         │         ▼                             │
         │  ┌─────────────────────────────────┐  │
         │  │ STEP 3: POST TO SHOPEE          │  │
         │  │ Call Shopee API:                │  │
         │  │ - campaign_id, content, image   │  │
         │  │                                 │  │
         │  │ shopee_post_id ◄─ Shopee API  │  │
         │  │ post_url = shopee.vn/...       │  │
         │  └──────┬──────────────────────────┘  │
         │         │                             │
         │         ▼                             │
         │  ┌─────────────────────────────────┐  │
         │  │ STEP 4: POST TO DISCORD         │  │
         │  │ Call Discord Webhook:          │  │
         │  │ - embed message                 │  │
         │  │ - image preview                 │  │
         │  │ - links to FB/Shopee            │  │
         │  │                                 │  │
         │  │ status = success/failed         │  │
         │  └──────┬──────────────────────────┘  │
         │         │                             │
         │         ▼                             │
         │  ┌─────────────────────────────────┐  │
         │  │ STEP 5: RECORD RESULTS          │  │
         │  │ Save to MongoDB:                │  │
         │  │ - brief_id                      │  │
         │  │ - image_url                     │  │
         │  │ - post_urls (FB, Shopee)        │  │
         │  │ - status (success/failed)       │  │
         │  │ - timestamp                     │  │
         │  └──────┬──────────────────────────┘  │
         │         │                             │
         │         ▼ (Next brief)                │
         └─────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────────────┐
         │ CAMPAIGN COMPLETED          │
         │ Summary:                    │
         │ - X briefs posted           │
         │ - Y posts successful        │
         │ - Z posts failed            │
         │ - Links to all posts        │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────────────────┐
         │ DISPLAY TO USER             │
         │ - Show results              │
         │ - Show post links           │
         │ - Option to view analytics  │
         └─────────────────────────────┘
```

### 2.1.4.5 Error Handling & Decision Flows

#### **Error Handling Workflow**

```
┌─────────────────────────────┐
│ ANY STEP FAILS              │
│ (Network, API, LLM error)   │
└────────────┬────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ CATCH EXCEPTION    │
    │ Log error details  │
    └────────┬───────────┘
             │
      ┌──────▼──────┬─────────────┐
      │             │             │
    Retry?      Fallback?    Skip/Abort?
      │             │             │
      ▼             ▼             ▼
   [Retry]   [Use default] [Continue with
    max 3     or cache       next brief]
    times     result
      │             │             │
      └─────────────┴─────────────┘
             │
             ▼
    ┌────────────────────┐
    │ NOTIFY USER        │
    │ Error message +    │
    │ Continue option    │
    └────────────────────┘
```

#### **User Decision Points**

```
┌──────────────────────────────────────┐
│ 1. AFTER CLARIFICATION (UC-7)        │
│                                      │
│    Proceed with research?            │
│    ├─ YES → Continue to Stage A      │
│    └─ NO  → Revise & resubmit        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 2. AFTER STAGE A REPORT              │
│                                      │
│    Satisfied with research?          │
│    ├─ YES → Go to Stage B (Strategy) │
│    ├─ NO  → Ask follow-up Q          │
│    └─ SAVE → Store for later         │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 3. AFTER CONTENT BRIEFS (Stage B)    │
│                                      │
│    Accept briefs?                    │
│    ├─ APPROVE ALL → Stage C          │
│    ├─ EDIT & RE-GENERATE             │
│    ├─ SELECT SOME → Execute selected │
│    └─ REJECT & REVISE                │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 4. BEFORE POSTING (Stage C)          │
│                                      │
│    When to post?                     │
│    ├─ POST NOW → Execute immediately │
│    ├─ SCHEDULE → Set specific times  │
│    └─ CANCEL  → Exit                 │
└──────────────────────────────────────┘
```

### 2.1.4.6 Flowchart: Intent Routing (Supervisor Agent)

```
┌────────────────────────────────────┐
│ USER SENDS MESSAGE                 │
│ (Text input from frontend)         │
└──────────────┬─────────────────────┘
               │
               ▼
     ┌─────────────────────────┐
     │ SUPERVISOR AGENT        │
     │ Analyze message         │
     │ (NLU - Intent detection)│
     └──────────┬──────────────┘
                │
    ┌───────────┼───────────┬──────────┐
    │           │           │          │
   Chat?    Knowledge?   Research?   Other?
    │           │           │          │
    ▼           ▼           ▼          ▼
 ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐
 │ Path 1 │ │ Path 2 │ │ Path 3   │ │ Error  │
 │ Chat   │ │ Search │ │ Full     │ │ Handler│
 │Handler │ │Handler │ │Pipeline  │ │        │
 └────────┘ └────────┘ └──────────┘ └────────┘
    │           │           │          │
    ▼           ▼           ▼          ▼
 [Chat Mode] [Web Search] [Stage A→] [Clarify]
             (Tavily)      Stage B→   or Error
                           Stage C    Response
```

### 2.1.4.7 Concurrent Processing & Streaming

```
┌─────────────────────────────────┐
│ REQUEST RECEIVED                │
└──────────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ OPEN SERVER-SENT EVENTS │
    │ (SSE Stream to client)  │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │ BACKGROUND PROCESSING   │
    │ (Flask generator function)
    │                         │
    ├─ Step 1: Planning      │
    │  └─ Send: progress msg │
    │                        │
    ├─ Step 2: ReAct        │
    │  └─ Send: each search │
    │     result as it comes │
    │                        │
    ├─ Step 3: Evidence     │
    │  └─ Send: filtering   │
    │     progress          │
    │                        │
    └─ Step 4: Synthesis    │
       └─ Send: final report│
               │
               ▼
    ┌─────────────────────────┐
    │ CLOSE SSE STREAM        │
    │ (Connection complete)   │
    └─────────────────────────┘
```

---

## 2.1.5 BẢNG TỔNG HỢP: MAPPING ACTORS & USE CASES

| Actor | Sử dụng Use Case | Bắt đầu lúc | Kết thúc lúc |
|-------|-----------------|----------|-------------|
| **User** | UC-1, 2, 3, 5, 6, 7, 14, 21, 23, 28, 31, 32, 33 | Đăng nhập | Xem kết quả cuối cùng |
| **Admin** | UC-1 + quản lý users | Đăng nhập | Xem reports/analytics |
| **LLM** | UC-7, 8, 10, 12, 15, 16, 17, 18, 19, 20, 24 | Khi được gọi | Trả lại kết quả |
| **Tavily API** | UC-9 | LLM gọi search | Trả lại search results |
| **DALL-E** | UC-24 | Stage C bắt đầu | Trả lại image URL |
| **Social APIs** | UC-25, 26, 27 | Đăng bài | Trả lại post URL + stats |
| **MongoDB** | UC-13, 22 | Lưu dữ liệu | Trả lại OK/error |

---

## 2.1.6 SEQUENCE DIAGRAM: FULL CAMPAIGN FLOW

```
User    Frontend   Backend   LLM    Tavily   DALL-E   FB API   MongoDB
 │         │         │       │        │        │        │        │
 │─Research─►│        │       │        │        │        │        │
 │          │─POST───►│       │        │        │        │        │
 │          │        │─Auth──┤        │        │        │        │
 │          │        │─Plan──►│        │        │        │        │
 │          │        │ ReAct ─────────►│        │        │        │
 │          │◄SSE Progress◄──┤        │        │        │        │
 │          │        │ Evidence──────►│        │        │        │
 │          │        │ Synthesis──────►│        │        │        │
 │          │        │ Save Report────────────────────────────────►│
 │          │◄─Final Report───┤        │        │        │        │
 │          │        │        │        │        │        │        │
 │ Approve ──►│        │        │        │        │        │        │
 │          │─POST───►│        │        │        │        │        │
 │          │        │─Strategy─┐      │        │        │        │
 │          │        │ SWOT     │      │        │        │        │
 │          │        │ USP      │      │        │        │        │
 │          │        │ Persona  ├──────►│        │        │        │
 │          │        │ Briefs   │       │        │        │        │
 │          │◄Briefs─┤        │        │        │        │        │
 │          │        │        │        │        │        │        │
 │ Approve Briefs──►│        │        │        │        │        │
 │          │─POST───►│        │        │        │        │        │
 │          │        │─Generate Image─────────────────►│        │
 │          │        │◄Image URL─────◄│        │        │        │
 │          │        │─POST to FB────────────────────────────►│
 │          │        │◄Post URL─────────────────────┤        │
 │          │        │─Save Campaign─────────────────────────────►│
 │          │◄Campaign Complete◄──┤        │        │        │
 │◄Results──│        │        │        │        │        │        │
 │          │        │        │        │        │        │        │
```

---

## TỔNG KẾT DÀN Ý

### **Phần 2.1.3 nên bao gồm:**
1. ✅ Danh sách 6 Actors chi tiết
2. ✅ Danh sách 35 Use Cases theo nhóm (Auth, Stage A, B, C, Advanced)
3. ✅ Mối quan hệ Include/Extend với ví dụ cụ thể
4. ✅ Bảng mô tả chi tiết 3 UC quan trọng nhất
5. ✅ PlantUML Use Case Diagram đầy đủ
6. ✅ Mapping table Actors ↔ Use Cases

### **Phần 2.1.4 nên bao gồm:**
1. ✅ Tổng quan luồng chính (high-level flow)
2. ✅ Chi tiết Stage A Activity Diagram (swimlane)
3. ✅ Chi tiết Stage B Activity Diagram
4. ✅ Chi tiết Stage C Activity Diagram
5. ✅ Error handling & Decision points
6. ✅ Intent Routing flowchart
7. ✅ Streaming/Concurrent processing diagram
8. ✅ Sequence diagram toàn bộ campaign

### **Cách sử dụng dàn ý này:**
- Sử dụng text và Mermaid diagram cho báo cáo
- Draw.io để tạo diagram chuyên nghiệp hơn (copy code mô tả lên Draw.io)
- Thêm ảnh minh họa nếu cần
- Tuỳ độ chi tiết mà bạn muốn: có thể rút gọn hoặc mở rộng từng phần
