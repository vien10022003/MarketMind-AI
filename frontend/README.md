# Frontend - MarketMind AI

Modern React TypeScript web interface for market research and marketing campaign management.

---

## 📋 Overview

The frontend provides an interactive UI for:
- **Market Research**: Chat-based research interface
- **Strategy Development**: Review and approve marketing strategies
- **Campaign Management**: Execute and schedule marketing campaigns
- **Conversation History**: Track and manage research conversations

**Technology**: React 19, TypeScript, Vite, Modern CSS

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat/              # Chat interface & message display
│   │   ├── Strategy/          # Strategy builder & viewer
│   │   ├── Campaign/          # Campaign execution & scheduling
│   │   ├── Forms/             # Input forms (marketing form, etc)
│   │   └── Common/            # Reusable components
│   │
│   ├── pages/
│   │   ├── ResearchPage.tsx   # Main research interface
│   │   ├── StrategyPage.tsx   # Strategy review/approval
│   │   ├── CampaignPage.tsx   # Campaign execution
│   │   └── ConversationsPage.tsx # Conversation history
│   │
│   ├── services/
│   │   ├── api.ts             # API client
│   │   ├── auth.ts            # Authentication service
│   │   └── storage.ts         # Local storage management
│   │
│   ├── types/
│   │   ├── messages.ts        # Message type definitions
│   │   ├── strategy.ts        # Strategy types
│   │   └── campaign.ts        # Campaign types
│   │
│   ├── hooks/
│   │   ├── useApi.ts          # API request hook
│   │   ├── useAuth.ts         # Authentication hook
│   │   └── useConversation.ts # Conversation management
│   │
│   ├── App.tsx                # Main app component
│   ├── App.css                # Global styles
│   └── main.tsx               # Entry point
│
├── public/                     # Static assets
├── index.html                 # HTML template
├── vite.config.ts             # Vite configuration
├── tsconfig.json              # TypeScript configuration
├── tsconfig.app.json          # App-specific TS config
├── tsconfig.node.json         # Node TS config
├── eslint.config.js           # ESLint rules
├── package.json               # Dependencies & scripts
└── README.md
```

---

## 🚀 Installation

### 1. Prerequisites
```bash
node --version     # Node.js 18+
npm --version      # npm 9+
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment

Create `.env` file in frontend root:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:5000

# Authentication
VITE_GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com

# Optional
VITE_LOG_LEVEL=info
```

---

## 🏃 Running the Frontend

### Development Server
```bash
npm run dev
```

**Server runs on**: `http://localhost:5173`

### Production Build
```bash
npm run build
```

Output in `dist/` directory

### Preview Production Build
```bash
npm run preview
```

---

## 📦 Available Scripts

```bash
npm run dev        # Start development server (Vite)
npm run build      # Build for production
npm run lint       # Run ESLint
npm run preview    # Preview production build locally
```

---

## 🏗️ Component Architecture

### Layout Structure
```
App
├── Header (Navigation, Auth)
├── Sidebar (Conversation List)
├── MainContent
│   ├── ResearchPage
│   │   ├── ChatArea (Messages)
│   │   └── InputArea (User input)
│   ├── StrategyPage
│   │   ├── StrategyViewer
│   │   └── ApprovalPanel
│   └── CampaignPage
│       ├── CampaignPreview
│       └── ExecutionPanel
└── Footer
```

### Key Components

#### Chat Interface
- **ChatContainer**: Manages chat messages and streaming
- **MessageList**: Displays messages with various types
- **InputBox**: User input with form handling
- **MessageRenderer**: Renders different message types (plan, report, strategy, etc)

#### Strategy Components
- **StrategyViewer**: Displays SWOT, USP, Persona
- **BriefEditor**: Edit and approve content briefs
- **ApprovalPanel**: Review and submit strategy

#### Campaign Components
- **CampaignPreview**: Show briefs to be posted
- **ScheduleManager**: Set posting times
- **ExecutionPanel**: Execute immediate or scheduled posting
- **ResultsDisplay**: Show campaign results

---

## 🔌 API Integration

### API Client (`services/api.ts`)

```typescript
import { api } from './services/api'

// Stage A Research
const response = await api.research.stageA({
  user_prompt: "Your question",
  llm_provider: "llama"
})

// Stage B Strategy
const strategy = await api.strategy.stageB(stageAReport)

// Stage C Campaign
const campaign = await api.campaign.stageC(approvedBriefs)

// Conversations
const conversations = await api.conversations.list()
const messages = await api.conversations.getMessages(conversationId)
```

---

## 🔐 Authentication

### Google OAuth Integration

