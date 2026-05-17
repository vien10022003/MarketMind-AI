# 🔍 MarketMind AI Android — Audit & Fix Plan

## Tổng quan hiện trạng

AI trước đã scaffold được **~70% file structure** nhưng có nhiều vấn đề quan trọng chưa hoàn thiện:

### ❌ Các vấn đề chính

| # | Vấn đề | Mức độ | File liên quan |
|---|--------|--------|----------------|
| 1 | **MainActivity dùng fake data** — `Thread.sleep(2000)` thay vì gọi backend thật | 🔴 Critical | `MainActivity.java` |
| 2 | **Drawer sidebar trống** — Không inflate conversation list, không load data | 🔴 Critical | `MainActivity.java`, `activity_main.xml` |
| 3 | **Không có nút Logout** — Toolbar thiếu menu logout/user info | 🔴 Critical | `MainActivity.java`, `activity_main.xml` |
| 4 | **API endpoint sai** — Android dùng `/api/stage_a_research` nhưng frontend dùng `/api/research/stage_a` | 🔴 Critical | `ResearchService.java` |
| 5 | **Conversation API parse sai** — Backend trả về `{data: {conversations: [...]}}` nhưng code parse trực tiếp thành `List<Conversation>` | 🔴 Critical | `ResearchService.java` |
| 6 | **Thiếu header `ngrok-skip-browser-warning`** — Tất cả request sẽ bị ngrok block | 🟡 High | `ResearchService.java` |
| 7 | **ChatAdapter quá đơn giản** — Mọi loại message ngoài user/assistant/error đều hiển thị là status | 🟡 Medium | `ChatAdapter.java` |
| 8 | **Stream handler chưa xử lý trên UI thread** — `runOnUiThread` thiếu | 🟡 High | `MainActivity.java` |

### ✅ Những gì đã làm tốt
- Splash → Auth → Main flow hoạt động
- ApiConfig lấy URL từ Firebase
- AuthService đầy đủ login/register/Google
- Model classes đầy đủ
- Layout XML cho mọi loại chat message
- Build.gradle dependencies đúng

---

## 📋 Kế hoạch sửa (5 Phases)

### Phase 1: Fix API + Backend Connection
1. Sửa endpoint URLs trong `ResearchService.java` cho khớp frontend
2. Thêm `ngrok-skip-browser-warning` header
3. Sửa Conversation API parsing (unwrap `{data: ...}`)
4. Kết nối `MainActivity` với `ResearchService` thật (thay `Thread.sleep`)

### Phase 2: Sidebar + Chat History
1. Inflate drawer layout + setup RecyclerView trong drawer
2. Load danh sách conversations từ backend
3. Click conversation → load messages
4. Nút "New Chat" hoạt động

### Phase 3: Logout + User Info
1. Thêm overflow menu vào toolbar (logout, user name)
2. Gọi `AuthService.logout()` → redirect về `AuthActivity`

### Phase 4: Cải thiện UI
1. Nâng cấp ChatAdapter xử lý đúng các message types
2. Cải thiện drawer UI + welcome hero

### Phase 5: Stream Handler
1. Xử lý đầy đủ stream events giống frontend `handleStreamMessage`
2. Auto-save messages to conversation

---

> [!IMPORTANT]
> Bạn muốn tôi bắt đầu implement từ Phase nào? Tôi khuyên bắt đầu từ **Phase 1 + 2 + 3** cùng lúc vì chúng liên quan chặt chẽ nhau.
