# Backend - MarketMind AI

Python Flask API implementing three-stage AI pipeline for market research and campaign execution.

---

## 📋 Overview

The backend provides REST API endpoints for:
- **Stage A**: Market research and intelligence gathering
- **Stage B**: Marketing strategy generation
- **Stage C**: Campaign execution (image generation, Discord posting)
- **Conversations**: Chat history and message management

**Technology**: Python 3.10+, Flask, Pydantic, MongoDB, LLM APIs

---

## 🏗️ Project Structure

```
backend/
├── stage_a/                    # Market Research Pipeline
│   ├── flask_api.py           # Main Flask API & endpoints
│   ├── main.py                # CLI entry point
│   ├── data_models.py         # Pydantic data models
│   ├── planning.py            # Research planning
│   ├── react.py               # ReAct reasoning loop
│   ├── evidence_processing.py # Evidence filtering & normalization
│   ├── synthesis.py           # Report synthesis
│   ├── knowledge_handler.py   # Knowledge query handling
│   ├── router.py              # Intent classification
│   ├── clarification.py       # User input clarification
│   ├── llm_provider.py        # LLM abstraction layer
│   ├── llm_config.py          # LLM initialization
│   ├── mongodb.py             # MongoDB integration
│   ├── tavily_search.py       # Web search integration
│   ├── discord_advertising.py # Discord operations
│   └── environment.py         # Config management
│
├── stage_b/                   # Strategy Generation
│   ├── campaign.py            # Strategy pipeline
│   ├── data_models_b.py       # Stage B data models
│   └── strategy.py            # SWOT & strategy logic
│
├── stage_c/                   # Campaign Execution
│   ├── discord_publisher.py   # Discord posting
│   ├── image_generator.py     # Image generation API
│   ├── content_expander.py    # Content expansion
│   ├── campaign_log.py        # Campaign logging
│   ├── campaign_scheduler.py  # Scheduled posting
│   ├── scheduler_routes.py    # Scheduler endpoints
│   ├── scheduler_service.py   # Scheduler service
│   ├── data_models_c.py       # Stage C data models
│   └── __init__.py
│
├── auth/                      # Authentication & Auth Routes
│   ├── auth_routes.py
│   ├── auth_middleware.py
│   └── auth_utils.py
│
├── finetune/                  # Fine-tuning scripts
│   ├── FinetuneTakingAI_v3.ipynb
│   ├── training_data.json
│   └── validate_data.json
│
├── reference/                 # Reference notebooks
│   ├── chat_template_*.py
│   └── *.ipynb
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Installation

### 1. Prerequisites
```bash
python --version  # Python 3.10+
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file in backend root:

```env
# ===== LLM Configuration =====
LLM_PROVIDER=llama              # llama, gemini, gpt
LLM_MODEL=meta-llama/Llama-2-7b-hf
LLM_API_KEY=your_api_key
HUGGING_FACE_TOKEN=your_hf_token

# ===== MongoDB =====
MONGO_URI=mongodb://localhost:27017/marketmind
MONGO_DB_NAME=marketmind

# ===== External APIs =====
TAVILY_API_KEY=your_tavily_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy
IMAGE_API_URL=http://localhost:8000

# ===== Server =====
PORT=5000
DEBUG=True
HOST=0.0.0.0
LOG_LEVEL=INFO

# ===== Optional: ngrok for tunneling =====
USE_NGROK=False
NGROK_AUTH_TOKEN=your_token
```

---

## 🏃 Running the Server

### Option 1: CLI Entry Point
```bash
python stage_a/main.py --serve
```

### Option 2: Direct Flask
```bash
cd stage_a
python flask_api.py
```

### Expected Output
```
[green]✅ All components initialized successfully[/green]
[green]✅ Auth blueprint registered[/green]
[green]✅ Scheduler blueprint registered[/green]
 * Running on http://0.0.0.0:5000
```

**Server URL**: `http://localhost:5000`

---

