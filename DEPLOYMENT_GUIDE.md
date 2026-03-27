# 🚀 Deployment Guide - MarketMind AI

## Giải Đáp: Tại Sao Không Dùng Ngrok Ban Đầu?

Notebook `A_stage_local_marketing_agent.ipynb` ban đầu **chỉ chạy local** vì:
- ✅ Dễ test và debug trên máy cá nhân
- ✅ Không cần expose API công khai
- ✅ Streaming hoạt động bình thường với streaming response (chunked transfer encoding)

**Nhưng:** Ngrok **hoàn toàn hỗ trợ streaming**! Ngrok chỉ là HTTP tunnel, không ảnh hưởng đến chunked transfer.

---

## 📋 Setup & Deploy với Ngrok

### Bước 1: Tạo Ngrok Account & Lấy Auth Token

1. Truy cập https://ngrok.com/
2. Đăng ký free account
3. Vào https://dashboard.ngrok.com/auth/your-authtoken
4. Copy auth token

### Bước 2: Cấu Hình Backend `.env`

```bash
# Tại thư mục backend/
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
LANGCHAIN_API_KEY=sk_...
TAVILY_API_KEY=tvly_...
MONGO_URI=mongodb+srv://...
NGROK_AUTH_TOKEN=2pysQCK1Q5pfYjsY0bgQ4sTQlQR_3AHt1g9v6kTn7erPhaRNA
```

### Bước 3: Chạy Notebook Backend

Chạy notebook `A_stage_local_marketing_agent.ipynb` từ đầu đến cuối:

1. Cell 1: Cài dependencies
2. Cell 2-14: Setup LLM, Planning, ReAct, MongoDB, Flask
3. **Cell 15-17** (MỚI): Setup Ngrok & Start Server

Khi chạy xong, bạn sẽ thấy output:
```
✅ API PUBLIC URL: https://abc-123-ngrok.io
✅ Endpoint: https://abc-123-ngrok.io/api/research/stage_a
```

### Bước 4: Cấu Hình Frontend

Chỉnh sửa `frontend/src/config.ts`:

```typescript
const ACTIVE_BACKEND_URL = BACKEND_NGROK;  // Đổi thành này

const BACKEND_NGROK = 'https://abc-123-ngrok.io';  // Thay bằng PUBLIC URL từ notebook
```

### Bước 5: Chạy Frontend

```bash
cd frontend
npm run dev
```

Truy cập http://localhost:5173/ → App sẽ call API qua ngrok tunnel

---

## 🔗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                               │
│  http://localhost:5173/                                │
└────────────┬────────────────────────────────────────────┘
             │ fetch('/api/research/stage_a')
             │ (ngrok streaming response)
             ▼
┌─────────────────────────────────────────────────────────┐
│  Ngrok Tunnel (Public URL)                             │
│  https://abc-123-ngrok.io                              │
└────────────┬────────────────────────────────────────────┘
             │ HTTP Forward
             ▼
┌─────────────────────────────────────────────────────────┐
│  Flask Server (Backend)                                │
│  http://localhost:5000                                 │
│  - POST /api/research/stage_a (Streaming NDJSON)       │
│  - GET /health                                         │
└────────────┬────────────────────────────────────────────┘
             │
             ├─→ Tavily Web Search API
             ├─→ Local LLM (Llama/Arcee)
             └─→ MongoDB (save reports)
```

---

## ✅ Streaming Qua Ngrok - Hoạt Động Bình Thường!

### Frontend Code (Automatic)
File `frontend/src/services/researchService.ts` đã hỗ trợ streaming:

```typescript
const reader = response.body.getReader();  // ✅ Hoạt động qua ngrok
const decoder = new TextDecoder('utf-8');

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  // Process NDJSON chunks
  const data = JSON.parse(line);
  onMessage(data);  // Update UI real-time
}
```

### Backend Code (Automatic)
File `A_stage_local_marketing_agent.ipynb` Cell 15 trả về:

```python
@app.route('/api/research/stage_a', methods=['POST'])
def api_research_stage_a():
    return Response(
        stream_with_context(run_stage_a_pipeline_generator(data)),
        content_type='application/x-ndjson',
        headers={'Transfer-Encoding': 'chunked'}  # ✅ Streaming
    )
```

**Ngrok sẽ forward chunked transfer encoding bình thường!**

---

## 🐛 Troubleshooting

### Problem: "Ngrok not found"
```bash
pip install pyngrok
```

### Problem: "NGROK_AUTH_TOKEN invalid"
```
- Kiểm tra token ở https://dashboard.ngrok.com/auth/your-authtoken
- Copy lại vào .env
```

### Problem: Frontend không gọi được API
```
1. Kiểm tra PUBLIC URL từ notebook output
2. Cập nhật BACKEND_NGROK trong frontend/src/config.ts
3. Restart frontend: npm run dev
```

### Problem: Streaming chậm
- Điều này là **bình thường** khi:
  - Local LLM đang synthesize report (có thể mất 1-2 phút)
  - Web search chạy (Tavily API)
- Xem progress messages trong UI để biết đang chạy bên nào

### Problem: "CORS error"
- Flask server đã có `CORS(app)` enabled
- Kiểm tra browser console để xem chi tiết lỗi

---

## 📊 So Sánh: Local vs Ngrok

| Aspect | Local | Ngrok |
|--------|-------|-------|
| URL | http://localhost:5000 | https://xxx.ngrok.io |
| Streaming | ✅ Yes | ✅ Yes |
| Setup | ✅ Simple | ⚠️ Need auth token |
| Share | ❌ Localhost only | ✅ Public URL |
| Latency | ✅ Fastest | ⚠️ +50-100ms tunnel |
| Cost | ✅ Free | ✅ Free tier |

---

## 🎯 Best Practices

1. **Development**: Dùng Local (`http://localhost:5000`)
   - Chạy frontend & backend trên cùng máy
   - Fastest, easiest debug

2. **Testing with External Users**: Dùng Ngrok
   - Share PUBLIC URL với colleagues
   - Test trên mobile, other devices

3. **Production**: Dùng Cloud Hosting (AWS, GCP, etc.)
   - Deploy Flask server lên VPS
   - Use proper domain + SSL certificate
   - Setup CI/CD pipeline

---

## 📚 Reference

- [Ngrok Official Docs](https://ngrok.com/docs)
- [Flask Streaming Response](https://flask.palletsprojects.com/streaming)
- [Fetch API ReadableStream](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
- [NDJSON Format](http://ndjson.org/)

---

**Created:** March 26, 2026  
**Version:** 1.0.0  
**Status:** Ready for Deployment ✅
