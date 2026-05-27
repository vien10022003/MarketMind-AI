# Sequence Diagrams Specification - MarketMind-AI

## Tổng Quan Kiến Trúc Hệ Thống

### Các Thành Phần Chính
- **User/Frontend**: Ứng dụng web/mobile (Vue.js hoặc React)
- **Flask API Server**: Backend API (stage_a, stage_b, stage_c)
- **LLM Provider**: Llama 3 hoặc Gemini (qua llm_provider)
- **Search API**: Tavily Search để thu thập dữ liệu
- **Image Generator**: Tạo hình ảnh quảng cáo
- **MongoDB**: Lưu trữ dữ liệu, báo cáo, chiến lược
- **Discord Webhook**: Đăng bài quảng cáo
- **Auth Service**: Xác thực người dùng

---

## 1. SEQUENCE DIAGRAM: Authentication & Session Management

### Participants
- User
- Frontend Application
- Auth Routes (Flask)
- MongoDB
- JWT Token Manager

### Flow
```
User -> Frontend: 1. Nhập username/password
Frontend -> Auth Routes: 2. POST /auth/login (credentials)
Auth Routes -> MongoDB: 3. Kiểm tra user trong DB
MongoDB --> Auth Routes: 4. Trả về user object hoặc error
Auth Routes -> JWT Token Manager: 5. Tạo JWT token (nếu xác thực thành công)
JWT Token Manager --> Auth Routes: 6. Trả về token
Auth Routes --> Frontend: 7. Trả về token + user info
Frontend -> Frontend: 8. Lưu token vào localStorage/sessionStorage
Frontend -> Frontend: 9. Thêm token vào Authorization header cho các request tiếp theo
```

### Return Value
```json
{
  "success": true,
  "user": {
    "id": "user_id_123",
    "username": "user_name",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. SEQUENCE DIAGRAM: Stage A - Research Pipeline (Nghiên Cứu Thị Trường)

### Participants
- User
- Frontend
- Flask API (/api/research/stage_a or /api/research/stage_a/marketing)
- Conversation Manager (MongoDB)
- LLM Provider
- ReAct Agent (với Tavily Search)
- Evidence Processor
- MongoDB (Lưu báo cáo)

### Sub-Flow 2.1: Initial Chat/Intent Classification

```
User -> Frontend: 1. Gửi yêu cầu ban đầu
Frontend -> Flask API: 2. POST /api/research/stage_a
  {
    "user_prompt": "Tôi muốn kinh doanh sữa chua",
    "conversation_history": [...],
    "llm_provider": "llama"
  }

Flask API -> Conversation Manager: 3. Tạo conversation mới (nếu cần)
Conversation Manager -> MongoDB: 4. Lưu conversation vào DB
MongoDB --> Conversation Manager: 5. Trả về conversation_id

Flask API -> LLM Provider: 6. Classify Intent
  Router.classify_intent_and_respond(user_prompt)

LLM Provider --> Flask API: 7. Trả về intent
  {
    "intent": "chat|knowledge|research",
    "response": "...",
    "confidence": 0.95
  }

alt intent == "chat"
  Flask API --> Frontend: Stream {"status": "chat_response", "message": "..."}
  Frontend -> User: 8. Hiển thị chat response
  end
  
alt intent == "knowledge"
  Flask API -> LLM Provider: Xử lý knowledge query
  LLM Provider -> Tavily Search: Tìm kiếm thông tin
  Tavily Search --> LLM Provider: Trả về kết quả
  LLM Provider --> Flask API: Tổng hợp answer
  Flask API --> Frontend: Stream knowledge response
  Frontend -> User: Hiển thị answer
  end
  
alt intent == "research" && !_from_marketing_form
  Flask API --> Frontend: Stream {"status": "show_marketing_form"}
  Frontend -> User: 8. Hiển thị form nhập thông tin marketing
  User -> Frontend: 9. Điền form và submit
