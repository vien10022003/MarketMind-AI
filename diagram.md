## UC Tổng Quát ##

@startuml
left to right direction

title Hệ thống Trợ lý Marketing Agentic AI

actor "Người dùng" as User
actor "Quản trị viên" as Admin

rectangle "Hệ thống Trợ lý Marketing Agentic AI" {

    usecase "Xác thực &\nQuản lý phiên" as UC_Auth

    usecase "Nghiên cứu thị trường\n(Stage A)" as UC_Research

    usecase "Xây dựng chiến lược\n(Stage B)" as UC_Strategy

    usecase "Triển khai chiến dịch\n(Stage C)" as UC_Campaign

    usecase "Quản lý chiến dịch\n/ Đoạn chat" as UC_Report

    usecase "Quản lý người dùng" as UC_QL
}

User --> UC_Auth
User --> UC_Research
User --> UC_Strategy
User --> UC_Campaign
User --> UC_Report

Admin --> UC_QL
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
actor "<center><<Service>>\n Discord Webhook" as Discord

rectangle "Stage C: Campaign Execution" {

    usecase "Thực thi chiến dịch ngay" as UC23
    usecase "Tạo nội dung và hình ảnh quảng cáo" as UC24
    usecase "Gửi quảng cáo Discord" as UC27
    usecase "Lập lịch đăng bài" as UC28
}

U --> UC23
U --> UC28

UC23 ..> UC24 : <<include>>
UC23 ..> UC27 : <<include>>

UC28 ..> UC24 : <<include>>


UC24 --> AI
UC24 --> ImageAPI
UC27 --> Discord
@enduml


## sequense

### xác thực ###

@startuml Authentication_Flow_Simplified
title Authentication & Session Management

skinparam sequenceMessageAlign center
skinparam participantStyle rectangular

actor User as "Người dùng"
participant FE as "Frontend"
participant Auth as "Auth Service"
database DB as "Database"

User -> FE: Nhập thông tin đăng nhập
FE -> Auth: Gửi yêu cầu đăng nhập

Auth -> DB: Kiểm tra tài khoản
DB --> Auth: Kết quả xác thực

alt Đăng nhập thành công
Auth --> FE: Trả về JWT Token
FE --> User: Truy cập hệ thống
else Đăng nhập thất bại
Auth --> FE: Thông báo lỗi
FE --> User: Hiển thị lỗi
end

@enduml




### Biểu đồ tuần tự luồng khởi tạo & Phân loại ý định người dùng ###

@startuml
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User
participant Frontend
participant "Backend API" as API
participant LLM
participant Search

User -> Frontend: Gửi yêu cầu
Frontend -> API: Gửi yêu cầu xử lý

API -> LLM: Phân loại yêu cầu
LLM --> API: Intent

alt Hội thoại thông thường
API --> Frontend: Trả phản hồi
Frontend --> User: Hiển thị kết quả

else Truy vấn thông tin
API -> Search: Tìm kiếm dữ liệu
Search --> API: Kết quả tìm kiếm
API -> LLM: Tổng hợp nội dung
LLM --> API: Câu trả lời
API --> Frontend: Trả kết quả
Frontend --> User: Hiển thị kết quả

else Nghiên cứu marketing
API --> Frontend: Yêu cầu nhập thông tin
Frontend --> User: Hiển thị biểu mẫu
end

@enduml


### Nghiên cứu thị trường



@startuml Sequence_StageA_Compact
autonumber
skinparam sequenceMessageAlign center

actor User as U
participant "Hệ thống" as APP
participant "LLM" as AI
participant "Search Tool" as Search
participant "Evidence\nProcessor" as EP
database "Database" as DB

U -> APP: Nhập yêu cầu marketing

APP -> AI: Phân tích đầu vào\nvà lập kế hoạch nghiên cứu
AI -> Search: Thu thập thông tin
Search --> AI: Trả về dữ liệu

AI --> APP: Tổng hợp evidence
APP -> EP: Xử lý và lọc dữ liệu
EP --> APP: Evidence tối ưu

APP -> AI: Sinh báo cáo marketing
AI --> APP: Trả về kết quả

APP -> DB: Lưu báo cáo
DB --> APP: Xác nhận

APP --> U: Hiển thị báo cáo

@enduml


### 2.2.2.4. Luồng Xây dựng Chiến lược Marketing ###





@startuml
title Sequence Diagram – Stage B: Strategy Generation

autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend" as FE
participant "Flask API" as API
participant "LLM" as LLM
database DB
participant "Conversation\nManager" as CM

U -> FE: Chọn "Tạo chiến lược"
FE -> API: Gửi yêu cầu tạo Stage B

API -> LLM: Phân tích dữ liệu Stage A\nvà xây dựng chiến lược
activate LLM

