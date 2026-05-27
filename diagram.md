## UC Tổng Quát ##

@startuml
title Hệ thống Trợ lý Marketing Agentic AI

' Định nghĩa các Actor
actor "Người dùng" as User
actor "<center><<Service>>\nSocial Media APIs" as SocialAPI
actor "<center><<Service>>\nImage Generation Modul" as ImageMod
actor "<center><<Service>>\nLLM Modul\n(Llama 3 / Gemini)" as LLM
actor "<center><<Service>>\nSearch API" as SearchAPI

' Khung hệ thống (System Boundary)
rectangle "Hệ thống Trợ lý Marketing Agentic AI" {

    ' Các Use Case chính
    usecase "Triển khai chiến dịch\n(Stage C)" as UC_Campaign
    usecase "Xây dựng chiến lược\n(Stage B)" as UC_Strategy
    usecase "Quản lý chiến dịch/ Đoạn chat" as UC_Report
    usecase "Xác thực & Quản lý phiên" as UC_Auth
    usecase "Nghiên cứu thị trường\n(Stage A)" as UC_Research

    ' Các Use Case con / phụ
    usecase "Lập lịch & đăng bài" as UC_Schedule
    usecase "Tạo nội dung đa phương tiện" as UC_Content
    usecase "Sinh Content Brief" as UC_Brief
    usecase "Phân tích yêu cầu" as UC_Analyze
    usecase "Thu thập dữ liệu thị trường" as UC_Data

    ' Mối quan hệ giữa Actor và Use Case (Association)
    User --> UC_Campaign
    User --> UC_Strategy
    User --> UC_Report
    User --> UC_Auth
    User --> UC_Research

    ' Mối quan hệ với các Actor bên ngoài
    UC_Schedule --> SocialAPI
    UC_Content --> ImageMod
    UC_Brief --> LLM
    UC_Analyze --> LLM
    UC_Data --> SearchAPI
    UC_Data --> LLM

    ' Mối quan hệ Include
    UC_Campaign ..> UC_Schedule : <<include>>
    UC_Campaign ..> UC_Content : <<include>>
    
    UC_Strategy ..> UC_Brief : <<include>>
    
    UC_Research ..> UC_Analyze : <<include>>
    UC_Research ..> UC_Data : <<include>>
}

@enduml




## 2.1.3.3.2. Nghiên cứu Thị trường (Research) ##

@startuml UseCase_StageA
!theme plain

actor User as U
actor "<center><<Service>>\nLLM" as AI
actor "<center><<Service>>\nSearch API" as T
rectangle "Stage A: Research Pipeline" {
usecase UC6 as "Gửi yêu cầu nghiên cứu"
usecase UC8 as "Thực thi Research Pipeline"
usecase UC9 as "Tìm kiếm & Thu thập dữ liệu"
usecase UC10 as "Phân tích đối thủ"
usecase UC12 as "Tổng hợp báo cáo"
}
U --> UC6
UC6 ..> UC8 : <<include>>
UC8 ..> UC9 : <<include>>
UC8 ..> UC10 : <<include>>
UC8 ..> UC12 : <<include>>
UC8 --> AI
UC10 --> AI
UC12 --> AI

UC9 --> T

@enduml


## 2.1.3.3.3. Xây dựng Chiến lược (Strategy) ##

@startuml UseCase_StageB
!theme plain

actor User as U
actor "<center><<Service>>\nLLM" as AI
actor "<center><<Service>>\n SearchAPI" as T
rectangle "Stage B: Strategy Generation" {
    usecase UC14 as "Lập chiến lược Marketing"
    usecase UC20 as "Sinh Content Briefs"
    usecase UC15 as "Phân tích SWOT"
}
U --> UC14
UC14 ..> UC20 : <<include>>
UC20 ..> UC15 : <<include>>
UC15 --> AI
UC20 --> AI
UC15 --> T
@enduml

## 2.1.3.3.4. Triển khai chiến dịch ##
@startuml
!theme plain

actor User as U
actor "<center><<Service>>\n LLM" as AI
actor "<center><<Service>>\n ImageModul" as ImageAPI
actor "Discord Webhook" as Discord