end
```

### Sub-Flow 2.2: Full Stage A Pipeline (Marketing Form Submitted)

```
User -> Frontend: 1. Submit marketing form với đầy đủ thông tin
  {
    "user_prompt": "Kinh doanh sữa chua",
    "ban_chat_san_pham": "Sữa chua",
    "khach_hang_muc_tieu": "Phụ nữ 25-40 tuổi",
    "gia_tri_cot_loi": "Tự nhiên, không đường",
    "gia_ca_chinh_sach": "50.000-100.000 VND",
    "_from_marketing_form": true
  }

Frontend -> Flask API: 2. POST /api/research/stage_a/marketing (STREAMING)

Flask API -> LLM Provider: 3. STEP 1: Validate & Prepare Input
LLM Provider --> Flask API: 4. Trả về validated StageAInput

Flask API --> Frontend: 5. Stream {"status": "starting", "message": "Khởi tạo tác vụ..."}

Flask API -> LLM Provider: 6. STEP 2: Planning (Lập kế hoạch)
  planner_chain(llm, user_input)
  Tạo plan 5-7 bước: research market size, analyze competitors, etc.

LLM Provider --> Flask API: 7. Trả về plan object
  {
    "goal": "Phân tích thị trường sữa chua",
    "steps": [
      {"step": 1, "name": "Xác định quy mô thị trường"},
      {"step": 2, "name": "Phân tích đối thủ cạnh tranh"},
      ...
    ]
  }

Flask API --> Frontend: 8. Stream {"status": "plan_completed", "plan": {...}}

Flask API -> GPU Memory: 9. Clear GPU memory

Flask API -> LLM Provider: 10. STEP 3: ReAct Loop
  run_react_loop(llm, plan)
  Lặp cho mỗi step trong plan:
    - LLM suy nghĩ (Thought)
    - Chọn công cụ (Action)
    - Gọi Tavily Search
    - Nhận kết quả (Observation)
    - Cập nhật state

LLM Provider -> Tavily Search: 11. Tìm kiếm (nhiều lần)
  "Quy mô thị trường sữa chua Việt Nam 2025"
  "Đối thủ cạnh tranh sữa chua premium"
  ...

Tavily Search --> LLM Provider: 12. Trả về kết quả tìm kiếm

LLM Provider --> Flask API: 13. Trả về react_state
  {
    "tool_calls": 8,
    "evidence": [
      {"source": "...", "content": "...", "relevance": 0.95},
      ...
    ]
  }

Flask API --> Frontend: 14. Stream {"status": "react_completed", "react_summary": {...}}

Flask API -> GPU Memory: 15. Clear GPU memory

Flask API -> Evidence Processor: 16. STEP 4: Evidence Processing
  normalize_and_filter_evidence(evidence_list)
  - Loại bỏ trùng lặp
  - Lọc theo độ liên quan (threshold 0.7+)
  - Chuẩn hóa định dạng

Evidence Processor --> Flask API: 17. Trả về evidence_df (DataFrame)
  20-50 items phù hợp nhất

Flask API --> Frontend: 18. Stream {"status": "evidence_ready", "evidence_count": {...}}

Flask API -> LLM Provider: 19. STEP 5: Synthesis
  synthesize_stage_a_report(llm, user_input, evidence_df)
  - Tóm tắt executive summary
  - Phân tích chuyên sâu từng khía cạnh
  - Đưa ra insights và khuyến nghị

LLM Provider --> Flask API: 20. Trả về stage_a_output
  {
    "executive_summary": "...",
    "market_analysis": {...},
    "competitor_analysis": {...},
    "recommendations": [...],
    "risks": [...]
  }

Flask API --> Frontend: 21. Stream {"status": "report_ready", "report": {...}}

Flask API -> GPU Memory: 22. Clear GPU memory

Flask API -> MongoDB: 23. STEP 6: Save Report
  mongo.save_report(metadata, stage_a_output, user_id)
  Lưu: input, plan, react_summary, full report

MongoDB --> Flask API: 24. Trả về mongodb_id

