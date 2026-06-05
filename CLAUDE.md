# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv run` to ensure the project's virtual environment is used. Plain `python`/`uvicorn`/`streamlit` will use the wrong environment.

```bash
# Install dependencies
uv sync

# Run the FastAPI backend (required before starting Streamlit)
uv run uvicorn api:app --reload --port 8000

# Run the Streamlit frontend
uv run streamlit run streamlit_app.py

# Run a single query via CLI (bypasses API/UI)
uv run python main.py

# One-time setup: generate policy PDFs then ingest into ChromaDB
uv run python scripts/generate_docs.py
uv run python pipelines/ingest_docs.py

# Run RAG evaluation (DeepEval)
uv run python eval/run_eval.py
```

No test suite or linter is configured in this project.

## Docker

The application is containerised as a single image (`dockerdebp/shopeasy-aria`). See `projectdocs/docker_deployment.md` for the full guide.

```bash
# Build image locally
docker build -t dockerdebp/shopeasy-aria:latest .

# Push to Docker Hub
docker push dockerdebp/shopeasy-aria:latest

# On AWS EC2 — pull and restart
docker pull dockerdebp/shopeasy-aria:latest
docker compose up -d
```

**Ports:** FastAPI backend on `8000`, Streamlit frontend on `8501`.  
**Health check:** `GET /health` on port 8000 returns `{"status": "ok"}`.  
**Volume:** `chroma_db/` is declared as a Docker volume — vector store data persists across restarts.  
**Env:** The `.env` file must exist on the host; it is not baked into the image. Ensure `docker-compose.yml` has `env_file: .env`.

## Architecture

This is a two-process application: a **FastAPI backend** (`api.py`) and a **Streamlit frontend** (`streamlit_app.py`). They communicate via HTTP — the frontend POSTs to `/chat` and receives a Server-Sent Events stream of tokens.

### Architecture: supervisor-orchestrator multi-agent (`src/`)

> Migration is complete. The supervisor + sub-agent design is the current and only pipeline.

```
User query
    │
    ▼
Supervisor graph (src/supervisor/graph.py)
    ├── guardrail node          ← safety + scope check (BLOCK → END)
    └── delegation_router node  ← which agent handles this?
            │
            ├──► RAG agent (src/agents/rag_agent.py)
            │       └── rag_node → response_generator (RAG path)
            │
            ├──► Order agent (src/agents/order_agent.py)
            │       └── tool_call_node → response_generator (tool path)
            │
            ├──► Escalation agent (src/agents/escalation_agent.py)
            │       └── complaint_handler → human_handoff → ticket_creation
            │
            └──► chitchat (inline in supervisor, no sub-agent)
                    │
                    ▼
            synthesis node  ← merge result + faithfulness check → END
```

**Key design decisions:**
- Guardrail lives in the supervisor only — runs once before delegation, sub-agents never see blocked queries.
- Each sub-agent is an independent `StateGraph` with its own state — changes to one agent don't affect others.
- RAG stays as bare vector lookup for now (top-3 ChromaDB retrieval). Query rewriter + reranker will be added later inside `rag_agent.py` without touching the supervisor.
- Chitchat is handled inline by the supervisor (no dedicated sub-agent graph needed).
- The existing node files in `src/nodes/` are reused as-is inside the sub-agent graphs — no rewrites.

### State design

| State class | File | Used by |
|---|---|---|
| `SupervisorState` | `src/supervisor/state.py` | Supervisor graph |
| `RagAgentState` | `src/agents/rag_agent.py` | RAG agent graph |
| `OrderAgentState` | `src/agents/order_agent.py` | Order agent graph |
| `EscalationAgentState` | `src/agents/escalation_agent.py` | Escalation agent graph |

### File layout (target)

```
src/
  nodes/                        ← existing node files, reused as-is
    guardrail.py
    rag.py
    tool_call.py
    chitchat.py
    response_generator.py
    intent_router.py            ← retired after migration (delegation_router replaces it)
  agents/
    __init__.py
    rag_agent.py                ← RAG sub-agent graph
    order_agent.py              ← Order sub-agent graph
    escalation_agent.py         ← Escalation sub-agent graph
  supervisor/
    __init__.py
    state.py                    ← SupervisorState
    graph.py                    ← Supervisor graph (entry point)
    delegation_router.py        ← LLM classifier: rag | order | escalation | chitchat
    synthesis.py                ← Merge sub-agent result + faithfulness check
  graph.py                      ← re-exports build_supervisor_graph() for backwards compat
  state.py                      ← re-exports SupervisorState for backwards compat
```

**Critical pattern — lazy LLM initialisation:** Every node file uses `@lru_cache(maxsize=1)` on a `_get_llm()` / `_get_retriever()` factory instead of creating `ChatOpenAI` / `OpenAIEmbeddings` at module level. This is required because `src/graph.py` is imported before `load_dotenv()` runs in `api.py`. Breaking this pattern will cause `openai.OpenAIError: Missing credentials` on startup. **All new nodes and agents must follow this pattern.**

### Streaming (api.py)

`POST /chat` uses `graph.astream_events(state, version="v2")` to stream events. Only `on_chat_model_stream` events from nodes `response_generator` and `chitchat` are forwarded as tokens — guardrail and intent_router LLM outputs are filtered out by checking `event["metadata"]["langgraph_node"]`. Guardrail blocks are emitted as a single token from the `on_chain_end` event of the `guardrail` node.

After migration, the streamed node names will change — `synthesis` replaces `response_generator` as the primary streaming node.

### Vector store

ChromaDB persists locally at `chroma_db/` (relative to project root). The collection is named `support_docs`. Documents come from PDFs in `data/docs/` chunked at 1000 chars. The RAG node retrieves top-3 chunks.

### Streamlit UI (known behaviours)

**Sidebar always visible:** Streamlit 1.58 hides the sidebar via a CSS `translateX` when `aria-expanded="false"`. The fix forces `transform: translateX(0)` and hides the collapse/reopen buttons. Do not set `background-color` or `color` on sidebar elements — it causes invisible (white-on-white) text.

**Fixed Aria header:** The `.top-sticky` bar uses `position: fixed` (not `sticky`) so it stays pinned as chat messages scroll. It is offset `left: 244px` to clear the sidebar. A `height: 150px` spacer `div` is injected after the header in the normal document flow so the first message is not hidden beneath it. If the header height changes, adjust both the spacer height and the `padding-top` on `.block-container`.

## Environment

Requires a `.env` file at the project root:
```
OPENAI_API_KEY=sk-...
```

Model used throughout: `gpt-4o-mini`. Embeddings: `text-embedding-3-small`.
