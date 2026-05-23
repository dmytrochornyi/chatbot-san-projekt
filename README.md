# SAN AI — Akademicki Asystent Chatbot

An AI-powered academic assistant for Społeczna Akademia Nauk (SAN) built with RAG (Retrieval-Augmented Generation). Students can ask questions about university regulations, syllabi, and other documents and get answers grounded in the actual source material.

## Architecture

```
Student types a question
        ↓
Next.js frontend  (assistant-ui)
        ↓
Next.js /api/chat route
        ↓
FastAPI /api/retrieve ──→ pgvector (finds relevant doc chunks)
        ↓
Ollama  (generates answer, streams back token by token)
        ↓
Answer appears word by word in the chat
```

| Service | Role |
|---------|------|
| **Next.js + assistant-ui** | Chat UI and request orchestration |
| **FastAPI** | RAG retrieval — embeds the question, searches pgvector, returns chunks |
| **PostgreSQL + pgvector** | Vector store for embedded document chunks |
| **Ollama** | Runs LLMs locally — `llama3.2` for generation, `nomic-embed-text` for embeddings |

## Project Structure

```
chatbot-san-projekt/
├── frontend/                  # Next.js 16 + assistant-ui
│   ├── app/
│   │   ├── page.tsx
│   │   ├── assistant.tsx      # Chat layout with sidebar
│   │   └── api/chat/route.ts  # Retrieval + Ollama streaming
│   └── components/assistant-ui/
├── backend/                   # FastAPI (UV)
│   ├── main.py
│   ├── routers/
│   │   ├── chat.py            # POST /api/chat
│   │   └── retrieve.py        # POST /api/retrieve
│   ├── rag/
│   │   ├── chain.py           # LangChain RAG chain
│   │   └── retriever.py       # pgvector retriever
│   ├── models/schemas.py
│   └── scripts/ingest.py      # One-time PDF ingestion
├── data/
│   └── raw/                   # University PDFs go here
├── docker-compose.yml
└── .env.example
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- Git

### 1. Clone and configure

```bash
git clone https://github.com/dawidoootak-jpg/chatbot-san-projekt.git
cd chatbot-san-projekt
cp .env.example .env
```

### 2. Start all services

```bash
docker-compose up --build
```

### 3. Pull AI models (first time only)

In a second terminal:

```bash
docker exec -it chatbot-san-projekt-ollama-1 ollama pull llama3.2
docker exec -it chatbot-san-projekt-ollama-1 ollama pull nomic-embed-text
```

### 4. Ingest university documents (first time only)

```bash
docker exec -it chatbot-san-projekt-backend-1 uv run python scripts/ingest.py
```

This loads all PDFs from `data/raw/`, splits them into chunks, embeds them, and stores them in pgvector.

### 5. Open the app

Go to **http://localhost:3000**

---

### Every time after that

```bash
git pull
docker-compose up
```

Model weights and the database persist in Docker volumes — no need to repeat steps 3 and 4.

## Adding New Documents

Drop PDF files into `data/raw/` and re-run the ingestion script:

```bash
docker exec -it chatbot-san-projekt-backend-1 uv run python scripts/ingest.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_DB` | `san_chatbot` | Database name |
| `DATABASE_URL` | `postgresql+psycopg://...` | Full connection string |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `llama3.2` | LLM model for generation |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model for embeddings |

## Tech Stack

- **Frontend:** Next.js 16, assistant-ui, Tailwind CSS, TypeScript
- **Backend:** Python, FastAPI, LangChain, UV
- **Vector DB:** PostgreSQL + pgvector
- **LLM:** Ollama (Llama 3.2)
- **Infrastructure:** Docker Compose