Flask API -> Conversation Manager: 25. Save to Conversation
  Lưu message với type "report" và reportData

Conversation Manager -> MongoDB: 26. Lưu vào conversation_messages collection

MongoDB --> Conversation Manager: 27. OK

Flask API --> Frontend: 28. Stream {"status": "completed", "mongodb_id": "...", "timestamp": "..."}

Frontend -> User: 29. Hiển thị báo cáo hoàn chỉnh
```

---

## 3. SEQUENCE DIAGRAM: Stage B - Strategy Generation (Xây Dựng Chiến Lược)

### Participants
- User
- Frontend
- Flask API (/api/strategy/stage_b)
- LLM Provider
- MongoDB
- Conversation Manager

### Flow

```
User -> Frontend: 1. Click "Tạo Chiến Lược" sau khi có Stage A Report

Frontend -> Flask API: 2. POST /api/strategy/stage_b (STREAMING)
  {
    "stage_a_report": {...full report object...},
    "stage_a_input": {...input parameters...},
    "mongodb_id": "stage_a_report_id",
    "llm_provider": "llama"
  }

Flask API -> LLM Provider: 3. Tạo StageBInput object
  {
    "stage_a_report": {...},
    "stage_a_input": {...},
    "mongodb_id": "..."
  }

Flask API --> Frontend: 4. Stream {"status": "progress", "message": "Đang tạo chiến lược..."}

Flask API -> LLM Provider: 5. run_stage_b_pipeline(llm, stage_b_input)
  Bước 1: Phân tích SWOT dựa trên Stage A report
  
LLM Provider --> Flask API: 6. SWOT Analysis
  {
    "strengths": [...],
    "weaknesses": [...],
    "opportunities": [...],
    "threats": [...]
  }

Flask API --> Frontend: 7. Stream {"status": "swot_completed", "swot": {...}}

Flask API -> LLM Provider: 8. Bước 2: Sinh Content Briefs
  Tạo 3-5 briefs cho các campaign khác nhau
  Mỗi brief bao gồm:
  - Campaign goal
  - Target audience
  - Tone & messaging
  - Key points
  - Call-to-action

LLM Provider --> Flask API: 9. Trả về list of briefs
  [
    {
      "id": "brief_001",
      "title": "Premium Positioning Campaign",
      "goal": "...",
      "target_audience": "...",
      "messaging": "...",
      "cta": "..."
    },
    ...
  ]

Flask API --> Frontend: 10. Stream {"status": "briefs_ready", "briefs": [...]}

Flask API -> LLM Provider: 11. Bước 3: Tạo Marketing Strategy
  Tổng hợp strategy toàn diện

LLM Provider --> Flask API: 12. Trả về strategy object
  {
    "overview": "...",
    "positioning": "...",
    "messaging": "...",
    "channels": ["Discord", "Twitter", ...],
    "timeline": "...",
    "budget_allocation": {...}
  }

Flask API --> Frontend: 13. Stream {"status": "strategy_completed", "strategy": {...}}

Flask API --> Frontend: 14. Stream {"status": "stage_b_completed"}

Frontend -> User: 15. Hiển thị Strategy + Briefs để review/edit

User -> Frontend: 16. Xem, chỉnh sửa (optional), nhấn "Phê duyệt"

Frontend -> Flask API: 17. POST /api/strategy/stage_b/approve
  {
    "mongodb_id": "stage_a_id",
    "strategy": {...},
    "approved_briefs": [...edited briefs...]
  }

Flask API -> MongoDB: 18. Lưu approved strategy vào DB
  collection: "stage_b_strategies"

MongoDB --> Flask API: 19. OK

Flask API -> Conversation Manager: 20. Save to Conversation
  Lưu message với type "strategy" và strategyData, contentBriefsData

Conversation Manager -> MongoDB: 21. Lưu vào conversation_messages

MongoDB --> Conversation Manager: 22. OK

Flask API --> Frontend: 23. {"status": "approved"}

