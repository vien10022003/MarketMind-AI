# Scheduled Posting Guide - Stage C

## Overview

Stage C now supports **scheduled posting** of content briefs to Discord. This allows you to:

- Schedule content briefs to be posted at specific times
- Automatically execute posts when the scheduled time arrives
- Track scheduled and posted briefs
- Monitor execution status in real-time

## How It Works

### Two Execution Modes

1. **Immediate Mode (Default)**
   - Posts all briefs immediately as they are processed
   - Traditional behavior - fast feedback
   - Best for urgent campaigns

2. **Scheduled Mode**
   - Saves briefs with scheduled posting times
   - Background scheduler monitors and executes at the right time
   - Allows gap between approval and posting
   - Best for planned campaigns with specific timing

## Setup

### 1. Initialize Scheduler in Your Flask App

Add to your `flask_api.py` or main app initialization:

```python
from stage_c.campaign_scheduler import initialize_scheduler
from stage_c.scheduler_service import initialize_scheduler_service
from stage_c.scheduler_routes import create_scheduler_blueprint

# Initialize scheduler (once at app startup)
initialize_scheduler()

# Start background scheduler service (runs in daemon thread)
scheduler_service = initialize_scheduler_service(auto_start=True)

# Register scheduler API routes
app.register_blueprint(create_scheduler_blueprint())
```

### 2. Ensure MongoDB is Running

Scheduled campaigns are stored in MongoDB. Make sure:
- MongoDB is accessible at `MONGODB_URI` (default: `mongodb://localhost:27017`)
- Database `marketmind` is accessible (auto-created if needed)

## API Reference

### Scheduler Management

#### Get Scheduler Status
```
GET /api/stage-c/scheduler/status
```
Response:
```json
{
  "success": true,
  "data": {
    "running": true,
    "pending_briefs": 5,
    "check_interval": 60
  }
}
```

#### Start Scheduler Service
```
POST /api/stage-c/scheduler/start
```

#### Stop Scheduler Service
```
POST /api/stage-c/scheduler/stop
```

#### Configure Scheduler
```
POST /api/stage-c/scheduler/config
Content-Type: application/json

{
  "check_interval": 30
}
```

### Campaign Management

#### List All Campaigns
```
GET /api/stage-c/scheduler/campaigns?status=scheduled
```

Query Parameters:
- `status`: Filter by status (scheduled, completed, failed, etc.)

Response:
```json
{
  "success": true,
  "data": {
    "total": 2,
    "campaigns": [
      {
        "campaign_id": "abc12345",
        "mongodb_stage_a_id": "stage_a_id",
        "status": "scheduled",
        "total_briefs": 3,
        "total_posted": 1,
        "total_scheduled": 2,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

#### Get Campaign Details
```
GET /api/stage-c/scheduler/campaigns/{campaign_id}
```

#### Get Campaign Execution Results
```
GET /api/stage-c/scheduler/campaigns/{campaign_id}/results
```

Response:
```json
{
  "success": true,
  "data": {
    "campaign_id": "abc12345",
    "status": "scheduled",
    "total_results": 3,
    "posted_count": 1,
    "failed_count": 0,
    "results": [
      {
        "brief_id": "brief-1",
        "brief_title": "Product Launch",
        "status": "success",
        "discord_sent": true,
        "scheduled_post_time": "2024-01-15T14:00:00Z",
        "posted_at": "2024-01-15T14:00:05Z"
      }
    ]
  }
}
```

#### Get Pending Briefs
```
GET /api/stage-c/scheduler/pending
```

Response:
```json
{
  "success": true,
  "data": {
    "total_campaigns_pending": 1,
    "total_briefs_pending": 2,
    "campaigns": [
      {
        "campaign_id": "abc12345",
        "pending_briefs_count": 2,
        "briefs_preview": [
          {
            "index": 1,
            "title": "Community Event",
            "scheduled_time": "2024-01-15T16:00:00Z"
          }
        ]
      }
    ]
  }
}
```

## Usage Example

### 1. Stage C with Scheduled Posting

Frontend sends:
```python
{
  "execution_mode": "scheduled",
  "scheduled_times": [
    "2024-01-15T09:00:00Z",
    "2024-01-15T14:00:00Z",
    "2024-01-15T18:00:00Z"
  ],
  "approved_briefs": [...]
}
```

### 2. Backend Creates Scheduled Campaign

```python
from stage_c.data_models_c import StageCInput

stage_c_input = StageCInput(
    approved_briefs=briefs,
    execution_mode="scheduled",
    scheduled_times=scheduled_times,
    mongodb_stage_a_id=stage_a_id,
)

# Stream the campaign creation
for event in run_stage_c_pipeline(stage_c_input):
    if event["status"] == "stage_c_completed":
        # Campaign scheduled successfully
        campaign_log = event["campaign_log"]
