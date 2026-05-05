[//]: # ([![Review Assignment Due Date]&#40;https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg&#41;]&#40;https://classroom.github.com/a/SHM9MYZJ&#41;)

[//]: # (# Valura AI — Team Lead Project Assignment)

[//]: # ()
[//]: # (You have been given access to this repository as part of the Valura AI team lead hiring process.)

[//]: # ()
[//]: # (**Read [`ASSIGNMENT.md`]&#40;ASSIGNMENT.md&#41; in full before writing a single line of code.**)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## What you're building)

[//]: # ()
[//]: # (An AI agent ecosystem that helps a novice investor **build, monitor, grow, and protect** their portfolio. See [`ASSIGNMENT.md`]&#40;ASSIGNMENT.md&#41; for the full mission, scope, and constraints.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Setup)

[//]: # ()
[//]: # (**Requirements:** Python 3.11+, an OpenAI API key.)

[//]: # ()
[//]: # (**Persistence is your choice.** Postgres, SQLite, or in-memory — pick one and defend it in your README. `DATABASE_URL` in `.env.example` is optional.)

[//]: # ()
[//]: # (**Streaming is required.** SSE only. Use `sse-starlette`, FastAPI's `StreamingResponse`, or roll your own — your call.)

[//]: # ()
[//]: # (```bash)

[//]: # (git clone <your-classroom-repo-url>)

[//]: # (cd <repo-name>)

[//]: # ()
[//]: # (python -m venv venv)

[//]: # (source venv/bin/activate        # Linux/macOS)

[//]: # (venv\Scripts\activate           # Windows)

[//]: # ()
[//]: # (pip install -r requirements.txt)

[//]: # ()
[//]: # (cp .env.example .env)

[//]: # (# Fill in OPENAI_API_KEY)

[//]: # (```)

[//]: # ()
[//]: # (Use `gpt-4o-mini` while developing to keep costs down. Evaluation runs against `gpt-4.1`.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Running Tests)

[//]: # ()
[//]: # (```bash)

[//]: # (pytest tests/ -v)

[//]: # (```)

[//]: # ()
[//]: # (Tests must pass without an `OPENAI_API_KEY` set — mock the LLM. We will run `pytest tests/ -v` on your repo.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Repository Structure)

[//]: # ()
[//]: # (When you submit, your repository must contain:)

[//]: # ()
[//]: # (```)

[//]: # (README.md   ← overwrite this with your own &#40;setup, decisions, library choices, video link&#41;)

[//]: # (src/        ← all code)

[//]: # (tests/      ← all tests, must pass with pytest)

[//]: # (```)

[//]: # ()
[//]: # (`fixtures/`, `pytest.ini`, `requirements.txt`, `.env.example`, and `.github/` are part of the scaffold — leave them in place. Do not delete `ASSIGNMENT.md`.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Submission)

[//]: # ()
[//]: # (- Push commits **throughout** your work — we read the git log)

[//]: # (- Your `README.md` must:)

[//]: # (  - Explain how to run your code)

[//]: # (  - List every required environment variable)

[//]: # (  - Document the non-obvious decisions you made)

[//]: # (  - Link your defence video &#40;≤ 10 min — see `ASSIGNMENT.md`&#41;)

[//]: # (- Deadline: **3 days** from the date you accepted this assignment)

[//]: # (- Defence video: due within **24 hours** of your final commit)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Environment)

[//]: # ()
[//]: # (You self-host everything. We do not provide credentials. See `.env.example` for the variables you'll need.)

# AI Financial Assistant Microservice

> A multi-agent AI system that processes financial queries using safety checks, intent classification, and real-time response streaming.
> 
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![SQLite](https://img.shields.io/badge/Memory-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## About This Project

This is a financial AI microservice that processes user queries through a modular pipeline and streams real-time insights.

It works as a structured system with safety checks, intent classification, and agent-based routing, while maintaining session-aware memory.

---
### What It Can Do

| Capability             | Description |
|------------------------|---|
| Portfolio Analysis     | Understand and evaluate your holdings |
| Market Research        | Analyze current market conditions |
| Risk Evaluation        | Quantify and explain portfolio risk |
| Recommendations        | Provide actionable investment insights |
| Financial Calculations | Run computations on portfolio data |

---

## Architecture Overview

```
                ┌──────────────────────┐
                │      User Query      │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │   FastAPI (/chat)    │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │    Safety Guard      │  ← Policy validation layer
                └─────────┬────────────┘
                          │
              ┌───────────┴───────────┐
           blocked ❌            allowed ✅
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   Session Memory     │  ← SQLite-backed context
                          └─────────┬────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │  Intent Classifier   │  ← LLM-based routing signal
                          └─────────┬────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │    Agent Router      │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │  Portfolio Health│   │  Market Research │   │  Risk Analysis   │
   │      Agent       │   │      Agent       │   │      Agent       │
   └──────────┬───────┘   └────────┬─────────┘   └───────┬──────────┘
              └────────────────────┼─────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   LLM / Logic Layer  │
                        └─────────┬────────────┘
                                  │
                                  ▼
                        ┌──────────────────────┐
                        │   SSE Streaming Layer│  ← Real-time delivery
                        └─────────┬────────────┘
                                  │
                                  ▼
                              ┌────────┐
                              │  User  │
                              └────────┘
```

### Execution Flow

```
Request → Safety Check → Memory Retrieval → Intent Classification
       → Agent Routing → Task Execution → LLM Response → SSE Stream
```

---

## Project Structure

```
src/
├── agents/                 # Modular domain-specific agents
│   ├── portfolio_agent.py  # Portfolio health & composition
│   ├── market_agent.py     # Market research & analysis
│   └── risk_agent.py       # Risk scoring & evaluation
│
├── main.py                 # FastAPI entry point
├── classifier.py           # LLM-based intent classification
├── router.py               # Intent → agent routing logic
├── safety_guard.py         # Safety validation & policy layer
├── memory.py               # Session memory (SQLite)
├── market_data.py          # External market data integration
├── schemas.py              # Pydantic request/response models
├── config.py               # App-wide configuration
├── db_debug.py             # Database inspection utility
│
└── valura_memory.db        # Persistent session storage
```

---

## Key Components

### 1. Safety Guard
Validates every incoming query against financial safety policies before it enters the pipeline. Blocks harmful, speculative, or out-of-scope requests.

### 2. Session Memory (SQLite)
Maintains conversation context across requests using a lightweight SQLite store. Enables coherent multi-turn interactions without a heavy vector DB.

### 3. Intent Classifier
Uses an LLM to classify user intent into one of the supported financial domains — portfolio, market, risk, or general. Routes the query accordingly.

### 4. Agent Router
Maps classified intents to the correct domain agent. Designed for extensibility — adding a new agent requires minimal changes.

### 5. Domain Agents
Each agent handles a specific financial concern and composes a structured prompt for the LLM layer, enriched with user context and session history.

### 6. SSE Streaming Layer
Streams intermediate status updates and the final response back to the client in real-time using Server-Sent Events.

---

## Streaming (SSE)

Responses are streamed step-by-step so users see progress immediately.

```
event: status
data: {"stage": "safety_check"}

event: status
data: {"stage": "classification", "intent": "risk_analysis"}

event: status
data: {"stage": "agent_execution"}

event: response
data: {"content": "Your portfolio has a high concentration in tech...", "intent": "risk_analysis"}

event: done
data: {}
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- An OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/2CentsCapital/valura-ai-ai-engineer-assignment-pratim4dasude.git
cd valura-ai-ai-engineer-assignment-pratim4dasude
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# .env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

### 4. Run the Server

```bash
# Option A: Module mode
python -m src.main

# Option B: Uvicorn with hot reload
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API Reference

### `POST /chat`

Send a financial query and receive a streamed response.

**Request Body**

```json
{
  "session_id": "user_123",
  "query": "Analyze my portfolio risk",
  "user_context": {
    "portfolio": [
      {"symbol": "AAPL", "value": 5000},
      {"symbol": "TSLA", "value": 3000}
    ]
  }
}
```

**Response** — Server-Sent Events stream

```
event: status
data: {"stage": "classification"}

event: response
data: {"content": "...", "intent": "risk_analysis", "session_id": "user_123"}

event: done
data: {}
```

---
 
## Database Debug Utility
 
A built-in CLI utility for inspecting and managing the SQLite session memory database directly , no external tools required.
 
```bash
python -m src.db_debug
```
 
| Operation              | Description |
|------------------------|---|
| View all sessions      | List every stored session and its metadata |
| Fetch by session ID    | Retrieve the full conversation context for a specific `session_id` |
| Delete a session     | Remove a single session and its associated memory |
| Clear entire database | Wipe all sessions — useful for a clean test slate |
 
> **Note:** This utility operates directly on `valura_memory.db`. Back up the file before running destructive operations in a shared environment.
 

---

## Testing

```bash
pytest
```

Tests cover safety guard logic, intent classification accuracy, agent routing, and SSE stream integrity.

---

## Design Principles

| Principle | Implementation |
|---|---|
| **Modular Architecture** | Agents are fully isolated — easy to add, swap, or test |
| **Safety First** | Every request passes through a policy guard before processing |
| **LLM + Rule Hybrid** | Combines LLM reasoning with deterministic safety and routing rules |
| **Streaming UX** | SSE ensures users receive real-time feedback at every pipeline stage |
| **Session-Aware** | SQLite memory enables context-rich, multi-turn conversations |

---

## License

This project is licensed under the [MIT License](LICENSE).

---