Frontend -> User: 24. Thông báo thành công, chuẩn bị cho Stage C
```

---

## 4. SEQUENCE DIAGRAM: Stage C - Campaign Execution (Triển Khai Chiến Dịch)

### Participants
- User
- Frontend
- Flask API (/api/campaign/stage_c or /api/campaign/stage_c/scheduled)
- LLM Provider
- Image Generator
- Discord Webhook
- MongoDB
- Campaign Scheduler (optional)
- Conversation Manager

### Sub-Flow 4.1: Immediate Campaign Execution

```
User -> Frontend: 1. Click "Thực thi chiến dịch" hoặc "Lập lịch"

Frontend -> Flask API: 2. POST /api/campaign/stage_c (STREAMING)
  {
    "approved_briefs": [...],
    "webhook_url": "https://discord.com/api/webhooks/...",
    "skip_image_generation": false,
    "mongodb_stage_a_id": "...",
    "llm_provider": "llama"
  }

Flask API -> LLM Provider: 3. run_stage_c_pipeline(stage_c_input, llm)

Flask API --> Frontend: 4. Stream {"status": "progress", "message": "Bắt đầu tạo nội dung..."}

loop Cho mỗi approved brief
  
  Flask API -> LLM Provider: 5. STEP 1: Tạo Content Variations
    Sinh 2-3 biến thể nội dung dựa trên brief
    
  LLM Provider --> Flask API: 6. Trả về content variations
    [
      {"id": "var_1", "title": "...", "body": "...", "cta": "..."},
      {"id": "var_2", ...},
      ...
    ]
  
  Flask API --> Frontend: 7. Stream {"status": "content_created", "brief_id": "..."}
  
  alt skip_image_generation == false
    
    Flask API -> Image Generator: 8. Tạo hình ảnh quảng cáo
      Prompt: "(content variations + styling guidelines)"
      
    Image Generator --> Flask API: 9. Trả về image URLs
      ["https://image1.png", "https://image2.png"]
    
    Flask API --> Frontend: 10. Stream {"status": "image_generated", "image_urls": [...]}
    
  end
  
  Flask API -> Discord Webhook: 11. POST message với nội dung + image
    {
      "content": "Quảng cáo sữa chua...",
      "embeds": [
        {
          "title": "...",
          "description": "...",
          "image": {"url": "..."},
          "fields": [...]
        }
      ]
    }
  
  Discord Webhook --> Flask API: 12. {"id": "message_id_123", "timestamp": "..."}
  
  Flask API --> Frontend: 13. Stream {"status": "posted_to_discord", "message_id": "..."}
  
end

Flask API -> MongoDB: 14. Save Campaign Log
  {
    "timestamp": datetime.now(),
    "briefs_processed": 3,
    "images_generated": 3,
    "messages_posted": 3,
    "mongodb_stage_a_id": "...",
    "details": [...]
  }

MongoDB --> Flask API: 15. Trả về campaign_log_id

Flask API -> Conversation Manager: 16. Save to Conversation
  Lưu message với type "campaign_log" và campaignLogData

Conversation Manager -> MongoDB: 17. Lưu vào conversation_messages

Flask API --> Frontend: 18. Stream {"status": "stage_c_completed"}

Frontend -> User: 19. Hiển thị Campaign Summary
  - Tổng số bài đã đăng
  - Link tới Discord messages
  - Timestamp
```

### Sub-Flow 4.2: Scheduled Campaign Execution

```
User -> Frontend: 1. Click "Lập lịch" (Schedule Campaign)

Frontend -> User: 2. Hiển thị Date/Time picker
  - Chọn ngày đăng
  - Chọn giờ đăng
  - Có thể chọn nhiều time slot

User -> Frontend: 3. Chọn lịch và submit