## 🔌 API Endpoints

### Stage A: Market Research

**POST** `/api/research/stage_a`
- Main research endpoint - routes between chat, knowledge, or research
- Request body:
  ```json
  {
    "user_prompt": "분석할 질문",
    "llm_provider": "llama",
    "conversation_history": []
  }
  ```
- Response: NDJSON stream with events

**POST** `/api/research/stage_a/marketing`
- Run full research pipeline (skips intent classification)
- Request body:
  ```json
  {
    "user_prompt": "user input",
    "ban_chat_san_pham": "product category",
    "khach_hang_muc_tieu": "target customer",
    "gia_tri_cot_loi": "core value",
    "gia_ca_chinh_sach": "pricing strategy",
    "llm_provider": "llama"
  }
  ```

### Stage B: Strategy Generation

**POST** `/api/strategy/stage_b`
- Generate marketing strategy from Stage A report
- Request body:
  ```json
  {
    "stage_a_report": { ... },
    "stage_a_input": { ... },
    "mongodb_id": "stage_a_id",
    "llm_provider": "llama"
  }
  ```

**POST** `/api/strategy/stage_b/approve`
- Save approved strategy and briefs
- Request body:
  ```json
  {
    "mongodb_id": "stage_a_id",
    "strategy": { ... },
    "approved_briefs": [ ... ]
  }
  ```

### Stage C: Campaign Execution

**POST** `/api/campaign/stage_c`
- Execute campaign immediately
- Request body:
  ```json
  {
    "approved_briefs": [ ... ],
    "webhook_url": "discord_url",
    "skip_image_generation": false,
    "mongodb_stage_a_id": "id",
    "llm_provider": "llama"
  }
  ```

**POST** `/api/campaign/stage_c/scheduled`
- Schedule campaign for future posting
- Request body:
  ```json
  {
    "approved_briefs": [ ... ],
    "scheduled_times": ["2026-05-30T10:00:00Z", "2026-05-31T14:00:00Z"],
    "webhook_url": "discord_url",
    "skip_image_generation": false,
    "mongodb_stage_a_id": "id"
  }
  ```

### Conversation Management

**GET** `/api/conversations?skip=0&limit=10`
- List user conversations

**POST** `/api/conversations`
- Create new conversation
- Request body:
  ```json
  {
    "title": "Optional title",
    "first_message": "First message to auto-generate title"
  }
  ```

**GET** `/api/conversations/<conversation_id>`
- Get conversation details with all messages

**POST** `/api/conversations/<conversation_id>/messages`
- Save messages to conversation
- Request body:
  ```json
  {
    "messages": [
      {
        "id": "msg_1",
        "type": "assistant",
        "content": "message text",
        "timestamp": "2026-05-28T10:00:00Z",
        "campaignLogData": { ... }
      }
    ]
  }
  ```

**PUT** `/api/conversations/<conversation_id>/title`
- Update conversation title
- Request body:
  ```json
  {
    "title": "New title"
  }
  ```

**DELETE** `/api/conversations/<conversation_id>`
- Delete conversation

### Health Check

**GET** `/health`
- Returns system status
- Response:
  ```json
  {
    "status": "healthy",
    "llm_ready": true,
    "mongodb_ready": true,
    "scheduler_running": true
  }
  ```

---

## 🔐 Authentication

All endpoints (except `/health`) require JWT authentication.

**Header Format**:
```
Authorization: Bearer <jwt_token>
```

### Get JWT Token
```bash
# Use Google OAuth or your auth endpoint
# See auth_routes.py for implementation
```

---

## 📊 Data Models

### Stage A Models
- `StageAInput`: User inputs and research parameters
- `StageAOutput`: Final research report
- `EvidenceItem`: Individual evidence piece

### Stage B Models
- `StageBInput`: Research report + parameters
- `StageBOutput`: Strategy and content briefs

