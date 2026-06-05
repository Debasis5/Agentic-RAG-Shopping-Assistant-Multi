from langgraph.graph import StateGraph, END

from src.supervisor.state import SupervisorState
from src.supervisor.delegation_router import delegation_router_node
from src.supervisor.synthesis import synthesis_node
from src.nodes.guardrail import guardrail_node
from src.nodes.chitchat import chitchat_node
from src.agents.rag_agent import build_rag_agent
from src.agents.order_agent import build_order_agent
from src.agents.escalation_agent import build_escalation_agent


# --- Sub-agent wrapper nodes ---

def _rag_agent_node(state: SupervisorState) -> dict:
    agent = build_rag_agent()
    result = agent.invoke({
        "query": state["query"],
        "messages": state.get("messages", []),
        "retrieved_docs": [],
        "agent_response": "",
    })
    return {
        "agent_response": result["agent_response"],
        "retrieved_docs": result.get("retrieved_docs", []),
    }


def _order_agent_node(state: SupervisorState) -> dict:
    agent = build_order_agent()
    result = agent.invoke({
        "query": state["query"],
        "messages": state.get("messages", []),
        "tool_output": None,
        "agent_response": "",
    })
    return {"agent_response": result["agent_response"]}


def _escalation_agent_node(state: SupervisorState) -> dict:
    agent = build_escalation_agent()
    result = agent.invoke({
        "query": state["query"],
        "messages": state.get("messages", []),
        "complaint_type": "",
        "ticket_id": "",
        "agent_response": "",
    })
    return {"agent_response": result["agent_response"]}


def _chitchat_node(state: SupervisorState) -> dict:
    result = chitchat_node(state)
    return {"agent_response": result["final_response"]}


# --- Routing functions ---

def _route_after_guardrail(state: SupervisorState) -> str:
    if state["guardrail_decision"] == "BLOCK":
        return "blocked"
    return "delegation_router"


def _route_by_agent(state: SupervisorState) -> str:
    return state.get("agent_outcome", "chitchat")


# --- Build graph ---

def build_supervisor_graph():
    graph = StateGraph(SupervisorState)

    graph.add_node("guardrail", guardrail_node)
    graph.add_node("delegation_router", delegation_router_node)
    graph.add_node("rag", _rag_agent_node)
    graph.add_node("order", _order_agent_node)
    graph.add_node("escalation", _escalation_agent_node)
    graph.add_node("chitchat", _chitchat_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("guardrail")

    graph.add_conditional_edges(
        "guardrail",
        _route_after_guardrail,
        {"blocked": END, "delegation_router": "delegation_router"},
    )

    graph.add_conditional_edges(
        "delegation_router",
        _route_by_agent,
        {
            "rag":        "rag",
            "order":      "order",
            "escalation": "escalation",
            "chitchat":   "chitchat",
        },
    )

    graph.add_edge("rag",        "synthesis")
    graph.add_edge("order",      "synthesis")
    graph.add_edge("escalation", "synthesis")
    graph.add_edge("chitchat",   "synthesis")
    graph.add_edge("synthesis",  END)

    return graph.compile()