Frontend -> Flask API: 4. POST /api/campaign/stage_c/scheduled (STREAMING)
  {
    "approved_briefs": [...],
    "webhook_url": "...",
    "skip_image_generation": false,
    "mongodb_stage_a_id": "...",
    "execution_mode": "scheduled",
    "scheduled_times": [
      "2026-05-28T08:00:00Z",
      "2026-05-29T14:30:00Z",
      "2026-05-30T16:45:00Z"
    ]
  }

Flask API -> LLM Provider: 5. run_stage_c_pipeline(stage_c_input, llm)

Flask API -> Campaign Scheduler: 6. Lưu vào APScheduler
  Tạo scheduled jobs cho các thời điểm

Campaign Scheduler -> MongoDB: 7. Lưu schedule metadata
  {
    "campaign_id": "...",
    "scheduled_times": [...],
    "status": "scheduled",
    "created_at": "...",
    "briefs": [...]
  }

MongoDB --> Campaign Scheduler: 8. OK

Flask API --> Frontend: 9. Stream {"status": "campaign_scheduled"}

Frontend -> User: 10. Hiển thị "Campaign scheduled successfully"

par (Background Process - theo lịch)
  
  loop Cho mỗi scheduled_time
    Campaign Scheduler -> Campaign Scheduler: Đợi tới scheduled_time
    
    Campaign Scheduler -> LLM Provider: Tạo content variations
    LLM Provider --> Campaign Scheduler: Trả về content
    
    Campaign Scheduler -> Image Generator: Tạo hình ảnh
    Image Generator --> Campaign Scheduler: Trả về images
    
    Campaign Scheduler -> Discord Webhook: POST message
    Discord Webhook --> Campaign Scheduler: OK
    
    Campaign Scheduler -> MongoDB: Cập nhật campaign log
    
  end
  
end
```

---

## 5. SEQUENCE DIAGRAM: Conversation Management (Quản Lý Cuộc Hội Thoại)

### Participants
- User
- Frontend
- Flask API
- Conversation Manager
- MongoDB

### Sub-Flow 5.1: Create New Conversation

```
User -> Frontend: 1. Click "New Conversation" hoặc gửi message mới

Frontend -> Flask API: 2. POST /api/conversations
  {
    "first_message": "Tôi muốn kinh doanh sữa chua",
    "title": null (optional)
  }

Flask API -> Conversation Manager: 3. create_conversation(conversation_id, title, user_id)

Conversation Manager -> LLM Provider: 4. (Optional) generate_conversation_title(first_message)
  Dùng LLM tạo tiêu đề ngắn 5-6 từ

LLM Provider --> Conversation Manager: 5. Trả về title
  "Kế hoạch kinh doanh sữa chua"

Conversation Manager -> MongoDB: 6. Lưu conversation mới
  {
    "id": "conv_123",
    "title": "Kế hoạch kinh doanh sữa chua",
    "user_id": "user_id",
    "created_at": "...",
    "updated_at": "...",
    "message_count": 0
  }

MongoDB --> Conversation Manager: 7. Trả về conversation object

Conversation Manager --> Flask API: 8. Trả về conversation

Flask API --> Frontend: 9. {"data": {"id": "conv_123", "title": "...", ...}}

Frontend -> User: 10. Mở conversation mới, sẵn sàng chat
```

### Sub-Flow 5.2: Save Messages to Conversation

```
User -> Frontend: 1. Gửi query hoặc nhận response từ API

Frontend -> Frontend: 2. Tạo message objects (user message + assistant messages)
  [
    {
      "id": "msg_001",
      "type": "user_input",
      "content": "Tôi muốn kinh doanh sữa chua",
      "timestamp": "2026-05-27T10:00:00Z"
    },
    {
      "id": "msg_002",
      "type": "clarification",
      "content": "...",
      "clarificationData": {...},
      "timestamp": "..."
    },
    {
      "id": "msg_003",
      "type": "report",
      "content": "Báo cáo...",
      "reportData": {...},
      "timestamp": "..."
    }
  ]

Frontend -> Flask API: 3. POST /api/conversations/{conversation_id}/messages
  {
    "messages": [...]
  }

