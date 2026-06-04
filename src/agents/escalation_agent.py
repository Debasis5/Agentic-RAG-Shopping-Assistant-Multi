import random
from functools import lru_cache
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI


class EscalationAgentState(TypedDict):
    query: str
    messages: Annotated[list, add_messages]
    complaint_type: str   # "damaged_item" | "wrong_item" | "late_delivery" | "other"
    ticket_id: str
    agent_response: str


@lru_cache(maxsize=1)
def _get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


_COMPLAINT_CLASSIFIER_PROMPT = """You are a complaint classification assistant for ShopEasy.

Classify the customer's complaint into exactly one of these categories:
- damaged_item   — product arrived damaged or broken
- wrong_item     — wrong product was delivered
- late_delivery  — order is significantly delayed
- other          — any other complaint or escalation request

Reply with ONLY the category name, nothing else."""


_HANDOFF_PROMPT = """You are Aria, a customer support agent for ShopEasy.

The customer has raised a complaint that requires human support.
Write a short, empathetic handoff message (2-3 sentences) that:
1. Acknowledges their complaint type: {complaint_type}
2. Informs them a support agent will contact them
3. Provides the support number: 1800-3000-9009 and estimated wait time: 10-15 minutes

Keep it warm and professional. Use British English spelling."""


def complaint_handler_node(state: EscalationAgentState) -> dict:
    query = state["query"]
    response = _get_llm().invoke([
        {"role": "system", "content": _COMPLAINT_CLASSIFIER_PROMPT},
        {"role": "user", "content": query},
    ])
    complaint_type = response.content.strip().lower()
    # Normalise to known categories
    valid = {"damaged_item", "wrong_item", "late_delivery", "other"}
    if complaint_type not in valid:
        complaint_type = "other"
    print(f"[complaint_handler] complaint_type={complaint_type!r}")
    return {"complaint_type": complaint_type}


def human_handoff_node(state: EscalationAgentState) -> dict:
    complaint_type = state["complaint_type"].replace("_", " ")
    prompt = _HANDOFF_PROMPT.format(complaint_type=complaint_type)
    response = _get_llm().invoke([
        {"role": "system", "content": prompt},
        {"role": "user", "content": state["query"]},
    ])
    handoff_message = response.content.strip()
    print(f"[human_handoff] message generated ({len(handoff_message)} chars)")
    return {"agent_response": handoff_message}


def ticket_creation_node(state: EscalationAgentState) -> dict:
    ticket_id = f"TKT-{random.randint(100000, 999999)}"
    confirmation = (
        f"{state['agent_response']}\n\n"
        f"Your complaint has been logged. Ticket ID: **{ticket_id}**. "
        f"Please keep this for your reference."
    )
    print(f"[ticket_creation] ticket_id={ticket_id!r}")
    return {"ticket_id": ticket_id, "agent_response": confirmation}


def build_escalation_agent():
    graph = StateGraph(EscalationAgentState)
    graph.add_node("complaint_handler", complaint_handler_node)
    graph.add_node("human_handoff", human_handoff_node)
    graph.add_node("ticket_creation", ticket_creation_node)
    graph.set_entry_point("complaint_handler")
    graph.add_edge("complaint_handler", "human_handoff")
    graph.add_edge("human_handoff", "ticket_creation")
    graph.add_edge("ticket_creation", END)
    return graph.compile()
