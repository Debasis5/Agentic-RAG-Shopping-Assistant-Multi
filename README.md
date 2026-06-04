# ShopEasy Agentic RAG — Aria Customer Support

An agentic Retrieval-Augmented Generation (RAG) system for ShopEasy, an Indian e-commerce platform. **Aria** is a context-aware AI customer support agent built on a **supervisor + multi-agent** LangGraph architecture, served via a FastAPI streaming backend, and presented through a Streamlit chat interface.

---

## Features

- **Supervisor-orchestrated multi-agent design** — a central supervisor graph delegates queries to independent specialised sub-agents
- **Safety guardrails** — classifies and blocks harmful, out-of-scope, or advice-seeking queries before they reach any sub-agent
- **Smart delegation router** — LLM classifier routes each query to the right agent: RAG, Order, Escalation, or chitchat
- **RAG agent** — retrieves relevant policy excerpts from a ChromaDB vector store and synthesises a grounded answer
- **Order agent** — handles live data lookups (order status, shipment tracking, account info, return status) via function calling
- **Escalation agent** — classifies complaints, generates empathetic handoff messages, and creates support tickets with unique IDs
- **Faithfulness check** — synthesis node validates RAG answers against retrieved documents before returning them
- **Streaming responses** — tokens stream token-by-token from FastAPI to the Streamlit UI via Server-Sent Events (SSE)
- **Aria persona** — consistent, warm, mobile-optimised responses in British English with Indian currency formatting

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    SUPERVISOR GRAPH                     │
│                                                         │
│  ┌───────────┐                                          │
│  │ Guardrail │──── BLOCK ───────────────────────────► END
│  └─────┬─────┘                                          │
│        │ PASS                                           │
│        ▼                                                │
│  ┌──────────────────┐                                   │
│  │ Delegation Router│                                   │
│  └──────┬───────────┘                                   │
│         │                                               │
│    ┌────┴──────────────────────────────────────┐        │
│    │ chitchat ──────────────────────────────►  │        │
│    │                                           │        │
│    │          ┌─────────────────────────┐      │        │
│    ├─ rag ──► │  RAG sub-agent graph    │ ────►│        │
│    │          │  rag_node               │      │        │
│    │          │    → response_generator │      ▼        │
│    │          └─────────────────────────┘  ┌──────────┐ │
│    │                                       │          │ │
│    │          ┌─────────────────────────┐  │synthesis │ │
│    ├─ order ► │  Order sub-agent graph  │► │   node   │ │
│    │          │  tool_call_node         │  │          │ │
│    │          │    → response_generator │  └────┬─────┘ │
│    │          └─────────────────────────┘       │       │
│    │                                            │       │
│    │                                            │       │
│    │          ┌─────────────────────────┐       │       │
│    └─ escal.► │Escalation sub-agent     │──────►│       │
│               │  complaint_handler      │               │
│               │    → human_handoff      │               │
│               │    → ticket_creation    │               │
│               └─────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                     Final Response
```

> **Synthesis node** — every path converges here before the final response is returned. For the RAG path it acts as a **quality gate**: an LLM faithfulness check validates the answer against the retrieved documents; a `FAIL` verdict replaces the response with a safe fallback. For `order`, `escalation`, and `chitchat` paths the sub-agent output is passed through unchanged — no extra LLM call is made.

> **Chitchat** is handled by a single node directly inside the supervisor — it has no sub-agent graph, no private state, and no tools. The delegation router sends it straight to `_chitchat_node`, which calls `chitchat_node` and writes the result to `agent_response`, then falls through to synthesis like any other path.

### Sub-agent graphs

| Sub-agent | Internal graph |
|---|---|
| **RAG** | `rag_node → response_generator_node → END` |
| **Order** | `tool_call_node → response_generator_node → END` |
| **Escalation** | `complaint_handler → human_handoff → ticket_creation → END` |

### Key design decisions

- **Guardrail runs once** in the supervisor — sub-agents never receive blocked queries.
- **Sub-agents are independent** `StateGraph` instances — changes to one agent do not affect others.
- **Chitchat is a supervisor node, not a sub-agent** — it needs no private state or tools, so a dedicated graph would add overhead with no benefit.
- **Sub-agents are invoked via `.invoke()`** wrapper nodes (not nested LangGraph subgraphs) — keeps SSE streaming straightforward.
- **Lazy LLM initialisation** — every node uses `@lru_cache(maxsize=1)` on a `_get_llm()` factory, because `src/graph.py` is imported before `load_dotenv()` runs.

---

## Components

| File | Description |
|---|---|
| `api.py` | FastAPI app — `POST /chat` streams SSE tokens, `GET /health`, `POST /debug-events` |
| `streamlit_app.py` | Streamlit frontend — Aria chat UI with streaming support and intent badges |
| `main.py` | CLI entrypoint — run a single query without the API/UI |
| `src/supervisor/graph.py` | Supervisor `StateGraph` — entry point, wires all agents and routing |
| `src/supervisor/state.py` | `SupervisorState` TypedDict — shared state across the supervisor |
| `src/supervisor/delegation_router.py` | LLM classifier — maps queries to `rag \| order \| escalation \| chitchat` |
| `src/supervisor/synthesis.py` | Merges sub-agent result; runs faithfulness check for the RAG path |
| `src/agents/rag_agent.py` | RAG sub-agent graph + `RagAgentState` |
| `src/agents/order_agent.py` | Order sub-agent graph + `OrderAgentState` |
| `src/agents/escalation_agent.py` | Escalation sub-agent graph + `EscalationAgentState` |
| `src/nodes/guardrail.py` | Safety classifier — `PASS / BLOCK_HARMFUL / BLOCK_ADVICE / BLOCK_SCOPE` |
| `src/nodes/rag.py` | ChromaDB retriever — top-3 semantic search over policy docs |
| `src/nodes/tool_call.py` | Function calling — order, shipment, account, return tools |
| `src/nodes/chitchat.py` | Conversational response node (used inline by the supervisor) |
| `src/nodes/response_generator.py` | Final answer synthesis using Aria persona |
| `src/graph.py` | Re-exports `build_supervisor_graph()` for backwards compatibility |
| `src/state.py` | Re-exports `SupervisorState` for backwards compatibility |
| `pipelines/ingest_docs.py` | One-time pipeline — chunks and embeds PDFs into ChromaDB |
| `scripts/generate_docs.py` | One-time script — generates 5 ShopEasy policy PDFs |

---

## State design

| State class | File | Used by |
|---|---|---|
| `SupervisorState` | `src/supervisor/state.py` | Supervisor graph |
| `RagAgentState` | `src/agents/rag_agent.py` | RAG agent graph |
| `OrderAgentState` | `src/agents/order_agent.py` | Order agent graph |
| `EscalationAgentState` | `src/agents/escalation_agent.py` | Escalation agent graph |

`SupervisorState` fields:

```python
query: str
messages: Annotated[list, add_messages]
guardrail_decision: str   # "PASS" | "BLOCK"
agent_outcome: str        # "rag" | "order" | "escalation" | "chitchat"
agent_response: str       # raw response from the sub-agent
final_response: str       # after synthesis
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM & Embeddings | OpenAI GPT-4o-mini + text-embedding-3-small |
| Vector Store | ChromaDB (local persistence) |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Package Manager | UV |