Flask API -> Conversation Manager: 4. Verify user owns conversation
  get_conversation(conversation_id, user_id)

Conversation Manager -> MongoDB: 5. Kiểm tra conversation
  
MongoDB --> Conversation Manager: 6. Trả về conversation hoặc null

alt conversation exists && user_id matches
  
  Flask API -> Conversation Manager: 7. save_batch_messages(conversation_id, messages)
  
  Conversation Manager -> MongoDB: 8. Insert all messages
    collection: "conversation_messages"
    bulk insert operation
  
  MongoDB --> Conversation Manager: 9. OK (ids of inserted documents)
  
  Conversation Manager -> MongoDB: 10. Update conversation
    update: message_count, updated_at
  
  MongoDB --> Conversation Manager: 11. OK
  
  Conversation Manager --> Flask API: 12. {success: true}
  
  Flask API --> Frontend: 13. 200 OK
  
else conversation not found or unauthorized
  Flask API --> Frontend: 14. 403 Forbidden
end
```

### Sub-Flow 5.3: Get Conversation & Messages

```
User -> Frontend: 1. Click on conversation từ sidebar

Frontend -> Flask API: 2. GET /api/conversations/{conversation_id}

Flask API -> Conversation Manager: 3. get_conversation(conversation_id, user_id)

Conversation Manager -> MongoDB: 4. Query: db.conversations.findOne({id, user_id})

MongoDB --> Conversation Manager: 5. Trả về conversation

Conversation Manager -> MongoDB: 6. Query: db.conversation_messages.find({conversation_id})
  Lấy tất cả messages, sort by timestamp

MongoDB --> Conversation Manager: 7. Trả về [messages...]

Conversation Manager --> Flask API: 8. Trả về {conversation, messages}

Flask API --> Frontend: 9. {"data": {"conversation": {...}, "messages": [...]}}

Frontend -> User: 10. Hiển thị messages thread
```

### Sub-Flow 5.4: Update Title & Delete Conversation

```
User -> Frontend: 1. Click edit icon on conversation title

Frontend -> User: 2. Hiển thị input field với title hiện tại

User -> Frontend: 3. Nhập title mới

Frontend -> Flask API: 4. PUT /api/conversations/{conversation_id}/title
  {
    "title": "Tiêu đề mới"
  }

Flask API -> Conversation Manager: 5. update_title(conversation_id, title, user_id)

Conversation Manager -> MongoDB: 6. Update document
  db.conversations.updateOne({id, user_id}, {$set: {title}})

MongoDB --> Conversation Manager: 7. OK

Flask API --> Frontend: 8. 200 OK

alt User clicks Delete
  Frontend -> User: 9. Hiển thị confirm dialog
  
  User -> Frontend: 10. Xác nhận xóa
  
  Frontend -> Flask API: 11. DELETE /api/conversations/{conversation_id}
  
  Flask API -> Conversation Manager: 12. delete_conversation(conversation_id, user_id)
  
  Conversation Manager -> MongoDB: 13. Delete conversation
    db.conversations.deleteOne({id, user_id})
  
  Conversation Manager -> MongoDB: 14. Delete messages
    db.conversation_messages.deleteMany({conversation_id})
  
  MongoDB --> Conversation Manager: 15. OK
  
  Flask API --> Frontend: 16. 200 OK
  
  Frontend -> User: 17. Redirect to conversation list
end
```

---

## 6. SEQUENCE DIAGRAM: Error Handling & Recovery

### Participants
- User
- Frontend
- Flask API
- LLM Provider
- GPU Memory Manager
- MongoDB
- Frontend Error Handler

### Flow

```
User -> Frontend: 1. Gửi request (Stage A, B, C, etc.)

Frontend -> Flask API: 2. POST /api/... (STREAMING)

Flask API -> Flask API: 3. try/except wrapper

