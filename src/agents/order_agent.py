from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.nodes.tool_call import tool_call_node
from src.nodes.response_generator import response_generator_node


class OrderAgentState(TypedDict):
    query: str
    messages: Annotated[list, add_messages]
    tool_output: Any
    agent_response: str


def _tool_call_node(state: OrderAgentState) -> dict:
    result = tool_call_node(state)
    return {"tool_output": result["tool_output"]}


def _response_node(state: OrderAgentState) -> dict:
    # response_generator_node writes to final_response; map it to agent_response
    adapted = {**state, "final_response": "", "retrieved_docs": []}
    result = response_generator_node(adapted)
    return {"agent_response": result.get("final_response", "")}


def build_order_agent():
    graph = StateGraph(OrderAgentState)
    graph.add_node("tool_call_node", _tool_call_node)
    graph.add_node("response_generator_node", _response_node)
    graph.set_entry_point("tool_call_node")
    graph.add_edge("tool_call_node", "response_generator_node")
    graph.add_edge("response_generator_node", END)
    return graph.compile()
