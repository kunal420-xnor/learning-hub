# Learning Hub

> A production-grade AI learning platform — two apps, one backend, built from scratch.



---

## What is this?

Learning Hub is a full-stack AI platform with two tools:

**🧸 Explain Like I'm 3 (ELI3)** — Ask any complex topic. Get a simple explanation from a MIT/Harvard professor persona. Responses are validated for length and simplicity. After 3 messages, the system enforces a 400-character limit with automatic retry.

**🇪🇸 Spanish Tutor** — A conversational Spanish tutor that teaches from scratch, corrects mistakes in real time, speaks Spanish responses aloud, accepts voice input, and learns from uploaded PDF documents via RAG.

---

## Features

### AI & LLM
- Local LLM via Ollama (gemma3:4b) — zero API cost, runs on your machine
- Structured output enforcement — every Spanish response validated for SPANISH/ENGLISH/TIP format
- Response length validation with automatic retry
- Session memory per user — conversation history isolated by JWT identity
- RAG pipeline — upload any PDF, AI learns from it instantly

### Security
- JWT authentication — login, token issuance, 8-hour expiry
- Per-user session isolation
- All LLM endpoints protected with `@jwt_required()`

### Observability
- LangSmith tracing on every LLM call — inputs, outputs, latency
- Automated format compliance scoring for Spanish tutor
- In-app 👍👎 feedback buttons — scores sent to LangSmith in real time
- Dataset builder — good/bad examples collected automatically for eval

### Voice
- Speech input via Web Speech API (es-ES) — click mic and speak
- Text-to-speech output — AI speaks only the Spanish section aloud
- Voice selection prioritizes Mónica (Apple neural es-ES) for natural accent

### Frontend
- React 18 + Tailwind CSS
- Login screen with JWT token management
- Real-time chat UI with typing indicators
- PDF upload with progress feedback
- Responsive design

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Vite |
| Backend | Python, Flask, flask-jwt-extended, flask-cors |
| LLM | Ollama (gemma3:4b) |
| Vector DB | ChromaDB + sentence-transformers |
| Observability | LangSmith |
| Database | SQLite (PostgreSQL migration in progress) |
| Auth | JWT — flask-jwt-extended |
| Voice | Web Speech API |

---

## Project Structure

```
learning-hub/
├── app.py                  # Flask API — all routes and LLM logic
├── database.py             # SQLite helpers
├── rag.py                  # RAG pipeline — PDF ingestion, embedding, retrieval
├── requirements.txt        # Python dependencies
├── README.md
├── CASE_STUDY.md           # Full FDE portfolio case study
├── .gitignore
├── documents/              # Uploaded PDFs (gitignored)
├── chroma_db/              # ChromaDB vector store (gitignored)
└── frontend/
    ├── src/
    │   ├── App.jsx          # Root — auth flow + routing
    │   └── pages/
    │       ├── Login.jsx    # JWT login screen
    │       ├── Home.jsx     # Landing page
    │       ├── ELI3.jsx     # ELI3 app
    │       └── Spanish.jsx  # Spanish tutor app
    ├── vite.config.js       # Proxy config — forwards API calls to Flask
    └── tailwind.config.js
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/login` | ❌ | Issue JWT token |
| POST | `/explain` | ✅ | ELI3 LLM call |
| POST | `/spanish/chat` | ✅ | Spanish tutor LLM call + RAG |
| POST | `/rag/upload` | ✅ | Upload PDF to ChromaDB |
| GET | `/rag/status` | ✅ | Check loaded chunks |
| POST | `/feedback` | ✅ | Send score to LangSmith |
| POST | `/create_dataset` | ✅ | Add example to LangSmith dataset |

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama — download from [ollama.com](https://ollama.com/download)

### 1. Clone the repo
```bash
git clone https://github.com/kunal420-xnor/learning-hub.git
cd learning-hub
```

### 2. Set up Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your LangSmith API key:
```
LANGSMITH_API_KEY=your-key-here
LANGSMITH_PROJECT=learning-hub
LANGCHAIN_TRACING_V2=true
```

Get a free LangSmith key at [smith.langchain.com](https://smith.langchain.com)

### 4. Pull the LLM model
```bash
ollama pull gemma3:4b
```

### 5. Set up React frontend
```bash
cd frontend
npm install
```

### 6. Run the app

You need three terminals:

**Terminal 1 — Ollama:**
```bash
ollama serve
```

**Terminal 2 — Flask:**
```bash
source venv/bin/activate
python3 app.py
```

**Terminal 3 — React:**
```bash
cd frontend
npm run dev
```

### 7. Open in browser
```
http://localhost:5173
```

Use **Chrome** for microphone support.

**Test accounts:**
```
kunal / password123
demo  / demo123
admin / admin123
```

---

## Using the RAG Pipeline

1. Go to the Spanish Tutor
2. Scroll to the bottom — you'll see a PDF upload box
3. Upload any PDF (Spanish textbook, vocabulary list, company document)
4. The AI will use it as context when answering
5. Responses that used document context show a "📄 Using document context" badge

---

## Roadmap

- [x] JWT Authentication
- [x] RAG Pipeline with ChromaDB
- [x] LangSmith Observability
- [x] User Feedback + Dataset Building
- [x] Voice Input/Output
- [ ] PostgreSQL (replace SQLite)
- [ ] Prometheus + Grafana dashboards
- [ ] Redis Streams data pipeline
- [ ] Kong API Gateway
- [ ] Docker — one-command deployment

---

## Why I built this

I'm transitioning from QA Engineering to Forward Deployment Engineering. This project was built to demonstrate that the skills transfer directly:

- **QA → Prompt validation** — I test AI outputs the same way I test software
- **Test frameworks → RAG pipelines** — structured, repeatable, measurable
- **Defect tracking → LangSmith** — observability over AI quality instead of bug counts
- **CI/CD → reproducible deployment** — clone, install, run on any machine

See [CASE_STUDY.md](./CASE_STUDY.md) for the full technical write-up.

---

## Author

**Kunal Singh** — QA Engineer transitioning to Forward Deployment Engineering  
[LinkedIn](https://www.linkedin.com/in/kunal-singh-a825ba15b/) · [GitHub](https://github.com/kunal420-xnor)
