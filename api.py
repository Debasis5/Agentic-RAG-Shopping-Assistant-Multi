import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.graph import build_graph
from src.state import GraphState

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
        _graph = build_graph()
    return _graph


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    initial_state: GraphState = {
        "query": request.query,
        "messages": [],
        "intent": "",
        "retrieved_docs": [],
        "tool_output": None,
        "guardrail_decision": "",
        "final_response": "",
    }

    async def event_stream():
        final_response = ""
        intent = ""
        guardrail_decision = ""

        # Stream graph events; we capture the final_response from the last node
        # that sets it, then stream its text token-by-token via a second LLM call.
        # For nodes that already have final_response (guardrail blocks, chitchat),
        # we stream the pre-built string directly.
        async for event in get_graph().astream_events(initial_state, version="v2"):
            kind = event.get("event")
            name = event.get("name", "")

            # Capture metadata from node outputs
            if kind == "on_chain_end" and event.get("data", {}).get("output"):
                output = event["data"]["output"]
                node = event.get("metadata", {}).get("langgraph_node", "")
                if isinstance(output, dict):
                    if output.get("intent"):
                        intent = output["intent"]
                    if output.get("guardrail_decision"):
                        guardrail_decision = output["guardrail_decision"]
                    # Guardrail block: stream the pre-built response text directly
                    if node == "guardrail" and output.get("final_response"):
                        blocked_text = output["final_response"]
                        payload = json.dumps({"type": "token", "content": blocked_text})
                        yield f"data: {payload}\n\n"

            # Stream tokens only from nodes that produce the final response
            if kind == "on_chat_model_stream":
                node = event.get("metadata", {}).get("langgraph_node", "")
                if node not in ("response_generator", "chitchat"):
                    continue
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    token = chunk.content
                    payload = json.dumps({"type": "token", "content": token})
                    yield f"data: {payload}\n\n"

        # Send final metadata
        meta = json.dumps({
            "type": "done",
            "intent": intent,
            "guardrail_decision": guardrail_decision,
        })
        yield f"data: {meta}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