### Stage C Models
- `StageCInput`: Approved briefs and execution parameters
- `ExecutionResult`: Individual brief execution result
- `CampaignLog`: Complete campaign execution log

### Conversation Models
- `ChatMessage`: Individual message
- `Conversation`: Collection of messages
- `ChatMessageDoc`: MongoDB document format

---

## 🧬 Pipeline Flow

```
1. User Input
   ↓
2. Intent Classification (Chat/Knowledge/Research)
   ├─ Chat → Return chat response
   ├─ Knowledge → Search + Answer
   └─ Research → Continue to Stage A
   ↓
3. Stage A: Market Research
   ├─ Planning (ReAct)
   ├─ Evidence Gathering (Tavily search)
   ├─ Synthesis (Report generation)
   ↓
4. Stage B: Strategy Generation
   ├─ SWOT Analysis
   ├─ USP Definition
   ├─ Persona Development
   ├─ Content Brief Generation
   ↓
5. Stage C: Campaign Execution
   ├─ Image Generation
   ├─ Discord Formatting
   ├─ Posting (Immediate or Scheduled)
   ├─ Campaign Logging
```

---

## 📡 Streaming Response

Most endpoints return NDJSON (newline-delimited JSON) streams:

```python
# Example client code
response = requests.post(url, json=data, stream=True)
for line in response.iter_lines():
    if line:
        event = json.loads(line)
        print(event)
```

Event types:
- `progress` - Processing status
- `plan_completed` - Planning finished
- `react_completed` - Evidence gathering done
- `report_ready` - Report generated
- `stage_b_completed` - Strategy generated
- `stage_c_completed` - Campaign executed
- `error` - Error occurred

---

## 🗄️ MongoDB Collections

- `reports` - Stage A reports
- `stage_b_strategies` - Stage B strategies and briefs
- `campaign_logs` - Stage C execution logs
- `conversations` - Chat conversations
- `messages` - Chat messages

---

## 🔧 Configuration Files

### .env (Example)
See `.env.example` for complete template

### requirements.txt
Main dependencies:
- flask
- pydantic
- pymongo
- requests
- tavily-python
- torch
- transformers
- rich

---

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Manual Testing with cURL
```bash
# Stage A
curl -X POST http://localhost:5000/api/research/stage_a \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "분석할 내용"}'

# Health Check
curl http://localhost:5000/health
```

---

## 📝 Logging

Backend logs to console with rich formatting. Log levels:
- `DEBUG` - Detailed debugging info
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error information

Control via `LOG_LEVEL` in `.env`

---

## 🆘 Troubleshooting

### "Failed to initialize LLM"
- Check `LLM_API_KEY` in `.env`
- Verify LLM provider is available

### "MongoDB connection failed"
- Check `MONGO_URI` format
- Ensure MongoDB server is running
- Verify network connectivity

### "Image generation failed"
- Check `IMAGE_API_URL` is accessible
- Verify image API is running
- Check API health at `{IMAGE_API_URL}/health`

### "Discord posting failed"
- Check `DISCORD_WEBHOOK_URL` is valid
- Verify webhook permissions
- Test with manual Discord message

### "Out of memory" errors
- Reduce evidence batch size
- Use smaller LLM model
- Increase available GPU/RAM

---

## 🚀 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 stage_a.flask_api:app
```

### Using Docker
```bash
docker build -t marketmind-backend .
docker run -p 5000:5000 --env-file .env marketmind-backend
```

### Production Settings
- Set `DEBUG=False`
- Set `LOG_LEVEL=INFO`
- Use proper MONGO_URI (managed MongoDB)
- Use environment variable secrets (not .env files)
- Enable HTTPS if behind proxy

---

## 📚 Additional Resources

- [Python Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Tavily Search API](https://tavily.com/docs)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)

---

## 🔗 Related Files

- Main app file: `stage_a/flask_api.py`
- CLI entry: `stage_a/main.py`
- Environment template: `.env.example`
- Dependencies: `requirements.txt`

---

**Last Updated**: May 2026