---

## Project Structure

```
├── api.py                      # FastAPI backend
├── streamlit_app.py            # Streamlit frontend
├── main.py                     # CLI entrypoint
├── pyproject.toml              # Project dependencies
├── .env                        # Environment variables (not committed)
├── data/
│   └── docs/                   # Generated policy PDFs
├── chroma_db/                  # ChromaDB vector store (local)
├── notebooks/
│   ├── test_notebook.ipynb     # Original single-agent test notebook (preserved)
│   └── test_notebook_multi.ipynb # Multi-agent end-to-end test notebook
├── pipelines/
│   └── ingest_docs.py          # Document ingestion pipeline
├── scripts/
│   └── generate_docs.py        # Policy PDF generator
└── src/
    ├── graph.py                # Re-exports build_supervisor_graph()
    ├── state.py                # Re-exports SupervisorState
    ├── nodes/
    │   ├── guardrail.py
    │   ├── rag.py
    │   ├── tool_call.py
    │   ├── chitchat.py
    │   └── response_generator.py
    ├── supervisor/
    │   ├── graph.py            # Supervisor graph (entry point)
    │   ├── state.py            # SupervisorState
    │   ├── delegation_router.py
    │   └── synthesis.py
    └── agents/
        ├── rag_agent.py
        ├── order_agent.py
        └── escalation_agent.py
```

---

## Setup

### Prerequisites

