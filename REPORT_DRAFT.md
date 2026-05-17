# BÁO CÁO: XÂY DỰNG HỆ THỐNG TRỢ LÝ MARKETING SỬ DỤNG GENAI VÀ AGENTIC AI

**Tác giả:** [Tên người dùng]  
**Ngày:** [Tháng/Năm]  
**Trường:** [Tên trường]  
**Đề tài:** Xây dựng hệ thống trợ lý Marketing thông minh sử dụng Generative AI và Agentic AI

---

## MỤC LỤC

1. [CHƯƠNG I: TỔNG QUAN LÝ THUYẾT](#chương-i-tổng-quan-lý-thuyết)
   - 1.1 Giới thiệu về Marketing Digital
   - 1.2 Generative AI (GenAI) là gì?
   - 1.3 Agentic AI (AI Agent) là gì?
   - 1.4 Large Language Model (LLM) là gì?
   - 1.5 Function Calling và cách hoạt động
   - 1.6 Chat Template và cấu trúc tin nhắn
   - 1.7 Fine-tuning LLM cho Function Calling

2. [CHƯƠNG II: THIẾT KẾ VÀ GIẢI PHÁP](#chương-ii-thiết-kế-và-giải-pháp)
   - 2.1 Phân tích yêu cầu hệ thống
   - 2.2 Kiến trúc tổng thể hệ thống
   - 2.3 Lựa chọn công nghệ
   - 2.4 Thiết kế từng module/agent
   - 2.5 Giải pháp xử lý các vấn đề kỹ thuật

3. [CHƯƠNG III: THỰC NGHIỆM VÀ KẾT QUẢ](#chương-iii-thực-nghiệm-và-kết-quả)
   - 3.1 Kết quả kiểm tra function calling
   - 3.2 Đánh giá hiệu năng hệ thống
   - 3.3 Giao diện ứng dụng
   - 3.4 Kết luận và hướng phát triển

---

---

# CHƯƠNG I: TỔNG QUAN LÝ THUYẾT

## 1.1 Giới thiệu về Marketing Digital

### 1.1.1 Marketing là gì?

Marketing là tập hợp các hoạt động có mục đích giúp doanh nghiệp:
- **Quảng bá sản phẩm/dịch vụ** đến đúng đối tượng khách hàng
- **Tạo giá trị** cho khách hàng thông qua communication
- **Xây dựng mối quan hệ** lâu dài với khách hàng
- **Tăng doanh số bán hàng** và phát triển thương hiệu

### 1.1.2 Marketing Digital

Marketing Digital (Digital Marketing) là các hoạt động marketing được thực hiện trên các nền tảng số:
- **Nền tảng mạng xã hội**: Facebook, TikTok, Instagram, Twitter
- **Nền tảng thương mại điện tử**: Shopee, Lazada, Amazon
- **Email Marketing**: Gửi quảng cáo qua email
- **Content Marketing**: Tạo nội dung hấp dẫn
- **SEO/SEM**: Tối ưu hóa tìm kiếm

### 1.1.3 Các bước thực hiện chiến dịch Marketing

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKETING WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. NGHIÊN CỨU THỊ TRƯỜNG (Market Research)                │
│     └─ Phân tích đối thủ, xu hướng, khách hàng mục tiêu   │
│                                                             │
│  2. LẬP CHIẾN LƯỢC (Strategy Planning)                    │
│     └─ Xác định mục tiêu, kênh, thông điệp, ngân sách     │
│                                                             │
│  3. TẠO NỘI DUNG (Content Creation)                       │
│     └─ Viết copy, tạo hình ảnh, video                     │
│                                                             │
│  4. TRIỂN KHAI CHIẾN DỊCH (Campaign Execution)            │
│     └─ Đăng bài, chạy quảng cáo, tương tác khách hàng    │
│                                                             │
│  5. THEO DÕI & TỐI ƯU HÓA (Monitoring & Optimization)     │
│     └─ Phân tích kết quả, điều chỉnh chiến lược          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.1.4 Thách thức của Marketing Digital

- **Chi phí nhân lực cao**: Cần đội ngũ chuyên gia (analyst, copywriter, designer)
- **Tốn thời gian**: Mỗi bước đòi hỏi thời gian dài
- **Cần kinh nghiệm**: Khó đưa ra chiến lược hiệu quả
- **Dữ liệu phức tạp**: Khó phân tích thị trường thủ công
- **Tính thay đổi cao**: Xu hướng mạng xã hội thay đổi nhanh

---

## 1.2 Generative AI (GenAI) là gì?

### 1.2.1 Định nghĩa

**Generative AI** (AI Sinh Tạo) là các mô hình AI có khả năng **tạo ra nội dung mới** dựa trên dữ liệu đã được huấn luyện.

### 1.2.2 Các ứng dụng của GenAI

| Ứng dụng | Ví dụ |
|---------|-------|
| **Tạo văn bản** | ChatGPT, Claude, Llama tạo bài viết marketing |
| **Tạo hình ảnh** | DALL-E, Midjourney, Stable Diffusion tạo ảnh quảng cáo |
| **Tạo video** | Runway, HeyGen tạo video marketing |
| **Tạo code** | GitHub Copilot, ChatGPT viết code |

### 1.2.3 Ưu điểm GenAI trong Marketing

- ✅ **Tối ưu hóa chi phí**: Giảm chi phí nhân lực
- ✅ **Tăng tốc độ**: Tạo nội dung nhanh chóng
- ✅ **Tăng sáng tạo**: Đưa ra ý tưởng mới
- ✅ **Cá nhân hóa**: Tạo nội dung theo từng khách hàng

---

## 1.3 Agentic AI (AI Agent) là gì?

### 1.3.1 Định nghĩa

**Agentic AI** (AI Tác Nhân) là các hệ thống AI có khả năng:
- **Suy luận độc lập**: Phân tích tình huống, lập kế hoạch
- **Thực hiện hành động**: Gọi các công cụ/hàm để hoàn thành nhiệm vụ
- **Tương tác với thế giới bên ngoài**: Gọi API, tìm kiếm web, đọc tài liệu
- **Tự sửa chữa**: Kiểm tra kết quả, thử lại nếu lỗi

### 1.3.2 Agent vs ChatGPT

| Tiêu chí | ChatGPT | Agent |
|---------|---------|-------|
| **Khả năng** | Chỉ trả lời câu hỏi | Hoàn thành nhiệm vụ phức tạp |
| **Tương tác công cụ** | Không (thường không) | Có - gọi API, tools |
| **Tự động hóa** | Không | Có |
| **Ví dụ** | "Hôm nay thời tiết thế nào?" | "Lập chiến lược marketing cho sản phẩm X" |

### 1.3.3 Cấu trúc của một Agent

```
┌─────────────────────────────────────────┐
│         USER REQUEST                    │
│  "Hãy lập chiến lược marketing..."      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  LLM REASONING (Suy luận)               │
│  - Phân tích yêu cầu                    │
│  - Lập kế hoạch                         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  FUNCTION CALLING (Gọi Tools)           │
│  - search_market() → Tìm kiếm thị trường│
│  - analyze_competitors() → Phân tích    │
│  - generate_strategy() → Tạo chiến lược│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  RESULT SYNTHESIS (Tổng hợp kết quả)  │
│  - Kết hợp kết quả các tools            │
│  - Trả lời người dùng                   │
└─────────────────────────────────────────┘
```

### 1.3.4 Ứng dụng Agentic AI trong hệ thống

Hệ thống MarketMind AI sử dụng multi-agent architecture:

- **Supervisor Agent**: Phân chia và điều phối nhiệm vụ
- **Research Agent**: Nghiên cứu thị trường (Stage A)
- **Strategy Agent**: Lập chiến lược (Stage B)
- **Content Agent**: Tạo nội dung quảng cáo (Stage C)
- **Execution Agent**: Triển khai chiến dịch (Posting)

---

## 1.4 Large Language Model (LLM) là gì?

### 1.4.1 Định nghĩa

**Large Language Model (LLM)** là các mô hình neural network lớn được huấn luyện trên hàng tỷ từ (tokens) để dự đoán và tạo ra văn bản.

### 1.4.2 Cách hoạt động của LLM

```
┌─────────────────────────────────────────┐
│         INPUT TEXT (Tokens)             │
│    "Lập chiến lược marketing cho"       │
└──────────────────┬──────────────────────┘
                   │
                   ▼ (Embedding)
┌─────────────────────────────────────────┐
│    TRANSFORMER LAYERS (Billions params) │
│  - Self-attention                       │
│  - Feed-forward networks                │
└──────────────────┬──────────────────────┘
                   │
                   ▼ (Softmax)
┌─────────────────────────────────────────┐
│   PROBABILITY DISTRIBUTION               │
│   [the:0.8, a:0.1, ...] →               │
└──────────────────┬──────────────────────┘
                   │
                   ▼ (Sampling/Greedy)
┌─────────────────────────────────────────┐
│       GENERATED TOKEN                   │
│             "sản phẩm"                  │
│   (Tiếp tục cho đến khi gặp [EOS])     │
└─────────────────────────────────────────┘
```

### 1.4.3 Các mô hình LLM phổ biến

| Mô hình | Số tham số | Công ty | Ưu điểm | Nhược điểm |
|--------|-----------|--------|--------|-----------|
| **GPT-4** | 1.7 Trillion | OpenAI | Cực mạnh, chính xác | Chi phí cao |
| **Claude 3** | 100B+ | Anthropic | Tư duy logic tốt | Chậm hơn GPT-4 |
| **Llama 2** | 7B, 13B, 70B | Meta | Open source, mã nguồn mở | Yếu hơn GPT-4 |
| **Llama 3** | 8B, 70B | Meta | Cải tiến Llama 2 | Vẫn không bằng GPT-4 |
| **Qwen 2.5** | 0.5B-72B | Alibaba | Đa ngôn ngữ (tiếng Việt tốt) | Bộ nhớ yêu cầu cao |
| **Mistral** | 7B, 8x7B | Mistral AI | Nhẹ nhàng, nhanh | Ít powerful |

### 1.4.4 Lựa chọn mô hình cho hệ thống

**Yêu cầu của dự án:**
- Cần hỗ trợ Function Calling (gọi tools)
- Chi phí thấp (chạy local hoặc API rẻ)
- Hỗ trợ tiếng Việt
- Có đủ "khôn ngoan" để suy luận
- Có thể fine-tune để cải tiến function calling

**Mô hình được chọn: Llama 2 / Llama 3 / Qwen 2.5**

**Lý do chọn:**
1. ✅ Open source → có thể fine-tune
2. ✅ Hỗ trợ function calling → có thể gọi tools
3. ✅ Có phiên bản nhỏ (3B-8B) → chạy trên GPU yếu
4. ✅ Community lớn → dễ tìm tài nguyên
5. ⚠️ Nhược điểm: 3B/8B ít "khôn ngoan" hơn GPT-4

### 1.4.5 Vấn đề với LLM kích thước nhỏ (3B/8B)

**Vấn đề 1: Không hiểu function calling**
```
INPUT:
  "Tìm kiếm thị trường cho sản phẩm iPhone 15"
  
LLAMA 3B OUTPUT:
  "Sản phẩm iPhone 15 là một điện thoại thông minh. Nó có camera tốt..."
  
EXPECTED (Function calling):
  {
    "function": "search_market",
    "arguments": {
      "product": "iPhone 15",
      "market": "Vietnam"
    }
  }
```

**Vấn đề 2: LLM nhỏ "ngu" khi nhập liệu phức tạp**
- Khi input lớn (10,000+ tokens) → output chất lượng giảm
- Khi câu hỏi phức tạp → suy luận sai lạc
- Khi context dài → quên thông tin ở đầu

**Vấn đề 3: Thường trả lời bằng văn bản thay vì JSON**
```
❌ SAI: "Nên gọi hàm tìm kiếm thị trường..."
✅ ĐÚNG: {"function": "search_market", "args": {...}}
```

---

## 1.5 Function Calling và cách hoạt động

### 1.5.1 Function Calling là gì?

**Function Calling** là kỹ thuật cho phép LLM **gọi các hàm (tools) bên ngoài** thay vì chỉ tạo văn bản.

### 1.5.2 Cách hoạt động

```
┌──────────────────────────────────────────────┐
│        USER MESSAGE                          │
│  "Tìm kiếm thị trường cho sản phẩm này"      │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   SYSTEM PROMPT (Khai báo các tools)        │
│  Tools: [                                    │
│    {name: "search_market", params: {...}}   │
│    {name: "analyze", params: {...}}         │
│  ]                                           │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   LLM REASONING                              │
│   "Người dùng muốn tìm kiếm thị trường"     │
│   "Tôi nên gọi search_market"               │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   OUTPUT: FUNCTION CALL (JSON)               │
│  {                                           │
│    "function": "search_market",              │
│    "arguments": {                            │
│      "product": "sản phẩm này",              │
│      "target_market": "Vietnam"              │
│    }                                         │
│  }                                           │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   EXECUTE FUNCTION (Backend)                 │
│   result = search_market(                    │
│     product="sản phẩm này",                  │
│     target_market="Vietnam"                  │
│   )                                          │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   RETURN RESULT TO LLM                       │
│  "Kết quả tìm kiếm: ..."                    │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   LLM GENERATE FINAL ANSWER                  │
│  "Dựa trên kết quả tìm kiếm, thị trường..." │
└──────────────────────────────────────────────┘
```

### 1.5.3 Ví dụ Function Calling trong MarketMind AI

```python
# Tools định nghĩa
TOOLS = [
    {
        "name": "search_market",
        "description": "Tìm kiếm thông tin thị trường",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Tên sản phẩm"},
                "market": {"type": "string", "description": "Thị trường cần tìm"}
            }
        }
    },
    {
        "name": "generate_strategy",
        "description": "Tạo chiến lược marketing",
        "parameters": {
            "type": "object",
            "properties": {
                "market_data": {"type": "string"},
                "budget": {"type": "number"}
            }
        }
    },
    {
        "name": "generate_content",
        "description": "Tạo nội dung quảng cáo",
        "parameters": {
            "type": "object",
            "properties": {
                "strategy": {"type": "string"},
                "platform": {"type": "string"}
            }
        }
    }
]

# LLM được cấp danh sách tools
system_prompt = """
Bạn là AI Marketing Assistant. Bạn có các công cụ sau:
""" + format_tools(TOOLS)

# User hỏi
user_input = "Hãy lập chiến lược marketing cho iPhone 15 với ngân sách 10 triệu VNĐ"

# LLM trả lời với function calling
llm_output = {
    "function": "search_market",
    "arguments": {
        "product": "iPhone 15",
        "market": "Vietnam"
    }
}
```

---

## 1.6 Chat Template và cấu trúc tin nhắn

### 1.6.1 Chat Template là gì?

**Chat Template** là định dạng đặc biệt để **cấu trúc hội thoại** giữa user, system, và AI, và **định vị nơi truyền function calling**.

### 1.6.2 Chat Template của Llama

```
<s>[INST] <<SYS>>
You are a helpful AI assistant. You have access to the following tools:
[
  {
    "name": "search_market",
    "description": "Search market information",
    "parameters": {...}
  }
]
<</SYS>>

User: Tìm kiếm thị trường cho iPhone 15 [/INST]