rectangle "Stage C: Campaign Execution" {

    usecase "UC-23\nThực thi chiến dịch ngay" as UC23
    usecase "UC-24\nTạo nội dung và hình ảnh quảng cáo" as UC24
    usecase "UC-27\nGửi quảng cáo Discord" as UC27
    usecase "UC-28\nLập lịch đăng bài" as UC28
    usecase "UC-29\nTheo dõi hiệu suất" as UC29
}

U --> UC23
U --> UC28

UC23 ..> UC24 : <<include>>
UC23 ..> UC27 : <<include>>
UC23 ..> UC29 : <<include>>

UC28 ..> UC24 : <<include>>
UC28 ..> UC29 : <<include>>


UC24 --> AI
UC24 --> ImageAPI
UC27 --> Discord
@enduml


## sequense

@startuml Authentication_Flow
title Sequence Diagram: Authentication & Session Management
skinparam sequenceMessageAlign center
skinparam participantStyle rectangular

actor "Người dùng" as User
participant "Frontend\n(Vue.js/React)" as FE
participant "Auth Routes\n(Flask)" as Auth
database "MongoDB" as DB
participant "JWT Manager" as JWT

== Giai đoạn 1: Nhập thông tin đăng nhập ==
User -> FE: Nhập username/password
FE -> Auth: POST /auth/login {credentials}

== Giai đoạn 2: Xác thực với Database ==
activate Auth
Auth -> DB: find_user(username)
activate DB
DB --> Auth: user_object hoặc null
deactivate DB

alt User tồn tại & password đúng
    == Giai đoạn 3: Cấp JWT Token ==
    Auth -> JWT: create_token(user_id, roles, exp)
    activate JWT
    JWT --> Auth: signed_jwt_token
    deactivate JWT
    
    Auth --> FE: HTTP 200 {success, user, token}
    deactivate Auth
    
    == Giai đoạn 4: Lưu trữ client-side ==
    FE -> FE: localStorage.setItem('token', token)
    FE -> FE: Set Authorization: Bearer <token>
    FE --> User: Đăng nhập thành công → Redirect Dashboard

else Xác thực thất bại
    Auth --> FE: HTTP 401 {error: "Invalid credentials"}
    deactivate Auth
    FE --> User: Hiển thị thông báo lỗi
end

@enduml





@startuml
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend\n(Vue.js / React)" as FE
participant "Flask API\nServer" as API
participant "Conversation\nManager" as CM
database "MongoDB" as DB
participant "LLM Provider" as LLM
participant "Tavily\nSearch API" as Tavily

U -> FE: 1. Gửi yêu cầu ban đầu
FE -> API: 2. POST /api/research/stage_a\n{user_prompt, conversation_history, llm_provider}
API -> CM: 3. Tạo conversation mới (nếu cần)
CM -> DB: 4. Lưu metadata conversation
DB --> CM: 5. Trả về conversation_id
API -> LLM: 6. Classify Intent\n(Router.classify_intent_and_respond)
LLM --> API: 7. Trả về {intent, response, confidence}

alt intent == "chat"
    API --> FE: 8. Stream chat_response
    FE --> U: 9. Hiển thị phản hồi hội thoại
else intent == "knowledge"
    API -> LLM: 10. Xử lý knowledge query
    LLM -> Tavily: 11. Tìm kiếm thông tin thực tế
    Tavily --> LLM: 12. Trả về kết quả search
    LLM --> API: 13. Tổng hợp câu trả lời (RAG/Contextual)
    API --> FE: 14. Stream knowledge_response
    FE --> U: 15. Hiển thị kết quả
else intent == "research" && !_from_marketing_form
    API --> FE: 16. Stream show_marketing_form
    FE --> U: 17. Hiển thị form nhập thông tin marketing
    U -> FE: 18. Điền và submit form
end
@enduml





@startuml Sequence_StageA_FullPipeline
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend" as FE
participant "Flask API" as API
participant "LLM Provider" as LLM
participant "Tavily Search" as Tavily
participant "Evidence\nProcessor" as EP
participant "GPU Memory" as GPU
database "MongoDB" as DB

U -> FE: 1. Submit marketing form\n(ban_chat, target, pricing, usp...)
FE -> API: 2. POST /api/research/stage_a/marketing (STREAMING)

