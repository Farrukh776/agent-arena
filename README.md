# 🎭 AgentArena — AI Decision Stress-Testing

> **Stress-test any idea, decision, or claim before you commit to it.**
> Three specialized AI agents debate your topic across multiple rounds — with real web search, live argument scoring, dynamic fact-checking, and a judge's final verdict.

🔗 **Live Demo:** [agentarena-ai.netlify.app](https://agentarena-ai.netlify.app)

---

## What Is AgentArena?

Most people make decisions by thinking through one or two perspectives. AgentArena forces every angle to be argued — simultaneously, with evidence — so you can see the full picture before deciding.

You enter a topic. Three AI agents with opposing personalities debate it across multiple rounds, each genuinely responding to the others' arguments. A Judge agent then reads the full transcript and delivers a structured verdict.

---

## Demo

| | |
|---|---|
| **Topic input** | Enter any decision, claim, or question |
| **Live streaming** | Watch each agent argue in real time, word by word |
| **Round structure** | Agents build on previous arguments each round |
| **Scoring** | Every argument scored on Logic, Evidence, Coherence |
| **Fact checking** | Claims with statistics trigger automatic web verification |
| **Judge verdict** | Structured final decision with winner and reasoning |
| **Memory** | Agents reference past debates on similar topics |

---

## Real-World Use Cases

**🚀 Startup Founders**
> "Should we pivot from B2C to B2B?" — Get a full stress-test of both sides before your next board meeting.

**📈 Investors & Analysts**
> "Are AI stocks overvalued in 2025?" — Three perspectives backed by live web search.

**🎓 Students & Researchers**
> "Does universal basic income reduce poverty?" — Instant multi-perspective analysis for essays and research.

**⚙️ Product & Engineering Teams**
> "Should we rewrite the app in a new framework?" — Hear the strongest case for and against before committing.

---

## How It Works

```
User enters topic
        ↓
┌─────────────────────────────────────────────────┐
│                  Debate Engine                   │
│                                                  │
│  Round 1                                         │
│  ├── 🟢 Optimist    → argues positive angle      │
│  ├── 🔴 Skeptic     → challenges with evidence   │
│  └── 🟣 Devil's Advocate → takes contrarian view │
│                                                  │
│  Round 2 (agents respond to each other)          │
│  ├── 🟢 Optimist    → counters Skeptic directly  │
│  ├── 🔴 Skeptic     → picks apart new claims     │
│  └── 🟣 Devil's Advocate → flips the consensus   │
│                                                  │
│  [Fact-Checker spawns on any factual claim] 🔍   │
└─────────────────────────────────────────────────┘
        ↓
⚖️ Judge Agent reads full transcript + scores
        ↓
Structured verdict: Winner · Key Insight · Final Analysis
        ↓
💾 Saved to SQLite — referenced in future debates
```

---

## Agent Personalities

| Agent | Role | Strategy |
|---|---|---|
| 🟢 **Optimist** | Positive angle | Opportunities, benefits, best-case outcomes |
| 🔴 **Skeptic** | Critical analysis | Risks, missing evidence, historical failures |
| 🟣 **Devil's Advocate** | Contrarian | Flips assumptions, introduces uncomfortable truths |
| 🔍 **Fact-Checker** | Dynamic spawner | Verifies claims with live web search via Tavily |
| ⚖️ **Judge** | Final verdict | Scores arguments, picks winner, delivers analysis |

---

## Scoring System

Each argument is evaluated on three dimensions:

| Dimension | What it measures |
|---|---|
| **Logic** /10 | Soundness of reasoning, absence of fallacies |
| **Evidence** /10 | Use of data, examples, citations |
| **Coherence** /10 | Clarity, structure, staying on topic |
| **Total** /30 | Combined score used for leaderboard |

Logical fallacies are detected and flagged per argument.

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11 | Core language |
| FastAPI | REST API + WebSocket server |
| Groq API | LLM inference (LLaMA 3.3 70B Versatile) |
| Tavily API | Real-time web search for agents |
| SQLite | Persistent debate memory + agent stats |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI framework |
| Tailwind CSS | Styling |
| Vite | Build tool |
| WebSocket API | Real-time token streaming |

### Deployment
| Service | Purpose |
|---|---|
| Render | Backend hosting (free tier) |
| Netlify | Frontend hosting (free tier) |

---

## Architecture

```
AgentArena/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py         # Base Agent class — blocking + streaming modes
│   │   ├── debate_agents.py      # Optimist, Skeptic, Devil's Advocate factories
│   │   ├── judge_agent.py        # Verdict agent — reads full transcript + scores
│   │   └── fact_checker.py       # Dynamic spawner — web search + claim verification
│   ├── memory/
│   │   └── debate_memory.py      # SQLite layer — save/retrieve debates + stats
│   ├── utils/
│   │   ├── scorer.py             # LLM-based argument scoring engine
│   │   └── web_search.py         # Tavily search wrapper
│   ├── main.py                   # FastAPI app — WebSocket endpoint + disconnect detection
│   └── debate_manager.py         # Orchestrator — runs debate, checks cancellation flag
└── frontend/
    └── src/
        ├── components/
        │   ├── AgentCard.jsx      # Per-agent streaming card with scores
        │   ├── ScorePanel.jsx     # Live leaderboard + all-time stats
        │   ├── VerdictPanel.jsx   # Judge verdict display
        │   ├── StatusBar.jsx      # Live status with round progress
        │   └── TopicForm.jsx      # Topic input with example prefills
        ├── hooks/
        │   └── useDebateSocket.js # WebSocket state management + stop logic
        └── App.jsx                # Main layout — round-grouped debate view
```

---

## Local Development

### Prerequisites
- Python 3.11
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)
- [Tavily API key](https://tavily.com) (free tier)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Start the server:
```bash
uvicorn main:app --reload --port 8000
```

API runs at `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173`

> Make sure `frontend/src/hooks/useDebateSocket.js` has `WS_URL = "ws://localhost:8000/debate"` for local development.

---

## Key Engineering Decisions

**Why no LangChain or agent frameworks?**
Built from scratch using raw Groq API calls. Every agent is a Python class with a `respond()` and `respond_streaming()` method. This makes the system fully transparent and easy to debug.

**How do agents "respond to each other"?**
Each agent receives the full debate context — all previous arguments from all agents — as its user message. The context grows every round, forcing agents to address what was actually said rather than repeating opening arguments.

**How does the stop button prevent database saves?**
A shared `asyncio.Event` (`cancelled`) is set the moment the WebSocket closes. The debate manager checks `is_cancelled()` before every token, every agent, and critically before `save_debate()`. Stopping at any point means nothing is persisted.

**Why SQLite over a cloud database?**
For a portfolio project running on free tier infrastructure, SQLite is the right call — zero configuration, zero cost, and the debate history is local to the server instance.

---

## Built By

**Farrukh** — CS Student  
Built as a portfolio project demonstrating multi-agent AI systems, real-time streaming, and full-stack deployment.

---

## License

MIT — free to use, fork, and build on.
