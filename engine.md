# Báo Cáo Dự Án: Xây Dựng Web Chat AI Tương Tự Grok (Streaming + Real-time Status)

**Tác giả:** to quang  
**Ngày tạo:** 26/02/2026  
**Mục tiêu:** Xây dựng một web chat AI có giao diện và trải nghiệm gần giống Grok/Claude/ChatGPT, với backend Python chạy qua file `.ipynb` (Jupyter Notebook) và frontend React.  
**Yêu cầu quan trọng:**  
- AI inference mất nhiều thời gian → phải có **real-time streaming** (token-by-token) và **status cập nhật liên tục** (Đang suy nghĩ → Đang sinh câu trả lời…).  
- Backend chạy hoàn toàn trong file `.ipynb` (không dùng file `.py` riêng cho server).  
- Frontend dùng **React** (Vite + TypeScript khuyến nghị).

---

## 1. Mục tiêu tổng quát của dự án

- Người dùng chat với AI (có sẵn trong file A_stage_local_marketing_agent.ipynb).
- Backend stream token theo thời gian thực + gửi status.
- Lưu lịch sử chat theo `conversation_id`.
- Giao diện hiện đại, mượt mà.
- Dễ mở rộng sau này (auth, multi-model, RAG…).

---

## 2. Tech Stack

| Layer          | Công nghệ                              | Lý do chọn |
|----------------|----------------------------------------|----------|
| **Backend**    | Python + FastAPI (ASGI)                | Async native, hỗ trợ SSE cực tốt |
| **Backend run**| Jupyter Notebook (`.ipynb`)            | Yêu cầu của user |
| **Real-time**  | Server-Sent Events (SSE)               | Nhẹ, dễ implement, tự reconnect |
| **AI Layer**   | LangChain hoặc trực tiếp OpenAI-compatible | Dễ stream |
| **Frontend**   | React 19 (Vite + TypeScript + TailwindCSS) | Hiện đại, dễ quản lý state |
| **Database**   | SQLite (ban đầu) → PostgreSQL sau     | Đơn giản cho dev |
| **State quản lý** | Zustand hoặc Redux Toolkit           | Quản lý conversation |
| **Deployment** | (sau) Docker + Railway/Render          | - |

---

## 3. Kiến trúc hệ thống (High-level)
Frontend (React)
↓ (fetch POST + EventSource SSE)
Backend (FastAPI chạy trong .ipynb)
↓
AI Engine
↓ (stream tokens + status)
SSE → Frontend (real-time token + status)