```typescript
import { GoogleLogin } from '@react-oauth/google'

<GoogleLogin
  onSuccess={(credentialResponse) => {
    // Handle login
    const token = credentialResponse.credential
    // Send to backend for validation
  }}
  onError={() => console.log('Login Failed')}
/>
```

### Token Storage
- JWT stored in localStorage
- Automatically included in API headers
- Auto-refresh on expiration

---

## 📊 State Management

### Using React Hooks

```typescript
// Chat state
const [messages, setMessages] = useState<ChatMessage[]>([])
const [isLoading, setIsLoading] = useState(false)

// Streaming API responses
const { data, loading, error } = useApi(endpoint, {
  stream: true,
  onData: (event) => {
    // Handle streamed event
  }
})
```

### Local Storage
```typescript
// Conversation persistence
localStorage.setItem('conversation_id', id)
localStorage.setItem('draft_message', text)
```

---

## 🎨 Styling

### CSS Architecture
- Global styles: `App.css`
- Component styles: Colocated with components
- CSS Variables: Theme colors and spacing

### Colors & Theme
```css
:root {
  --color-primary: #5865F2;    /* Discord Blue */
  --color-secondary: #72767D;
  --color-success: #57F287;
  --color-danger: #ED4245;
  --color-warning: #FFA500;
  --color-bg: #36393F;
  --color-text: #FFFFFF;
}
```

---

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints:
  - Mobile: < 640px
  - Tablet: 640px - 1024px
  - Desktop: > 1024px

---

## 🧪 Testing

### Linting
```bash
npm run lint
```

Checks:
- TypeScript type safety
- ESLint rules
- Code formatting

### Manual Testing Checklist
- [ ] Chat messaging works
- [ ] Streaming responses display
- [ ] Form submissions work
- [ ] Strategy approval flows
- [ ] Campaign execution flows
- [ ] Mobile responsive

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Deploy to Static Host (GitHub Pages, etc)
```bash
npm run build
# Upload dist/ folder to your hosting
```

---

## 🔧 Configuration

### Vite Config (`vite.config.ts`)
- React Fast Refresh enabled
- JSX support
- TypeScript support
- CSS preprocessing

### TypeScript Config (`tsconfig.json`)
- ES2020 target
- Strict mode enabled
- React 19 support
- Path aliases for imports

### ESLint Config (`eslint.config.js`)
- React/Hooks rules
- TypeScript strict checking
- React Fast Refresh compliance

---

## 📝 Type Definitions

### Chat Messages
```typescript
interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'plan' | 'report' | 'strategy' | 'campaign_results'
  content: string
  timestamp: Date
  
  // Optional payloads
  planData?: PlanData
  reportData?: ReportData
  strategyData?: StrategyData
  campaignLogData?: CampaignLogData
  // ... more
}
```

### Strategy Types
```typescript
interface Strategy {
  title: string
  swot: SWOT
  usp: USP
  persona: Persona
  content_briefs: ContentBrief[]
}
```

### Campaign Types
```typescript
interface CampaignLog {
  campaign_id: string
  results: ExecutionResult[]
  total_briefs: number
  total_posted: number
  execution_mode: 'immediate' | 'scheduled'
}
```

---

## 🆘 Troubleshooting

### "Cannot connect to API"
- Check `VITE_API_BASE_URL` in `.env`
- Verify backend is running on port 5000
- Check CORS headers in backend

### "Google OAuth not working"
- Verify `VITE_GOOGLE_CLIENT_ID` is correct
- Check OAuth redirect URIs in Google Console
- Ensure frontend is on allowed origin

### "Messages not streaming"
- Check API response is NDJSON
- Verify streaming implementation
- Check browser console for errors

### "Build fails with TypeScript errors"
```bash
npm run lint  # Check all errors first
tsc --noEmit  # Run type checker
```

---

## 📚 Technologies & Libraries

| Library | Purpose |
|---------|---------|
| React 19 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool & dev server |
| @react-oauth/google | Google authentication |
| jwt-decode | JWT parsing |
| ESLint | Code linting |

---

## 🔗 Related Files

- API client: `src/services/api.ts`
- Type definitions: `src/types/`
- Main app: `src/App.tsx`
- Config: `vite.config.ts`, `tsconfig.json`
- Dependencies: `package.json`

---

## 🌐 Environment Variables

```env
# Required
VITE_API_BASE_URL=http://localhost:5000
VITE_GOOGLE_CLIENT_ID=your_client_id

# Optional
VITE_LOG_LEVEL=info
VITE_DEBUG=false
```

---

## 📖 Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev)
- [Vite + React](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts)

---

**Last Updated**: May 2026