- Python 3.13+
- [UV](https://docs.astral.sh/uv/) package manager
- OpenAI API key

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd agents-capstone-project-agentic-rag-multi
uv sync
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
```

### 3. Generate policy documents (one-time)

```bash
uv run python scripts/generate_docs.py
```

### 4. Ingest documents into ChromaDB (one-time)

```bash
uv run python pipelines/ingest_docs.py
```

---

## Running the Application

### Start the FastAPI backend

```bash
uv run uvicorn api:app --reload --port 8000
```

### Start the Streamlit frontend (separate terminal)

```bash
uv run streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

### CLI (no API/UI required)

```bash
uv run python main.py
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/chat` | Stream a response — body: `{"query": "..."}` |
| `POST` | `/debug-events` | Dump all `astream_events` for a query (dev/debug) |

The `/chat` endpoint returns Server-Sent Events with two frame types:

```json
// Token frame (one or more, streamed during generation)
{"type": "token", "content": "Hello"}

// Done frame (sent after the final token)
{"type": "done", "agent_outcome": "rag", "guardrail_decision": "PASS"}
```

---

## Delegation Router

The delegation router classifies each passing query into one of four intents:

| Intent | Trigger |
|---|---|
| `rag` | Policy / FAQ questions — returns, payments, shipping, product conditions, account policies |
| `order` | Specific order / shipment / return / account status — needs live data |
| `escalation` | Complaints, damaged items, wrong items, requests for a human agent |
| `chitchat` | Greetings, small talk, thanks, purely conversational |

---

## Guardrail Behaviour

| Decision | Trigger |
|---|---|
| `PASS` | Shopping queries, greetings, account/order questions |
| `BLOCK_HARMFUL` | Hacking, fraud, illegal activity, abuse |
| `BLOCK_ADVICE` | Medical, legal, or financial advice |
| `BLOCK_SCOPE` | Competitor comparisons, price predictions, unrelated topics |

Guardrail blocks are emitted immediately — the query never reaches the delegation router or sub-agents.

---

## Escalation Agent

When a query is routed to the escalation agent it runs three nodes in sequence:

1. **`complaint_handler`** — LLM classifies the complaint into `damaged_item | wrong_item | late_delivery | other`
2. **`human_handoff`** — generates an empathetic handoff message with support number (1800-3000-9009) and estimated wait time
3. **`ticket_creation`** — appends a mock ticket ID (`TKT-XXXXXX`) to the response

---

## Synthesis & Faithfulness Check

After every sub-agent returns, the `synthesis` node:

- **Non-RAG paths** (`order`, `escalation`, `chitchat`): passes `agent_response` through directly as `final_response`.
- **RAG path**: runs an LLM faithfulness check — if the answer contains fabricated or unsupported claims (`FAIL`), a safe fallback response is returned instead.

---

## Knowledge Base & Ingestion Pipeline

Five ShopEasy policy PDFs are generated by `scripts/generate_docs.py` into `data/docs/`:

- Returns & Refunds Policy
- Shipping & Delivery Policy
- Payments & Pricing Policy
- Account Management Policy
- Product Condition & Listing Guidelines

`pipelines/ingest_docs.py` processes these into ChromaDB across four stages:

```
data/docs/*.pdf
      │
      ▼
┌──────────────────────────────────────────┐
│ Stage 1 · LOAD                           │
│  PyPDFDirectoryLoader                    │
│  · Reads all PDFs, merges pages per doc  │
│  · Extracts metadata per document:       │
│    title, version, effective_date,       │
│    department                            │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│ Stage 2 · CHUNK                          │
│  RecursiveCharacterTextSplitter          │
│  · chunk_size    = 650 chars             │
│  · chunk_overlap = 0                     │
│  · Splits on numbered sections first     │
│    (regex: \n(?=\d+\. )), then \n\n,     │
│    then \n                               │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│ Stage 3 · EMBED                          │
│  OpenAIEmbeddings                        │
│  · Model: text-embedding-3-small         │
│  · 1536-dimensional vectors              │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│ Stage 4 · STORE                          │
│  ChromaDB                                │
│  · Collection : support_docs             │
│  · Persisted to : chroma_db/             │
└──────────────────────────────────────────┘
```

At query time the RAG node retrieves the **top-3 chunks** by cosine similarity and passes them as context to the response generator.

Re-run the pipeline whenever documents change:

```bash
uv run python pipelines/ingest_docs.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (required) |