API -> LLM: 3. STEP 1: Validate & Prepare Input
LLM --> API: 4. Trả về StageAInput (chuẩn hóa schema)
API --> FE: 5. Stream "starting"

API -> LLM: 6. STEP 2: Planning (planner_chain)
LLM --> API: 7. Trả về plan object (5-7 bước nghiên cứu)
API --> FE: 8. Stream "plan_completed"

API -> GPU: 9. Giải phóng bộ nhớ GPU (clear cache)
API -> LLM: 10. STEP 3: ReAct Loop (lặp theo từng bước plan)
LLM -> Tavily: 11. Gửi yêu cầu tìm kiếm (nhiều lần)
Tavily --> LLM: 12. Trả về kết quả (Observation)
LLM --> API: 13. Trả về react_state (tool_calls, evidence)
API --> FE: 14. Stream "react_completed"

API -> GPU: 15. Giải phóng bộ nhớ GPU
API -> EP: 16. STEP 4: Evidence Processing\n(normalize, deduplicate, filter relevance > 0.7)
EP --> API: 17. Trả về evidence_df (20-50 items tối ưu)
API --> FE: 18. Stream "evidence_ready"

API -> LLM: 19. STEP 5: Synthesis Report
LLM --> API: 20. Trả về stage_a_output\n(executive_summary, market/competitor analysis, risks)
API --> FE: 21. Stream "report_ready"

API -> GPU: 22. Giải phóng bộ nhớ GPU
API -> DB: 23. STEP 6: Lưu báo cáo & metadata
DB --> API: 24. Trả về mongodb_id
API -> DB: 25. Lưu vào conversation_messages (type: report)
DB --> API: 26. Xác nhận lưu thành công
API --> FE: 27. Stream "completed"
FE --> U: 28. Hiển thị báo cáo hoàn chỉnh
@enduml




@startuml Sequence_StageB_Strategy
title Sequence Diagram - Stage B: Strategy Generation Pipeline
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam sequenceParticipantFontSize 10
skinparam sequenceMessageFontSize 9

actor User as U
participant "Frontend\n(Web/Mobile)" as FE
participant "Flask API\nServer" as API
participant "LLM Provider" as LLM
database "MongoDB" as DB
participant "Conversation\nManager" as CM

U -> FE: 1. Click "Tạo Chiến Lược" (sau khi nhận Stage A Report)
FE -> API: 2. POST /api/strategy/stage_b (STREAMING)\n{stage_a_report, stage_a_input, mongodb_id, llm_provider}
API -> API: 3. Đóng gói StageBInput object (chuẩn hóa schema)
API --> FE: 4. Stream {"status": "progress", "message": "Đang tạo chiến lược..."}

API -> LLM: 5. STEP 1: SWOT Analysis\n(Dựa trên dữ liệu Stage A)
LLM --> API: 6. Trả về SWOT Matrix\n{strengths, weaknesses, opportunities, threats}
API --> FE: 7. Stream {"status": "swot_completed", "swot": {...}}

API -> LLM: 8. STEP 2: Generate Content Briefs\n(Sinh 3-5 campaign briefs)
LLM --> API: 9. Trả về list of briefs\n[{id, title, goal, target, messaging, cta}, ...]
API --> FE: 10. Stream {"status": "briefs_ready", "briefs": [...]}

API -> LLM: 11. STEP 3: Synthesize Marketing Strategy\n(Tổng hợp chiến lược toàn diện)
LLM --> API: 12. Trả về strategy object\n{overview, positioning, channels, timeline, budget}
API --> FE: 13. Stream {"status": "strategy_completed", "strategy": {...}}
API --> FE: 14. Stream {"status": "stage_b_completed"}

FE --> U: 15. Hiển thị Strategy + Briefs để review/chỉnh sửa
U -> FE: 16. Hiệu đính nội dung (optional) & nhấn "Phê duyệt"
FE -> API: 17. POST /api/strategy/stage_b/approve\n{mongodb_id, strategy, approved_briefs}

