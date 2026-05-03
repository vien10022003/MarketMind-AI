# API Sinh Ảnh từ Text

Chạy cell cuối cùng trong notebook `GenTextToImage.ipynb` để khởi động API.

**Lưu ý:** API tự động tải ảnh lên imgbb và chỉ trả về URL thay vì base64, giúp phản hồi nhẹ và nhanh hơn.

Ngrok tunnel URL sẽ được in ra, ví dụ: `https://xxxx-xx-xxx-xxx.ngrok.io`



## Cách Dùng

### 1. Sinh 1 ảnh
```javascript
const response = await fetch('https://YOUR_NGROK_URL/generate-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'a beautiful sunset',
    num_inference_steps: 50 //chất lượng ảnh
  })
});

const data = await response.json();
// data.image_url là URL của ảnh trên imgbb
```

### 2. Sinh nhiều ảnh
```javascript
const response = await fetch('https://YOUR_NGROK_URL/generate-batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompts: ['a dog', 'a cat', 'a bird'],
    num_inference_steps: 50
  })
});

const data = await response.json();
// data.images là mảng các ảnh với image_url
```

### 3. Kiểm tra API
```javascript
fetch('https://YOUR_NGROK_URL/health').then(r => r.json()).then(console.log);
```

## Kết Quả

**Sinh 1 ảnh:**
```json
{
  "success": true,
  "image_url": "https://i.ibb.co/xxxxx/image.png",
  "prompt": "your prompt",
  "message": "Image generated and uploaded successfully"
}
```

**Sinh nhiều ảnh:**
```json
{
  "success": true,
  "images": [
    { "prompt": "a dog", "image_url": "https://i.ibb.co/xxxxx/dog.png" },
    { "prompt": "a cat", "image_url": "https://i.ibb.co/yyyyy/cat.png" }
  ],
  "total": 2,
  "message": "Generated 2 images successfully"
}
```

**Lỗi:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Tham số

| Tham số | Mặc định | Ghi chú |
|---------|----------|--------|
| `prompt` | - | Bắt buộc |
| `prompts` | - | Bắt buộc (batch) |
| `num_inference_steps` | 50 | Tùy chọn, 20-100 |
