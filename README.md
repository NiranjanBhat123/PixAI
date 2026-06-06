# ✦ PixAI — AI-Powered Photo Editing Assistant

A conversational assistant that helps you caption, edit, and artistically transform your photos.
Upload a photo, pick what you want — captions, edits, or artistic styles — and get results in a dark editorial chat interface.

---

## What it does

| | |
|---|---|
| **Caption suggestions** | Gemini reads your image and writes 4 captions across different tones |
| **Edit suggestions + apply** | AI suggests brightness/contrast/etc. values, Pillow applies them |
| **Artistic style filters** | Pencil sketch, vintage, oil painting, emboss — all via Pillow |

---

## Architecture

```
React (localhost:3000)
    │  HTTP / REST
    ▼
Spring Boot WebFlux (localhost:8081) ── MongoDB
    │  MCP over SSE
    ▼
Python MCP Server (localhost:8000)
    ├── GeminiService ── Gemini API  (captions, edit analysis, style suggestions)
    ├── ImageEditService ── Pillow   (apply brightness/contrast/warmth/etc.)
    └── StyleFilterService ── Pillow (pencil sketch, vintage, oil painting, emboss)
```

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + TypeScript + Vite + shadcn/ui |
| Backend | Kotlin + Spring Boot 3 + WebFlux (reactive) |
| Database | MongoDB |
| AI protocol | Model Context Protocol (MCP over SSE) |
| MCP server | Python + FastMCP + uvicorn |
| AI model | Google Gemini (gemini-3.5-flash) |
| Image processing | Pillow |

---

## Local setup

### Prerequisites

- Java 21 · Node 22 (LTS) · Python 3.11+ · MongoDB 7+
- A Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### 1 — Environment

```bash
echo "GEMINI_API_KEY=your_key_here" > mcp-server/.env
```

### 2 — Start MongoDB

```bash
brew services start mongodb-community   # macOS
```

### 3 — Start MCP server

```bash
cd mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### 4 — Start backend

```bash
cd backend/pixai-api
./gradlew bootRun
```

Wait for: `Netty started on port 8081`

API docs → http://localhost:8081/swagger-ui.html

### 5 — Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open → http://localhost:3000

---

> **Startup order matters:** MongoDB → MCP server → Backend → Frontend.
> The backend connects to the MCP server eagerly at boot — if it's not running, Spring fails to start.