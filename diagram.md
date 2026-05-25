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
skinparam usecaseBackgroundColor #CAD0D8
skinparam usecaseBorderColor #3E4246

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
skinparam usecaseBackgroundColor #CAD0D8
skinparam usecaseBorderColor #3E4246

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




## Đường dẫn ## 

https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa700002