# Learning Hub — FDE Portfolio Case Study

**Author:** Kunal Singh  
**Role:** QA Engineer → Forward Deployment Engineer  
**Timeline:** Built in a single session  
**GitHub:** github.com/kunal420-xnor/learning-hub

---

## Overview

Learning Hub is a production-grade AI learning platform built from scratch — two AI-powered applications running on a shared Flask backend with a React frontend, secured with JWT authentication, instrumented with LangSmith observability, and extended with a RAG pipeline for document-grounded responses.

The project was built as a deliberate transition artifact: demonstrating that QA engineering depth — systematic thinking, validation logic, edge case coverage, and production mindset — transfers directly into Forward Deployment Engineering.

---

## The Problem

Most AI learning tools are black boxes. They give you a response and you have no idea whether it was accurate, appropriately formatted, or improving over time. For enterprise deployments, this is unacceptable.

The goal was to build something that mirrors what FDEs actually do for clients:

- Integrate an LLM into a real product
- Validate and control its output format
- Instrument it for observability
- Secure it for multi-user access
- Extend it with domain-specific knowledge via RAG

---

## Architecture

```
Browser (React + Tailwind + Vite)
         │
         │ JWT-authenticated HTTP requests
         ▼
Kong API Gateway (rate limiting, routing)
         │
         ▼
Flask API (Python)
    ├── /login          → JWT token issuance
    ├── /explain        → ELI3 LLM pipeline
    ├── /spanish/chat   → Spanish tutor + RAG
    ├── /rag/upload     → PDF ingestion endpoint
    ├── /rag/status     → ChromaDB chunk count
    ├── /feedback       → LangSmith feedback
    └── /create_dataset → LangSmith dataset builder
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Ollama     ChromaDB
(gemma3:4b) (vector store)
    │
    ▼
LangSmith (tracing + evaluation)
    │
    ▼
SQLite → PostgreSQL (migration in progress)
```

---

## Application 1 — Explain Like I'm 3 (ELI3)

### What it does
Takes any complex topic and explains it in simple terms — as if the user is 3 years old — using a MIT/Harvard professor persona with strict output constraints.

### Key engineering decisions

**Prompt engineering with validation**
The system prompt enforces: maximum 3 sentences, analogies using toys/food/animals, no jargon, a different analogy on every retry if the user says they don't understand. This mirrors production LLM validation work done at Treiva AI.

**Response length validation with auto-retry**
After 3 conversations, every response is validated against a 400 character limit. If exceeded, the system automatically sends a retry prompt and truncates — ensuring consistent UX without manual intervention.

```python
if count > 3 and len(reply) > 400:
    history.append({"role": "user", "content": "Too long! Under 400 characters."})
    retry, _ = get_eli3_response(history)
    reply = retry["message"]["content"].strip()[:400]
```

**Session memory per user**
Each user gets an isolated conversation history keyed by JWT identity + session UUID. The model remembers context across messages without cross-contaminating other users' sessions.

**LangSmith tracing**
Every LLM call is traced using `@traceable` decorator, capturing inputs, outputs, latency, and run IDs for downstream feedback collection.

---

## Application 2 — Spanish Tutor

### What it does
A conversational Spanish tutor that teaches from scratch, corrects mistakes in real time, speaks responses aloud using the Web Speech API, accepts voice input, and can learn from uploaded PDF documents via RAG.

### Key engineering decisions

**Structured output enforcement**
The Spanish tutor enforces a strict three-section response format:

```
SPANISH: <sentence>
ENGLISH: <translation>
TIP: <grammar note or correction>
```

Every response is automatically validated against this format using regex. Non-compliant responses are flagged in LangSmith with a `format_check` score of 0.0, creating a continuous quality signal.

```python
def validate_spanish_format(reply):
    has_spanish = bool(re.search(r'SPANISH:\s*.+', reply, re.IGNORECASE))
    has_english = bool(re.search(r'ENGLISH:\s*.+', reply, re.IGNORECASE))
    has_tip = bool(re.search(r'TIP:\s*.+', reply, re.IGNORECASE))
    return has_spanish and has_english and has_tip
```

**Voice I/O with language detection**
- Speech input uses the Web Speech API in `es-ES` mode — recognizes Spanish pronunciation
- Text-to-speech extracts only the `SPANISH:` section before speaking — never reads English translations aloud
- Voice selection prioritizes Mónica (Apple neural es-ES) for natural accent

