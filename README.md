# MarketMind AI

AI-powered platform for comprehensive market research and marketing campaign execution. Combines intelligent research (Stage A), strategy generation (Stage B), and automated campaign deployment (Stage C).

**Language**: Vietnamese • **Type**: Full-stack AI System • **Status**: Development

---

## 📋 Project Overview

MarketMind AI is a three-stage marketing intelligence and execution platform:

### Stage A: Market Research 🔍
- **User Input**: Customer receives detailed marketing research questions
- **Processing**: AI analyzes market, competitors, trends, and customer insights
- **Output**: Comprehensive market research report with actionable insights

### Stage B: Strategy Generation 🎯
- **Input**: Stage A research findings
- **Processing**: AI generates marketing strategy including SWOT, USP, target persona, and content pillars
- **Output**: Marketing strategy with approved content briefs for Stage C

### Stage C: Campaign Execution 🚀
- **Input**: Approved content briefs from Stage B
- **Processing**: AI generates images, formats Discord embeds, posts to Discord channels
- **Output**: Executed campaign with detailed logs and analytics

---

## 🏗️ Architecture

```
MarketMind AI
├── Backend (Python Flask)
│   ├── Stage A: Market Research Pipeline
│   ├── Stage B: Strategy Generation
│   ├── Stage C: Campaign Execution
│   └── Integration: MongoDB, LLM, Discord, Tavily Search
│
├── Frontend (React + TypeScript)
│   ├── Chat Interface
│   ├── Strategy Builder
│   └── Campaign Manager
│
└── Mobile App (Android)
    ├── Native Chat UI
    ├── Campaign Results Display
    └── Schedule Manager
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Android Studio (for mobile app)
- MongoDB instance
- Discord Webhook URL
- LLM API access (Llama, Gemini, etc.)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB URI

# Run Flask API
python stage_a/main.py --serve
```

**API runs on**: `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**Dev server**: `http://localhost:5173`

### Android App Setup

```bash
cd android
./gradlew build
# Open in Android Studio and run on emulator or device
```

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.10+, Flask, Pydantic, MongoDB |
| **LLM** | Llama, Gemini, or other LLM providers |
| **Frontend** | React 19, TypeScript, Vite |
| **Mobile** | Android Native (Java/Kotlin), Firebase |
| **External APIs** | Tavily (Search), Discord (Webhook), Image Generation |
| **Database** | MongoDB |

---

## 📚 Documentation

- **[Backend README](./backend/README.md)** - Backend setup, API endpoints, environment variables
- **[Frontend README](./frontend/README.md)** - Frontend setup, components, development guide
- **[Android App README](./android/README.md)** - App setup, build instructions, features

---

## 🔌 API Endpoints

### Research (Stage A)
- `POST /api/research/stage_a` - Main research endpoint
- `POST /api/research/stage_a/marketing` - Marketing form submission

### Strategy (Stage B)
- `POST /api/strategy/stage_b` - Generate strategy
- `POST /api/strategy/stage_b/approve` - Approve/save strategy

### Campaign (Stage C)
- `POST /api/campaign/stage_c` - Execute campaign (immediate)
- `POST /api/campaign/stage_c/scheduled` - Schedule campaign (future posting)

### Conversations
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/<id>` - Get conversation details
- `POST /api/conversations/<id>/messages` - Save messages

---

## 🔐 Authentication

The system uses JWT-based authentication. Include token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 🛠️ Configuration

### Environment Variables (Backend)

```env
# LLM Configuration
LLM_PROVIDER=llama  # or gemini, gpt
LLM_MODEL=llama-2
LLM_API_KEY=your_key

# MongoDB
MONGO_URI=mongodb://user:pass@host:port/dbname

# APIs
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TAVILY_API_KEY=your_key
IMAGE_API_URL=http://image-service:8000

# Server
PORT=5000
DEBUG=false
```

---

## 📊 Data Flow

```
User Input
    ↓
[Stage A] Market Research
├─ Intent Classification
├─ Planning (ReAct)
├─ Evidence Gathering (Tavily)
├─ Synthesis → Report
    ↓
[Stage B] Strategy Generation
├─ SWOT Analysis
├─ USP Definition
├─ Persona Development
├─ Content Brief Generation
    ↓
[Stage C] Campaign Execution
├─ Image Generation
├─ Discord Formatting
├─ Scheduled/Immediate Posting
├─ Campaign Logging
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

---

## 📱 Features

✅ **Market Research**
- Multi-step research pipeline
- Evidence gathering and synthesis
- Competitive analysis
- Market trend analysis

✅ **Strategy Generation**
- SWOT analysis
- Target persona definition
- Content pillar creation
- Brief templates for content creators

✅ **Campaign Execution**
- AI image generation
- Discord webhook integration
- Scheduled posting
- Campaign analytics

✅ **Conversation Management**
- Message history
- Multi-turn conversations
- Data persistence

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📝 License

This project is part of a thesis work. See LICENSE for details.

---

## 👥 Team

- **Advisor**: [Your Advisor Name]
- **Developer**: [Your Name]

---

## 📞 Support & Issues

For bugs and feature requests, please open an issue on the project repository.

---

## 🔄 Version History

- **v1.0** - Initial release with 3-stage pipeline
  - Stage A: Market Research
  - Stage B: Strategy Generation  
  - Stage C: Campaign Execution

---

**Last Updated**: May 2026
