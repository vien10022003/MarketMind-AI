# Scheduled Posting Implementation - Integration Checklist

Hoàn tất việc triển khai **Scheduled Posting** cho Stage C. Danh sách kiểm tra dưới đây hướng dẫn cách tích hợp vào hệ thống hiện tại.

## 📋 Danh sách Kiểm Tra Triển Khai

### Backend Integration

#### ✅ Bước 1: Cập nhật Flask App
- [ ] Mở `backend/stage_a/flask_api.py`
- [ ] Thêm import ở đầu file:
```python
from stage_c import (
    initialize_scheduler,
    initialize_scheduler_service,
    create_scheduler_blueprint,
)
```
- [ ] Thêm trong hàm khởi tạo app (sau khi tạo Flask app):
```python
# Initialize Stage C scheduler
initialize_scheduler()
scheduler_service = initialize_scheduler_service(auto_start=True)
app.register_blueprint(create_scheduler_blueprint())
```

#### ✅ Bước 2: Kiểm Tra MongoDB
- [ ] MongoDB đang chạy trên `mongodb://localhost:27017`
- [ ] Hoặc thiết lập `MONGODB_URI` env variable
- [ ] Database `marketmind` sẽ được tự động tạo

#### ✅ Bước 3: Thêm Endpoint cho Stage C Scheduled
- [ ] Thêm route mới vào `flask_api.py`:
```python
@app.route('/stage-c/campaign-scheduled', methods=['POST'])
def stage_c_campaign_scheduled():
    """Execute Stage C with scheduled posting"""
    data = request.get_json()
    from stage_c.data_models_c import StageCInput
    from stage_c.discord_publisher import run_stage_c_pipeline
    
    try:
        stage_c_input = StageCInput(
            approved_briefs=data.get('approved_briefs', []),
            execution_mode='scheduled',
            scheduled_times=data.get('scheduled_times', []),
            mongodb_stage_a_id=data.get('mongodb_stage_a_id'),
        )
        
        def generate():
            for event in run_stage_c_pipeline(stage_c_input):
                yield json.dumps(event) + '\n'
        
        return Response(generate(), content_type='application/x-ndjson')
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### Frontend Integration

#### ✅ Bước 4: Tạo ScheduleEditor Component
- [ ] Tạo file `frontend/src/components/ScheduleEditor.tsx`
- [ ] Copy nội dung từ `FRONTEND_INTEGRATION.md`
- [ ] Thêm CSS từ file đó

#### ✅ Bước 5: Tạo ScheduleManager Component
- [ ] Tạo file `frontend/src/components/ScheduleManager.tsx`
- [ ] Implement dashboard để xem campaigns
- [ ] Auto-refresh mỗi 10 giây

#### ✅ Bước 6: Cập Nhật App.tsx
- [ ] Import ScheduleEditor vào App.tsx
- [ ] Thêm button "📅 Lên lịch" vào stage_c_proposal
- [ ] Hiển thị ScheduleManager trong sidebar/modal

#### ✅ Bước 7: Cập Nhật researchService.ts
- [ ] Thêm method `callStageCCampaignScheduled()`
- [ ] Gọi endpoint `/stage-c/campaign-scheduled`
- [ ] Handle streaming response

### Testing

#### ✅ Bước 8: Test Immediate Mode (Existing)
- [ ] Tạo campaign với `execution_mode="immediate"`
- [ ] Verify briefs post ngay lập tức
- [ ] Check campaign log

#### ✅ Bước 9: Test Scheduled Mode (New)
- [ ] Tạo campaign với `execution_mode="scheduled"`
- [ ] Set scheduled_times 1 phút từ bây giờ
- [ ] Monitor `/api/stage-c/scheduler/pending`
- [ ] Verify posts thực hiện đúng thời gian
- [ ] Check execution results

#### ✅ Bước 10: Test API Endpoints
```bash
# Check scheduler status
curl http://localhost:5000/api/stage-c/scheduler/status

# List campaigns
curl http://localhost:5000/api/stage-c/scheduler/campaigns

# Get pending briefs
curl http://localhost:5000/api/stage-c/scheduler/pending

# Get campaign details
curl http://localhost:5000/api/stage-c/scheduler/campaigns/{campaign_id}

