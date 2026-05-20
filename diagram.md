
## 2.1.3.3.2. Nghiên cứu Thị trường (Research) ##

@startuml UseCase_StageA
!theme plain
skinparam usecaseBackgroundColor #CAD0D8
skinparam usecaseBorderColor #3E4246

actor User as U
actor LLM as AI
actor "Search API" as T
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
skinparam usecaseBackgroundColor #CAD0D8
skinparam usecaseBorderColor #3E4246

actor User as U
actor LLM as AI
actor SearchAPI as T
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