par (Normal execution - parallel processes)
  Flask API -> GPU Memory: 4a. Clear GPU memory before LLM init
  
  Flask API -> LLM Provider: 4b. Khởi tạo LLM
  
  Flask API -> Flask API: 4c. Validate input data
end

alt LLM Provider initialization fails
  LLM Provider --> Flask API: 5a. Exception: "Failed to load model"
  
  Flask API -> Frontend: 5b. Stream {"status": "error", "message": "..."}
  
  Frontend -> User: 5c. Hiển thị error message
  
else Processing error (e.g., Evidence extraction fails)
  Flask API -> Flask API: 5d. Catch exception
  
  Flask API -> MongoDB: 5e. (Optional) Log error details
  
  Flask API --> Frontend: 5f. Stream {"status": "error", "message": "..."}
  
  Frontend -> User: 5g. Hiển thị error, gợi ý retry

else Out of Memory error
  LLM Provider --> Flask API: 5h. RuntimeError: "CUDA out of memory"
  
  Flask API -> GPU Memory: 5i. gc.collect(); torch.cuda.empty_cache()
  
  Flask API --> Frontend: 5j. Stream {"status": "progress", "message": "Giảm dung lượng, thử lại..."}
  
  Flask API -> Evidence Processor: 5k. evidence_df = evidence_df.head(5)
    Giảm số lượng evidence từ 20 xuống 5
  
  Flask API -> LLM Provider: 5l. Retry synthesis với evidence giảm
  
  alt Retry succeeds
    LLM Provider --> Flask API: 5m. Trả về report
    Flask API --> Frontend: 5n. Stream report
  else Retry fails
    Flask API --> Frontend: 5o. Stream error
  end

else Network/Timeout error
  Tavily Search --> Flask API: 5p. Connection timeout
  
  Flask API --> Frontend: 5q. Stream {"status": "warning", "message": "Tìm kiếm bị chậm..."}
  
  Frontend -> User: 5r. Hiển thị warning, vẫn tiếp tục
  
end

Frontend -> Frontend: 6. Frontend error handler catches streaming errors
  
  alt Status == "error"
    Frontend -> Frontend: 7. Stop streaming
    
    Frontend -> User: 8. Hiển thị error dialog
    
    User -> Frontend: 9. Click "Retry" hoặc "Cancel"
    
  end
