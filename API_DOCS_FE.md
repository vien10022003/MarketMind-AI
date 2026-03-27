# Tài Liệu Giao Tiếp API - Stage A Market Research Agent

Tài liệu này cung cấp các thông tin cần thiết cho đội ngũ Frontend (FE) để kết nối và hiển thị dữ liệu từ Backend của Agent phân tích thị trường Giai đoạn A. API này sử dụng cơ chế phản hồi theo luồng (Streaming) để FE có thể hiển thị tiến trình theo thời gian thực thay vì phải chờ rất lâu.

## 1. Tổng quan Endpoint

- **Endpoint URL:** `http://127.0.0.1:5000/api/research/stage_a`
- **HTTP Method:** `POST`
- **Request Content-Type:** `application/json`
- **Response Content-Type:** `application/x-ndjson` (Luồng các JSON object, mỗi object trên một dòng phân cách bởi `\n`)

---

## 2. Request Body (Thông tin đầu vào)

FE cần gửi một JSON body chứa các tham số cấu hình cuộc nghiên cứu.

| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| `nganh_hang` | `string` | **Có** | | Tên ngành hàng, lĩnh vực kinh doanh (VD: "Mỹ phẩm thuần chay") |
| `thi_truong_muc_tieu` | `string` | **Có** | | Phạm vi thị trường (VD: "Việt Nam") |
| `phan_khuc_quan_tam` | `string[]` | Không | `[]` | Các tệp khách hàng hướng tới (VD: `["Gen Z", "Da nhạy cảm"]`) |
| `doi_thu_seed` | `string[]` | Không | `[]` | Các đối thủ ban đầu để tham chiếu (VD: `["Cocoon"]`) |
| `khung_thoi_gian` | `string` | Không | `"12 thang gan nhat"` | Mốc thời gian để tìm kiếm dữ liệu (VD: `"2024-2026"`) |
| `muc_tieu_nghien_cuu` | `string[]` | Không | `[]` | Các mục tiêu cụ thể muốn LLM xoáy sâu vào (VD: `["Độ lớn thị trường"]`) |

### Mẫu Request JSON:
```json
{
  "nganh_hang": "Mỹ phẩm thuần chay",
  "thi_truong_muc_tieu": "Việt Nam",
  "phan_khuc_quan_tam": ["Gen Z", "Người mua trên sàn TMĐT"],
  "doi_thu_seed": ["Cocoon", "The Body Shop", "Innisfree"],
  "khung_thoi_gian": "2024-2026",
  "muc_tieu_nghien_cuu": [
    "Độ lớn thị trường",
    "Đối thủ và định vị",
    "Xu hướng hành vi mua hàng",
    "Insight phân khúc"
  ]
}
```

---

## 3. Response Format (Luồng Stream)

Do việc lên kế hoạch, crawl web và chạy Local LLM mất nhiều thời gian, API trả về dữ liệu stream theo chuẩn NDJSON (Newline Delimited JSON). Điều này có nghĩa là mỗi chunk trả về là một chuỗi JSON hợp lệ, kết thúc bằng kí tự xuống dòng `\n`.

Mỗi dòng JSON (chunk) sẽ luôn có các trường cơ bản:
- `status`: Trạng thái thực thi (`starting` | `progress` | `completed` | `error`)
- `message`: Thông báo tiến độ (Có thể dùng trực tiếp để hiển thị loading text lên UI cho user).

### A. Các trạng thái đang xử lý (`starting`, `progress`)
Ví dụ các dữ liệu trả về theo thời gian:
```json
{"status": "starting", "message": "Khởi tạo tác vụ Giai đoạn A..."}
{"status": "progress", "message": "Xác thực đầu vào thành công."}
{"status": "progress", "message": "Đang lập kế hoạch (Planning)..."}
{"status": "progress", "message": "Lập kế hoạch hoàn tất.", "plan_summary": {...}}
{"status": "progress", "message": "Đang tổng hợp báo cáo bằng Local LLM (có thể mất thời gian)..."}
```

### B. Trạng thái kết thúc thành công (`completed`)
Khi chạy thành công, chunk cuối cùng sẽ có trạng thái `completed` đi kèm `mongodb_id` và đối tượng `report` hoàn chỉnh bao gồm 4 phần phân tích và citations.

```json
{
  "status": "completed",
  "message": "Chiến dịch hoàn thành",
  "mongodb_id": "651a2b3c4d5e...",
  "report": {
    "tong_quan_thi_truong": "Nội dung phân tích tổng quan...",
    "phan_tich_doi_thu": "Nội dung phân tích đối thủ...",
    "xu_huong_nganh": "Nội dung xu hướng ngành...",
    "phan_khuc_va_insight_khach_hang": "Nội dung phân khúc và insight...",
    "citations": [
      {
        "title": "Báo cáo thị trường mỹ phẩm VN 2025",
        "url": "https://example.com/bao-cao",
        "snippet": "Quy mô thị trường đạt 3 tỷ USD...",
        "published_date": "2024-01-01",
        "source_score": 0.85
      }
    ]
  }
}
```

### C. Trạng thái lỗi (`error`)
Nếu có lỗi xảy ra ở bất kỳ bước nào trong pipeline, stream sẽ kết thúc sớm với payload như sau:
```json
{
  "status": "error",
  "message": "Bị lỗi trong quá trình thực thi: <Chi_tiết_lỗi_của_hệ_thống>"
}
```

---

## 4. Hướng dẫn Parsing ở Frontend (Tham khảo)

Frontend khi fetch API nên sử dụng Fetch API mặc định của trình duyệt để đọc `ReadableStream`.

**Mẫu code JavaScript dùng Fetch API kết hợp stream:**

```javascript
async function callStageA_API(requestData) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/research/stage_a', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Giải mã chunk (có thể chứa nhiều dòng có kí tự \n)
      const chunkText = decoder.decode(value, { stream: true });
      const lines = chunkText.split('\\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        const data = JSON.parse(line);
        
        // Handle logic dựa trên trạng thái
        if (data.status === 'starting' || data.status === 'progress') {
          console.log("Tiến độ:", data.message);
          // TODO: Update state UI Loading message
        } else if (data.status === 'error') {
          console.error("Pipeline gặp lỗi:", data.message);
          // TODO: Update UI show Error
        } else if (data.status === 'completed') {
          console.log("Hoàn thành báo cáo:", data.report);
          // TODO: Hide loading, show Report data
        }
      }
    }
  } catch (err) {
    console.error("Lỗi fetch API:", err);
  }
}
```