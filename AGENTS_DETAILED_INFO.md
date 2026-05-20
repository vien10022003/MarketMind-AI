# Thông tin Chi Tiết về Các Agents trong MarketMind AI

## 1. Supervisor Agent (Orchestrator/Router)

**Vị trí code:** `backend/stage_a/router.py` - `classify_intent_and_respond()`

### Chức năng:
- **Phân tích ý định (Intent Classification):** Phân loại yêu cầu của người dùng vào 3 loại:
  - `chat`: Hội thoại thông thường, chào hỏi
  - `knowledge`: Câu hỏi khó, cần tìm kiếm web
  - `research`: Yêu cầu phân tích marketing, nghiên cứu thị trường

- **Định hướng (Routing):** Chuyển yêu cầu đến agent phù hợp
  - Chat → Trả lời trực tiếp
  - Knowledge → Gọi `handle_knowledge_query()` (sử dụng Tavily search)
  - Research → Hiển thị form marketing để người dùng điền thêm thông tin

### Implementation:
```python
# Sử dụng LLM với function calling
messages = build_messages_from_history(user_prompt, conversation_history)
raw = llm.generate(
    messages=messages,
    system_message=SYSTEM_MESSAGE_INTENT_CLASSIFIER,
    tools=INTENT_CLASSIFICATION_TOOLS,  # Công cụ phân loại
    max_new_tokens=500
)

# Trả về: {"intent": "chat|knowledge|research", "response": "...", "reasoning": "..."}
```

### Nơi được sử dụng:
- **Flask API:** `/api/research/stage_a` → Gọi `run_stage_a_pipeline_generator()`
- **Conversation History:** Lưu lịch sử để xác định ngữ cảnh

---

## 2. Research Agent (Stage A)

**Vị trí code:** `backend/stage_a/main.py` + `backend/stage_a/flask_api.py`

### Chức năng:
Nghiên cứu thị trường và phân tích sâu về sản phẩm/dịch vụ

### Các bước pipeline:
1. **Clarification** (`clarify_user_prompt()`)
   - Xác minh và làm rõ các thông tin input
   - Trích xuất: ngành hàng, thị trường, phân khúc khách hàng, etc.

2. **Planning** (`planner_chain()`)
   - Lập kế hoạch chi tiết cho quá trình nghiên cứu
   - Tạo danh sách các bước cần thực hiện

3. **ReAct Loop** (`run_react_loop()`)
   - Lặp lại: Reasoning → Tool Calling → Observation
   - Sử dụng Tavily Search API để tìm kiếm thông tin thị trường
   - Thu thập bằng chứng/dữ liệu từ web

4. **Evidence Processing** (`normalize_and_filter_evidence()`)
   - Lọc, chuẩn hóa và xác thực độ chất lượng của dữ liệu
   - Loại bỏ dữ liệu không liên quan

5. **Synthesis** (`synthesize_stage_a_report()`)
   - Tổng hợp thành báo cáo chuyên nghiệp
   - Tạo các mục: Tổng quan thị trường, Phân tích đối thủ, Xu hướng ngành, Insight khách hàng

6. **Output Formatting**
   - Xuất báo cáo dưới dạng Markdown + JSON
   - Lưu vào MongoDB

### Công cụ sử dụng:
- **Tavily Search API:** Tìm kiếm web
- **LLM (Llama 3):** Phân tích và tổng hợp

### API Endpoints:
- `POST /api/research/stage_a` - Phân tích ý định
- `POST /api/research/stage_a/marketing` - Chạy đầy đủ (skip intent classification)

### Output:
```json
{
  "tong_quan_thi_truong": "Phân tích tổng quan thị trường...",
  "phan_tich_doi_thu": "Danh sách đối thủ và phân tích...",
  "xu_huong_nganh": "Các xu hướng hiện tại...",
  "phan_khuc_va_insight_khach_hang": "Phân khúc khách hàng mục tiêu...",
  "citations": ["URL1", "URL2", ...]
}
```

---