API -> DB: 18. Lưu approved strategy\n(collection: stage_b_strategies)
DB --> API: 19. Xác nhận lưu thành công
API -> CM: 20. Save to Conversation\n(type: "strategy", metadata, strategyData, briefsData)
CM -> DB: 21. Lưu vào conversation_messages
DB --> CM: 22. OK
API --> FE: 23. {"status": "approved"}
FE --> U: 24. Thông báo thành công, chuyển trạng thái sang Stage C
@enduml





@startuml Sequence_StageC_Immediate
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam participantStyle rectangle

actor User as U
participant "Frontend\n(Vue.js / React)" as FE
participant "Flask API\nServer" as API
participant "LLM Provider" as LLM
participant "Image\nGenerator" as IMG
participant "Discord\nWebhook" as DC
database "MongoDB" as DB
participant "Conversation\nManager" as CM

U -> FE: 1. Click "Thực thi chiến dịch"
FE -> API: 2. POST /api/campaign/stage_c (STREAMING)\n{approved_briefs, webhook_url, skip_image_generation, mongodb_stage_a_id}

API -> LLM: 3. run_stage_c_pipeline(stage_c_input, llm)
API --> FE: 4. Stream {"status": "progress", "message": "Bắt đầu tạo nội dung..."}

loop Cho mỗi approved brief
    API -> LLM: 5. STEP 1: Tạo Content Variations\n(Sinh 2-3 biến thể nội dung/brief)
    LLM --> API: 6. Trả về content variations\n[{id, title, body, cta}, ...]
    API --> FE: 7. Stream {"status": "content_created", "brief_id": "..."}
    
    alt skip_image_generation == false
        API -> IMG: 8. Tạo hình ảnh quảng cáo\nPrompt: content + styling guidelines
        IMG --> API: 9. Trả về image URLs\n["https://img1.png", "https://img2.png"]
        API --> FE: 10. Stream {"status": "image_generated", "image_urls": [...]}
    end
    
    API -> DC: 11. POST message (content + embeds + image)
    DC --> API: 12. {"id": "msg_123", "timestamp": "..."}
    API --> FE: 13. Stream {"status": "posted_to_discord", "message_id": "..."}
end

API -> DB: 14. Save Campaign Log\n{briefs_processed, images_generated, messages_posted, details}
DB --> API: 15. Trả về campaign_log_id
API -> CM: 16. Lưu vào conversation_messages (type: campaign_log)
CM -> DB: 17. Persist conversation history
DB --> CM: 18. OK
API --> FE: 19. Stream {"status": "stage_c_completed"}
FE --> U: 20. Hiển thị Campaign Summary\n(số bài đăng, link Discord, timestamp)
@enduml




@startuml Sequence_StageC_Scheduled
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam participantStyle rectangle

actor User as U
participant "Frontend" as FE
participant "Flask API" as API
participant "Campaign\nScheduler" as SCH
database "MongoDB" as DB
participant "LLM Provider" as LLM
participant "Image Generator" as IMG
participant "Discord Webhook" as DC

U -> FE: 1. Click "Lập lịch chiến dịch"
FE -> U: 2. Hiển thị Date/Time picker (multi-slot support)
U -> FE: 3. Chọn lịch và submit
FE -> API: 4. POST /api/campaign/stage_c/scheduled (STREAMING)\n{approved_briefs, scheduled_times[], execution_mode: "scheduled"}

API -> LLM: 5. run_stage_c_pipeline (pre-generate content if needed)
API -> SCH: 6. Đăng ký scheduled jobs vào APScheduler\n{campaign_id, scheduled_times, briefs, config}
SCH -> DB: 7. Lưu schedule metadata\n{status: "scheduled", created_at, next_run}
DB --> SCH: 8. OK
API --> FE: 9. Stream {"status": "campaign_scheduled"}
FE --> U: 10. Hiển thị "Campaign scheduled successfully"

== Background Execution (theo lịch) ==

par Job Scheduler Loop
    loop Cho mỗi scheduled_time
        SCH -> SCH: Đợi tới scheduled_time (cron/interval trigger)
        activate SCH
        
        SCH -> LLM: 11. Tạo content variations (hoặc load từ cache)
        LLM --> SCH: 12. Trả về content
        SCH -> IMG: 13. Tạo hình ảnh (nếu skip_image_generation == false)
        IMG --> SCH: 14. Trả về image URLs
        SCH -> DC: 15. POST message tới Discord
        DC --> SCH: 16. {"id": "msg_xyz", "ok": true}
        SCH -> DB: 17. Cập nhật campaign log\n{executed_at, message_id, status: "posted"}
        
        deactivate SCH
    end