LLM --> API: SWOT + Campaign Briefs\n+ Marketing Strategy
deactivate LLM

API --> FE: Stream kết quả tạo chiến lược

FE --> U: Hiển thị chiến lược\ncho phép chỉnh sửa

opt Người dùng phê duyệt
U -> FE: Xác nhận chiến lược
FE -> API: Gửi yêu cầu phê duyệt
API -> DB: Lưu chiến lược
API -> CM: Lưu hội thoại

CM -> DB: Ghi lịch sử
API --> FE: Xác nhận hoàn tất

end

FE --> U: Chuyển sang Stage C
@enduml


### 2.2.2.5. Luồng triển khai chiến dịch ngay lập tức ###


@startuml Sequence_StageC_Final
autonumber
skinparam participantStyle rectangle
skinparam sequenceMessageAlign center

actor User
participant "Hệ thống Marketing" as SYS
participant "LLM" as LLM
participant "Image Generator" as IMG
participant "Discord" as DC
database "MongoDB" as DB

User -> SYS: Thực thi chiến dịch

SYS -> LLM: Sinh nội dung marketing
LLM --> SYS: Nội dung chiến dịch

opt Sinh hình ảnh
SYS -> IMG: Tạo hình ảnh quảng cáo
IMG --> SYS: Trả về hình ảnh
end

SYS -> DC: Đăng nội dung chiến dịch
DC --> SYS: Xác nhận đăng

SYS -> DB: Lưu lịch sử chiến dịch

SYS --> User: Hiển thị kết quả chiến dịch

@enduml



### 2.2.2.6. Luồng triển khai chiến dịch theo lịch ###


@startuml Sequence_StageC_Scheduled_Report
autonumber
skinparam participantStyle rectangle
skinparam sequenceMessageAlign center

actor User
participant "Hệ thống" as SYS
participant Scheduler
participant "AI Engine" as AI
participant "Kênh quảng cáo" as PUB
database DB

User -> SYS: Tạo chiến dịch và chọn thời gian đăng
SYS -> Scheduler: Lưu yêu cầu lập lịch
Scheduler -> DB: Lưu thông tin chiến dịch
SYS --> User: Xác nhận lập lịch thành công

== Đến thời điểm thực thi ==

Scheduler -> AI: Sinh nội dung chiến dịch
AI --> Scheduler: Trả về nội dung

Scheduler -> PUB: Đăng nội dung
PUB --> Scheduler: Trả về kết quả

Scheduler -> DB: Cập nhật trạng thái

@enduml


### Biểu đồ tuần tự luồng Tạo Hội Thoại & Lưu Tin Nhắn ###

@startuml Sequence_Conversation_Simplified
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant "Frontend" as FE
participant "Backend" as API
participant "Conversation\nManager" as CM
participant "LLM" as LLM
database "MongoDB" as DB

== Tạo hội thoại ==

U -> FE: Tạo hội thoại mới
FE -> API: createConversation()
API -> CM: create()

alt Chưa có tiêu đề
CM -> LLM: Sinh tiêu đề
LLM --> CM: Title
end

CM -> DB: Lưu hội thoại
DB --> CM: Conversation
CM --> FE: Trả về hội thoại
FE --> U: Hiển thị màn chat

== Gửi tin nhắn ==

U -> FE: Gửi nội dung
FE -> API: sendMessages()
API -> CM: Xử lý yêu cầu

CM -> DB: Kiểm tra + lưu tin nhắn
DB --> CM: Thành công

CM --> FE: Kết quả
FE --> U: Cập nhật hội thoại

@enduml


### luồng Truy xuất & Quản lý Hội thoại ###


@startuml Sequence_Conversation_Manage_Simplified
autonumber
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

actor User as U
participant Frontend as FE
participant "Backend" as API
participant "Conversation Manager" as CM
database MongoDB as DB

== Truy xuất hội thoại ==

U -> FE: Chọn hội thoại
FE -> API: Yêu cầu tải hội thoại
API -> CM: getConversation()
CM -> DB: Lấy thông tin + tin nhắn
DB --> CM: Dữ liệu hội thoại
CM --> API: Conversation data
API --> FE: Trả dữ liệu
FE --> U: Hiển thị nội dung

== Quản lý hội thoại ==

U -> FE: Đổi tên hội thoại
FE -> API: Gửi cập nhật
API -> CM: updateTitle()
CM -> DB: Cập nhật tiêu đề
DB --> API: Thành công
API --> FE: Refresh UI

alt Xóa hội thoại
U -> FE: Xác nhận xóa
FE -> API: Yêu cầu xóa
API -> CM: deleteConversation()
CM -> DB: Xóa hội thoại và tin nhắn
DB --> API: Thành công
API --> FE: Cập nhật danh sách
end

@enduml


## Đường dẫn ## 

https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa700002