## 3. Strategy Agent (Stage B)

**Vị trí code:** `backend/stage_b/campaign.py` + `backend/stage_b/strategy.py`

### Chức năng:
Lập chiến lược marketing và tạo content briefs dựa trên báo cáo từ Stage A

### Các bước pipeline:

1. **SWOT Analysis** (`generate_swot_analysis()`)
   - Phân tích Strengths, Weaknesses, Opportunities, Threats
   - Dựa trên báo cáo Stage A

2. **USP Extraction** (`extract_usp()`)
   - Xác định Unique Selling Proposition (Điểm bán được duy nhất)
   - Tạo thông điệp marketing chính

3. **Buyer Persona** (`refine_persona()`)
   - Xây dựng profile chi tiết về khách hàng mục tiêu
   - Gồm: Đặc điểm nhân khẩu học, Hành vi, Nhu cầu, Pain points

4. **Content Pillars** (`define_content_pillars()`)
   - Định nghĩa 4-5 chủ đề nội dung chính
   - Ví dụ: Product Features, Customer Stories, Industry Insights, Promotions

5. **Campaign Plan** (`create_campaign_plan()`)
   - Lập kế hoạch 7 ngày
   - Tạo content briefs cho từng ngày
   - Định nghĩa timing, content type, platform

### Content Brief Structure:
```json
{
  "day": 1,
  "title": "Tên bài đăng",
  "caption": "Nội dung tóm tắt",
  "image_prompt": "Mô tả ảnh cơ bản",
  "pillar": "Chủ đề (Product Features, etc.)",
  "content_type": "Loại nội dung (story, post, etc.)",
  "platform": "Nền tảng (Discord, Facebook, etc.)"
}
```

### API Endpoints:
- `POST /api/strategy/stage_b` - Tạo chiến lược
- `POST /api/strategy/stage_b/approve` - Lưu chiến lược đã phê duyệt

### Output:
```json
{
  "status": "strategy_ready",
  "strategy": {
    "swot": {...},
    "usp": {...},
    "persona": {...},
    "content_pillars": [...],
    "campaign_plan": [...]
  },
  "content_briefs": [...]
}
```

---

## 4. Content/Execution Agent (Stage C)

**Vị trí code:** `backend/stage_c/discord_publisher.py` + `backend/stage_c/content_expander.py`

### Chức năng:
Tạo nội dung chi tiết, sinh ảnh, và triển khai chiến dịch lên Discord

### Các bước pipeline:

1. **Content Expansion** (`expand_content_brief()`)
   - Mở rộng content briefs thành bài viết hoàn chỉnh
   - Viết caption hấp dẫn cho Discord
   - Tạo prompt chi tiết cho tạo ảnh (tiếng Anh)

2. **Image Generation** (`generate_image()`)
   - Gọi API tạo ảnh (DALL-E, Stable Diffusion, etc.)
   - Tạo ảnh chuyên nghiệp dựa trên prompt

3. **Format Discord Content** (`format_discord_embed()`)
   - Tạo Discord embed payload
   - Gồm: Title, Description, Image, Footer, Timestamp

4. **Post to Discord** 
   - Gửi webhook request tới Discord
   - Đăng bài lên server

5. **Scheduling** (Optional)
   - Lên lịch đăng bài ở những thời điểm cụ thể
   - Sử dụng APScheduler cho việc tự động hóa

### API Endpoints:
- `POST /api/campaign/stage_c` - Tạo và đăng ngay lập tức
- `POST /api/campaign/stage_c/scheduled` - Lên lịch đăng bài

### Output:
```json
{
  "status": "stage_c_completed",
  "campaign_log": {
    "campaign_id": "ID",
    "briefs_processed": 7,
    "images_generated": 7,
    "posts_published": 7,
    "scheduled_posts": 0,
    "errors": []
  }
}
```

---