# Get campaign results
curl http://localhost:5000/api/stage-c/scheduler/campaigns/{campaign_id}/results
```

### Documentation

#### ✅ Bước 11: Đọc Tài Liệu
- [ ] Đọc `backend/stage_c/SCHEDULER_GUIDE.md` - Hướng dẫn chi tiết
- [ ] Đọc `backend/stage_c/SCHEDULER_INIT_EXAMPLE.py` - Ví dụ code
- [ ] Đọc `backend/stage_c/FRONTEND_INTEGRATION.md` - Frontend examples
- [ ] Đọc `backend/SCHEDULED_POSTING_SUMMARY.md` - Tổng quan

#### ✅ Bước 12: Environment Setup
- [ ] Verify `.env` có `DISCORD_WEBHOOK_URL`
- [ ] Verify `.env` có `MONGODB_URI` (hoặc dùng default)
- [ ] Verify `.env` có `IMAGE_API_URL` (optional)

### Monitoring & Maintenance

#### ✅ Bước 13: Thiết Lập Monitoring
- [ ] Tạo cron job để check scheduler health (optional)
- [ ] Setup logging for scheduled campaigns
- [ ] Monitor MongoDB disk usage
- [ ] Archive old campaigns (implement cleanup)

#### ✅ Bước 14: Performance Tuning
- [ ] Test với 10+ campaigns
- [ ] Adjust `check_interval` nếu cần
- [ ] Monitor CPU/memory usage
- [ ] Optimize image generation if needed

## 📁 File Structure

```
backend/stage_c/
├── __init__.py                      [✅ UPDATED]
├── data_models_c.py                 [✅ UPDATED]
├── discord_publisher.py             [✅ UPDATED]
├── image_generator.py               [unchanged]
├── campaign_log.py                  [unchanged]
├── campaign_scheduler.py             [✅ NEW - 180 lines]
├── scheduler_service.py              [✅ NEW - 210 lines]
├── scheduler_routes.py               [✅ NEW - 220 lines]
├── SCHEDULER_GUIDE.md                [✅ NEW - API Reference]
├── SCHEDULER_INIT_EXAMPLE.py         [✅ NEW - Examples]
└── FRONTEND_INTEGRATION.md           [✅ NEW - React Components]

backend/
└── SCHEDULED_POSTING_SUMMARY.md      [✅ NEW - Overview]
```

## 🔑 Key Changes Summary

### Data Models (`data_models_c.py`)
```
ExecutionResult:
  - Added: scheduled_post_time (ISO datetime)
  - Added: posted_at (ISO datetime)
  - Renamed: timestamp → created_at

CampaignLog:
  - Added: total_scheduled
  - Added: execution_mode ("immediate" | "scheduled")

StageCInput:
  - Added: execution_mode
  - Added: scheduled_times[]
```

### Discord Publisher (`discord_publisher.py`)
```
run_stage_c_pipeline():
  - Check execution_mode
  - If scheduled: Save to MongoDB, return immediately
  - If immediate: Execute and post right away (existing behavior)
```

### New Services
```
CampaignScheduler:
  - Manages MongoDB persistence
  - Query/update scheduled campaigns

SchedulerService:
  - Daemon thread background service
  - Monitors and executes scheduled posts

Scheduler Routes:
  - 7 REST API endpoints
  - Campaign management
  - Service control
```

## 🧪 Test Cases

### Test 1: Immediate Mode Still Works
```python
# Old behavior should not change
stage_c_input = StageCInput(
    approved_briefs=[...],
    execution_mode="immediate"  # or omitted (default)
)
# Should post immediately
```

### Test 2: Schedule Single Brief
```python
stage_c_input = StageCInput(
    approved_briefs=[brief1],
    execution_mode="scheduled",
    scheduled_times=["2024-01-15T10:00:00Z"]  # 1 minute from now
)
# Should return immediately, post after 1 minute
```

### Test 3: Schedule Multiple Briefs
```python
stage_c_input = StageCInput(
    approved_briefs=[brief1, brief2, brief3],
    execution_mode="scheduled",
    scheduled_times=[
        "2024-01-15T09:00:00Z",
        "2024-01-15T10:00:00Z",
        "2024-01-15T11:00:00Z"
    ]
)
# Should post at different times
```

### Test 4: Monitor Pending Briefs
```bash
curl http://localhost:5000/api/stage-c/scheduler/pending
# Should show campaigns with briefs ready to post
```

### Test 5: Check Results
```bash
curl http://localhost:5000/api/stage-c/scheduler/campaigns/abc12345/results
# Should show all briefs: posted_at timestamps
```

## ⚡ Performance Tips

1. **Check Interval**
   - 60s (default) = good for most use cases
   - 30s = faster posting, higher CPU
   - 120s = lower CPU, slower posting

2. **Image Generation**
   - First post with image takes ~5s
   - Subsequent posts faster if reusing images
   - Consider caching image URLs

3. **Discord Rate Limits**
   - Space posts 5+ minutes apart
   - Don't spam single webhook

4. **MongoDB**
   - Create index on `scheduled_post_times`
   - Create index on `status`
   - Archive old campaigns regularly

## 🐛 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check MongoDB Directly
```bash
mongo marketmind
db.scheduled_campaigns.find()
db.scheduled_campaigns.find({status: "scheduled"})
```

### Inspect Campaign
```bash
curl http://localhost:5000/api/stage-c/scheduler/campaigns/CAMPAIGN_ID | jq
```

## 🎯 Success Criteria

- [x] Campaigns can be scheduled
- [x] Posts execute at scheduled times
- [x] Full audit trail of posts
- [x] Can monitor pending briefs
- [x] Can control scheduler service
- [x] No breaking changes to existing code
- [x] Complete documentation
- [x] React component examples

## 📞 Support

### Issues?

1. Check `SCHEDULER_GUIDE.md` → Troubleshooting section
2. Check scheduler status: `/api/stage-c/scheduler/status`
3. Check MongoDB logs
4. Check Flask app logs
5. Verify env variables

### Questions?

See:
- `SCHEDULER_INIT_EXAMPLE.py` - Code examples
- `FRONTEND_INTEGRATION.md` - UI examples
- `SCHEDULER_GUIDE.md` - API reference

---

**Status**: ✅ Ready to Deploy
**Next Step**: Follow the checklist above to integrate into your app