```

### 3. Background Scheduler Monitors

```
Every 60 seconds:
- Check for campaigns with pending briefs
- If scheduled time <= now:
  - Generate image
  - Format Discord embed
  - Post to Discord
  - Log result
  - Update campaign status
```

### 4. Track Campaign Progress

```bash
# Check pending briefs
curl http://localhost:5000/api/stage-c/scheduler/pending

# Get campaign results
curl http://localhost:5000/api/stage-c/scheduler/campaigns/abc12345/results

# Get all scheduled campaigns
curl http://localhost:5000/api/stage-c/scheduler/campaigns?status=scheduled
```

## Data Models

### ExecutionResult (Updated)
```python
class ExecutionResult(BaseModel):
    brief_id: str
    brief_title: str
    status: str  # pending | scheduled | success | failed | skipped
    image_url: Optional[str]
    discord_sent: bool
    error: Optional[str]
    scheduled_post_time: Optional[str]  # ISO datetime
    posted_at: Optional[str]  # ISO datetime when actually posted
    created_at: str  # ISO datetime
```

### CampaignLog (Updated)
```python
class CampaignLog(BaseModel):
    campaign_id: str
    mongodb_stage_a_id: Optional[str]
    results: List[ExecutionResult]
    total_briefs: int
    total_posted: int
    total_scheduled: int  # New: briefs pending posting
    total_failed: int
    total_skipped: int
    execution_mode: str  # "immediate" | "scheduled"
    started_at: str
    completed_at: Optional[str]
```

### StageCInput (Updated)
```python
class StageCInput(BaseModel):
    approved_briefs: List[dict]
    execution_mode: str  # "immediate" | "scheduled"
    scheduled_times: Optional[List[str]]  # ISO datetimes (one per brief)
    webhook_url: Optional[str]
    image_api_url: Optional[str]
    skip_image_generation: bool
    mongodb_stage_a_id: Optional[str]
```

## Monitoring

### MongoDB Collections

**scheduled_campaigns**
```
{
  _id: ObjectId,
  campaign_id: "abc12345",
  mongodb_stage_a_id: "stage_a_id",
  briefs: [...],
  scheduled_times: ["2024-01-15T09:00:00Z", ...],
  webhook_url: "https://discord.com/api/webhooks/...",
  status: "scheduled|completed|failed",
  execution_results: [...],
  posted_count: 1,
  failed_count: 0,
  created_at: "2024-01-15T10:30:00Z",
  completed_at: "2024-01-15T18:05:00Z"
}
```

### Logging

The scheduler logs all activity:
```
✅ Campaign abc12345 saved to scheduler
📅 Executing campaign abc12345: 2 briefs
📝 Processing: Product Launch
✅ Image generated for Product Launch
✅ Posted: Product Launch
🎉 Campaign abc12345 completed!
```

## Configuration

### Check Interval

Set how often the scheduler checks for pending briefs:

```bash
curl -X POST http://localhost:5000/api/stage-c/scheduler/config \
  -H "Content-Type: application/json" \
  -d '{"check_interval": 30}'
```

- Default: 60 seconds
- Minimum recommended: 30 seconds
- Trade-off: faster posting vs lower CPU usage

## Troubleshooting

### Scheduler Not Running

1. Check if service started:
   ```bash
   curl http://localhost:5000/api/stage-c/scheduler/status
   ```

2. Manually start:
   ```bash
   curl -X POST http://localhost:5000/api/stage-c/scheduler/start
   ```

### Posts Not Being Posted

1. Check pending briefs:
   ```bash
   curl http://localhost:5000/api/stage-c/scheduler/pending
   ```

2. Check campaign details:
   ```bash
   curl http://localhost:5000/api/stage-c/scheduler/campaigns/CAMPAIGN_ID
   ```

3. Verify Discord webhook is valid in scheduled campaign

4. Check MongoDB connection

### Timing Issues

- Ensure server time is synchronized (NTP)
- Consider timezone when setting scheduled times (use UTC/ISO 8601 format)
- Increase check_interval if system load is high

## Best Practices

1. **Use UTC/ISO 8601 Format**
   ```
   2024-01-15T14:30:00Z  ✅ Good
   2024-01-15 14:30:00   ❌ Avoid
   ```

2. **Space Out Posts**
   - Avoid posting all briefs at the same second
   - Consider Discord rate limits
   - Example: 5 minutes apart

3. **Monitor Scheduler Health**
   - Periodically check `/api/stage-c/scheduler/status`
   - Monitor pending_briefs_count
   - Check MongoDB storage usage

4. **Archive Old Campaigns**
   - Implement cleanup for completed campaigns
   - Keep recent 100 campaigns for audit

## Future Enhancements

- [ ] Reschedule failed briefs
- [ ] Batch scheduling with intervals
- [ ] Timezone-aware scheduling
- [ ] Campaign templates
- [ ] A/B testing with scheduled variations
- [ ] Webhook notifications on post completion