## 5. Multi-Agent Orchestration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                             │
│              "Tạo chiến dịch marketing..."                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│     SUPERVISOR AGENT (router.py)                            │
│  - Intent Classification                                    │
│  - Route: chat → knowledge → research                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ (If research intent)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│     RESEARCH AGENT (Stage A)                                │
│  1. Clarification (Làm rõ yêu cầu)                          │
│  2. Planning (Lập kế hoạch)                                 │
│  3. ReAct Loop (Tìm kiếm dữ liệu)                           │
│  4. Evidence Processing (Lọc dữ liệu)                       │
│  5. Synthesis (Tổng hợp báo cáo)                            │
│                                                             │
│  Output: Market Analysis Report → MongoDB                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
              (User approval required)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│     STRATEGY AGENT (Stage B)                                │
│  1. SWOT Analysis (Phân tích)                               │
│  2. USP Extraction (Điểm bán được)                          │
│  3. Buyer Persona (Profile khách hàng)                      │
│  4. Content Pillars (Chủ đề nội dung)                       │
│  5. Campaign Plan (Lập kế hoạch chiến dịch 7 ngày)         │
│                                                             │
│  Output: Campaign Plan + Content Briefs → MongoDB           │
└─────────────────────────┬───────────────────────────────────┘
                          │
              (User approval required)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│     CONTENT/EXECUTION AGENT (Stage C)                       │
│  1. Content Expansion (Mở rộng nội dung)                    │
│  2. Image Generation (Tạo ảnh)                              │
│  3. Format Discord (Định dạng Discord)                      │
│  4. Post to Discord (Đăng lên)                              │
│  5. Scheduling (Lên lịch posting)                           │
│                                                             │
│  Output: Campaign Log → MongoDB                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Công nghệ và Tools Sử dụng

| Agent | LLM Model | Công cụ chính | API/Services |
|-------|-----------|---------------|--------------|
| **Supervisor** | Llama 3 8B | Function Calling | N/A |
| **Research (A)** | Llama 3 8B | ReAct Loop | Tavily Search API |
| **Strategy (B)** | Llama 3 8B | Function Calling | N/A |
| **Content (C)** | Llama 3 8B | Content Generation | DALL-E / Stable Diffusion, Discord API |

---

## 7. Persistent Storage

Tất cả agents sử dụng **MongoDB** để lưu trữ:

- **Stage A Reports:** Collection `research_reports`
- **Stage B Strategies:** Collection `stage_b_strategies`
- **Stage C Campaign Logs:** Collection `campaign_logs`
- **Conversation History:** Collection `conversations`

---

## 8. Conversation History Management

**Vị trí code:** `backend/conversation_manager.py`

### Tính năng:
- Lưu trữ lịch sử hội thoại với người dùng
- Cải thiện ngữ cảnh khi processing requests
- Hỗ trợ multi-turn conversations
- Sử dụng MongoDB cho persistence

### Sử dụng:
```python
from conversation_manager import get_conversation_manager

cm = get_conversation_manager()
history = cm.get_conversation_history(user_id)
# Truyền history vào LLM để cải tiến response
```

---

## 9. Authentication & User Isolation

**Vị trí code:** `backend/auth_middleware.py`, `backend/auth_routes.py`

### Bảo vệ:
- JWT token authentication
- User ID validation
- Data isolation per user
- MongoDB user-scoped queries

---

## 10. Future Enhancements

Dựa trên REPORT_DETAILED.md, các hướng phát triển tương lai:

| Hướng | Chi tiết | Ưu tiên |
|-------|----------|--------|
| **Upgrade Model** | GPT-4o / Claude 3 → Tư duy tốt hơn | 🔴 High |
| **Multi-Tenant** | Hỗ trợ nhiều tổ chức | 🔴 High |
| **Advanced Scheduling** | Timezone-aware, A/B testing | 🟡 Medium |
| **Analytics Dashboard** | Theo dõi KPIs chiến dịch | 🟡 Medium |
| **WhatsApp/Telegram** | Thêm platform mới | 🟡 Medium |
| **Voice Input** | Whisper API | 🟢 Low |

---

Generated: Chi tiết xác minh từ code backend MarketMind AI
