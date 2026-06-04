import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.supervisor.graph import build_supervisor_graph
from src.supervisor.state import SupervisorState

load_dotenv()

app = FastAPI(title="ShopEasy Aria API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_supervisor_graph()
    return _graph


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/debug-events")
async def debug_events(request: ChatRequest):
    """Dump all astream_events for a query so we can inspect event names/kinds."""
    initial_state: SupervisorState = {
        "query": request.query,
        "messages": [],
        "guardrail_decision": "",
        "agent_outcome": "",
        "agent_response": "",
        "final_response": "",
    }
    events = []
    async for event in get_graph().astream_events(initial_state, version="v2"):
        kind = event.get("event")
        name = event.get("name", "")
        node = event.get("metadata", {}).get("langgraph_node", "")
        output = event.get("data", {}).get("output")
        entry = {"kind": kind, "name": name, "node": node}
        if isinstance(output, dict):
            entry["output_keys"] = list(output.keys())
            if output.get("final_response"):
                entry["final_response_preview"] = output["final_response"][:80]
        events.append(entry)
    return {"events": events}


@app.post("/chat")
async def chat(request: ChatRequest):
    initial_state: SupervisorState = {
        "query": request.query,
        "messages": [],
        "guardrail_decision": "",
        "agent_outcome": "",
        "agent_response": "",
        "final_response": "",
    }

    async def event_stream():
        agent_outcome = ""
        guardrail_decision = ""

        async for event in get_graph().astream_events(initial_state, version="v2"):
            kind = event.get("event")

            if kind == "on_chain_end" and event.get("data", {}).get("output"):
                output = event["data"]["output"]
                name = event.get("name", "")
                node = event.get("metadata", {}).get("langgraph_node", "")
                if isinstance(output, dict):
                    if output.get("agent_outcome"):
                        agent_outcome = output["agent_outcome"]
                    if output.get("guardrail_decision"):
                        guardrail_decision = output["guardrail_decision"]

                    # Guardrail block — emit pre-built response directly
                    if node == "guardrail" and output.get("final_response"):
                        payload = json.dumps({"type": "token", "content": output["final_response"]})
                        yield f"data: {payload}\n\n"

                    # Synthesis node end — emit the final response once.
                    # Guard on name=="synthesis" to skip the top-level LangGraph
                    # on_chain_end which also carries final_response.
                    if node == "synthesis" and name == "synthesis" and output.get("final_response"):
                        payload = json.dumps({"type": "token", "content": output["final_response"]})
                        yield f"data: {payload}\n\n"

        # Send final metadata
        meta = json.dumps({
            "type": "done",
            "agent_outcome": agent_outcome,
            "guardrail_decision": guardrail_decision,
        })
        yield f"data: {meta}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