```

---

## 7. KEY DATA STRUCTURES

### StageAInput
```json
{
  "user_prompt": "Tôi muốn kinh doanh sữa chua",
  "ban_chat_san_pham": "Sữa chua",
  "khach_hang_muc_tieu": "Phụ nữ 25-40 tuổi, thu nhập cao",
  "gia_tri_cot_loi": "Tự nhiên, không chất bảo quản",
  "gia_ca_chinh_sach": "50.000-100.000 VND"
}
```

### StageAOutput
```json
{
  "executive_summary": "Thị trường sữa chua premium...",
  "market_analysis": {
    "market_size": "...",
    "growth_rate": "...",
    "trends": [...]
  },
  "competitor_analysis": [
    {
      "competitor_name": "...",
      "strengths": [...],
      "weaknesses": [...]
    }
  ],
  "recommendations": ["...", "..."],
  "risks": ["...", "..."],
  "opportunities": ["...", "..."]
}
```

### StageBOutput (Strategy)
```json
{
  "swot": {
    "strengths": [...],
    "weaknesses": [...],
    "opportunities": [...],
    "threats": [...]
  },
  "strategy": {
    "overview": "...",
    "positioning": "...",
    "messaging": "...",
    "channels": ["Discord", "Twitter"],
    "timeline": "..."
  },
  "content_briefs": [
    {
      "id": "brief_001",
      "title": "Campaign Title",
      "goal": "...",
      "target_audience": "...",
      "messaging": "...",
      "tone": "...",
      "cta": "..."
    }
  ]
}
```

### StageCOutput (Campaign Log)
```json
{
  "campaign_id": "camp_001",
  "timestamp": "2026-05-27T15:30:00Z",
  "status": "completed",
  "briefs_processed": 3,
  "content_variations_created": 3,
  "images_generated": 3,
  "messages_posted": 3,
  "posted_urls": [
    "https://discord.com/channels/.../123456789"
  ],
  "campaign_log": [
    {
      "brief_id": "brief_001",
      "content": "...",
      "image_url": "...",
      "posted_url": "...",
      "posted_at": "..."
    }
  ]
}
```

### Conversation & Message Structure
```json
{
  "conversation": {
    "id": "conv_123",
    "user_id": "user_id",
    "title": "Kế hoạch kinh doanh sữa chua",
    "created_at": "2026-05-27T10:00:00Z",
    "updated_at": "2026-05-27T15:45:00Z",
    "message_count": 25
  },
  "messages": [
    {
      "id": "msg_001",
      "conversation_id": "conv_123",
      "type": "user_input|clarification|plan|react|evidence|report|strategy|campaign",
      "content": "...",
      "timestamp": "...",
      "mongodbId": "...(nếu là report/strategy/campaign)",
      "reportData": "{...}",
      "strategyData": "{...}",
      "campaignLogData": "{...}"
    }
  ]
}
```

---

## 8. API ENDPOINTS SUMMARY

### Authentication
- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất
- `POST /auth/register` - Đăng ký (if enabled)

### Stage A (Research)
- `POST /api/research/stage_a` - Intent classification & research pipeline
- `POST /api/research/stage_a/marketing` - Direct pipeline (bypass intent classification)

### Stage B (Strategy)
- `POST /api/strategy/stage_b` - Generate strategy from report
- `POST /api/strategy/stage_b/approve` - Approve & save strategy

### Stage C (Campaign)
- `POST /api/campaign/stage_c` - Execute campaign immediately
- `POST /api/campaign/stage_c/scheduled` - Schedule campaign execution
- `GET /api/stage-c/scheduler/schedules` - List scheduled campaigns
- `POST /api/stage-c/scheduler/schedules/{id}/cancel` - Cancel scheduled campaign

### Conversation Management
- `GET /api/conversations` - List user's conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{conversation_id}` - Get conversation + messages
- `PUT /api/conversations/{conversation_id}/title` - Update title
- `DELETE /api/conversations/{conversation_id}` - Delete conversation
- `POST /api/conversations/{conversation_id}/messages` - Save messages

### Health Check
- `GET /health` - System health status

---

## 9. STREAMING RESPONSE FORMAT

Tất cả endpoints chính sử dụng **NDJSON streaming** (Newline Delimited JSON):

```
POST /api/research/stage_a

HTTP/1.1 200 OK
Content-Type: application/x-ndjson

{"status":"progress","message":"Nhận được yêu cầu: Tôi muốn kinh doanh sữa chua..."}
{"status":"progress","message":"Đang phân tích ý định..."}
{"status":"plan_completed","message":"Lập kế hoạch hoàn tất: 6 bước","plan":{...}}
{"status":"progress","message":"Đang chạy tác vụ tìm kiếm..."}
{"status":"react_completed","message":"Hoàn thành thu thập: 8 phiên tìm kiếm","react_summary":{...}}
{"status":"progress","message":"Lọc và chuẩn hóa dữ liệu..."}
{"status":"evidence_ready","message":"Còn lại 25 chứng cứ hợp lệ","evidence_count":{...}}
{"status":"progress","message":"Đang tổng hợp báo cáo..."}
{"status":"report_ready","message":"Báo cáo đã tạo xong","report":{...}}
{"status":"progress","message":"Đang lưu dữ liệu..."}
{"status":"completed","message":"Chiến dịch hoàn thành","mongodb_id":"...","timestamp":"2026-05-27T15:45:00Z"}
```

Frontend dùng ReadableStream hoặc EventSource để parse NDJSON và update UI real-time.

---

Đây là thông tin đủ đầy để bạn vẽ được các Sequence Diagrams chi tiết cho tất cả các luồng chính của hệ thống!