end

note right of SCH
  Cơ chế retry:
  - Max 3 lần retry với exponential backoff
  - Lưu error log nếu thất bại vĩnh viễn
  - Gửi notification tới user qua email/webhook
end note





@startuml Sequence_Conversation_Write
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend\n(Web/Mobile)" as FE
participant "Flask API" as API
participant "Conversation\nManager" as CM
participant "LLM Provider" as LLM
database "MongoDB" as DB

U -> FE: 1. Khởi tạo hội thoại mới
FE -> API: 2. POST /api/conversations\n{first_message, title (optional)}
API -> CM: 3. create_conversation()
alt title is null
    CM -> LLM: 4. generate_conversation_title(first_message)
    LLM --> CM: 5. Trả về title (vd: "Kế hoạch kinh doanh sữa chua")
end
CM -> DB: 6. Insert conversation document\n(id, title, user_id, created_at)
DB --> CM: 7. Trả về conversation object
CM --> API: 8. Trả về conversation mới tạo
API --> FE: 9. 200 OK + conversation data
FE --> U: 10. Mở giao diện chat mới

note over U, FE: Người dùng tương tác với Agent (chat, nhận báo cáo, v.v.)

FE -> FE: 11. Đóng gói batch messages\n(user_input, clarification, report, etc.)
FE -> API: 12. POST /api/conversations/{id}/messages\n{messages: [...]}
API -> CM: 13. verify_ownership(conversation_id, user_id)
CM -> DB: 14. Query conversation by id & user_id
DB --> CM: 15. Trả về conversation (hoặc null)
alt conversation exists & authorized
    CM -> DB: 16. Bulk insert messages\n(collection: conversation_messages)
    DB --> CM: 17. OK (inserted IDs)
    CM -> DB: 18. Update conversation metadata\n(message_count, updated_at)
    DB --> CM: 19. OK
    CM --> API: 20. {success: true}
    API --> FE: 21. 200 OK
else unauthorized / not found
    API --> FE: 22. 403 Forbidden
end
@enduml




@startuml Sequence_Conversation_Read_Manage
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend" as FE
participant "Flask API" as API
participant "Conversation\nManager" as CM
database "MongoDB" as DB

note over U, FE: === Luồng 3: Truy xuất hội thoại ===
U -> FE: 1. Chọn hội thoại từ sidebar
FE -> API: 2. GET /api/conversations/{conversation_id}
API -> CM: 3. get_conversation(conversation_id, user_id)
CM -> DB: 4. Query conversation document
DB --> CM: 5. Trả về conversation
CM -> DB: 6. Query messages\n(find({conversation_id}), sort by timestamp)
DB --> CM: 7. Trả về [messages...]
CM --> API: 8. Gói dữ liệu {conversation, messages}
API --> FE: 9. 200 OK + data payload
FE --> U: 10. Render message thread

note over U, FE: === Luồng 4: Cập nhật & Xóa ===
U -> FE: 11. Chỉnh sửa tiêu đề hội thoại
FE -> API: 12. PUT /api/conversations/{id}/title\n{title: "Mới"}
API -> CM: 13. update_title(id, title, user_id)
CM -> DB: 14. updateOne({id, user_id}, {$set: {title}})
DB --> CM: 15. OK
CM --> API: 16. 200 OK
API --> FE: 17. Cập nhật UI title

alt Người dùng xác nhận xóa hội thoại
    U -> FE: 18. Click Delete & Confirm
    FE -> API: 19. DELETE /api/conversations/{id}
    API -> CM: 20. delete_conversation(id, user_id)
    CM -> DB: 21. deleteOne(conversations)
    CM -> DB: 22. deleteMany(conversation_messages)
    DB --> CM: 23. OK (cascade delete)
    CM --> API: 24. 200 OK
    API --> FE: 25. Xác nhận xóa thành công
    FE --> U: 26. Redirect về danh sách hội thoại
end
@enduml

## Đường dẫn ## 

https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa700002