**RAG Pipeline**
Users can upload any PDF — a Spanish textbook, vocabulary list, or company policy document. The system:
1. Extracts text page by page using pypdf
2. Chunks into 200-word segments
3. Embeds using `sentence-transformers/all-MiniLM-L6-v2`
4. Stores in ChromaDB with persistent storage
5. On every user message, retrieves top-2 relevant chunks and injects into the system prompt

This turns the Spanish tutor into a domain-specific training tool — upload a company's Spanish onboarding materials and the AI teaches using company-specific vocabulary.

---

## Security Layer — JWT Authentication

Every API endpoint is protected with JWT tokens issued on login. Token expiry is set to 8 hours, matching enterprise session standards.

```python
@app.route('/explain', methods=['POST'])
@jwt_required()
def explain():
    current_user = get_jwt_identity()
    session_id = f"{current_user}_{uuid}"
```

- Multi-user support with isolated session histories
- Tokens stored in localStorage with client-side expiry validation
- Role-based user store (extensible to database-backed auth)

---

## Observability — LangSmith Integration

Every LLM call is traced end-to-end:

| Signal | What it captures |
|--------|-----------------|
| Traces | Full input/output for every LLM call |
| Latency | Response time per request |
| format_check | Automated score for Spanish format compliance |
| user_feedback | 👍👎 scores from in-app feedback buttons |
| Dataset | Good/bad examples collected for future evals |

This creates a feedback loop: user rates a response → score sent to LangSmith → example added to eval dataset → dataset used to test prompt improvements.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Vite |
| Backend | Python, Flask, flask-jwt-extended, flask-cors |
| LLM | Ollama (gemma3:4b) — runs locally, zero API cost |
| Vector DB | ChromaDB with sentence-transformers embeddings |
| Observability | LangSmith — tracing, feedback, datasets |
| Database | SQLite (PostgreSQL migration in progress) |
| Auth | JWT with 8-hour token expiry |
| Voice | Web Speech API — recognition (es-ES) + synthesis (Mónica) |
| DevOps | Git, GitHub, multi-device deployment |

---

## Problems Solved

**Problem 1 — All major LLM APIs blocked in India**
Anthropic, OpenAI, and Google Gemini all hit quota or billing walls. Solved by running Ollama locally — free, private, and production-equivalent for portfolio purposes.

**Problem 2 — AI mixing Spanish and English in speech**
The TTS was reading everything including English translations. Solved by extracting only the `SPANISH:` section using regex before passing to SpeechSynthesisUtterance — English translations remain visible but are never spoken.

**Problem 3 — API keys exposed in Git history**
During initial push, API keys were detected in commit history by GitHub's secret scanning. Solved using `git filter-branch` to rewrite history and remove the files, followed by key rotation.

**Problem 4 — React proxy not forwarding to Flask**
404 errors on all API calls after migrating from HTML templates to React. Solved by configuring Vite's proxy to forward all API routes to Flask port 5000.

---

## What This Demonstrates for FDE Roles

| FDE Skill | Where it shows in this project |
|-----------|-------------------------------|
| LLM integration | Ollama + Flask API from scratch |
| Prompt engineering | Structured output, persona, retry logic |
| Output validation | Format checking, length enforcement, auto-retry |
| RAG pipeline | PDF ingestion → chunking → embedding → retrieval |
| Observability | LangSmith tracing, automated scoring, feedback loops |
| Security | JWT auth, session isolation, key management |
| Debugging | 5 different API billing walls, Git history rewrite, proxy config |
| Full stack | React + Flask + Python — end to end |
| Multi-device deployment | GitHub → clone → run on second Mac in under 10 minutes |

---

## What's Next

- **PostgreSQL** — replace SQLite with production-grade database
- **Prometheus + Grafana** — API latency and token usage dashboards
- **Redis Streams** — real-time event pipeline (Kafka equivalent)
- **Kong API Gateway** — rate limiting and gateway-level JWT validation
- **Docker** — containerize the full stack for one-command deployment

---

## Key Learnings

Building this project surfaced the exact skills FDE roles require: the ability to integrate an LLM into a product quickly, instrument it for quality monitoring, secure it for real users, and extend it with domain knowledge — all while debugging real production-level problems under constraints.

The Treiva AI experience — being the sole QA on a live AI agent product — provided the mental model. This project built the technical vocabulary to talk about it in engineering terms.

---

*Built by Kunal Singh as part of a QA → FDE transition. All infrastructure runs locally at zero cost using open-source tooling.*
