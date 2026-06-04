from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.nodes.rag import rag_node
from src.nodes.response_generator import response_generator_node


class RagAgentState(TypedDict):
    query: str
    messages: Annotated[list, add_messages]
    retrieved_docs: list[str]
    agent_response: str


def _rag_node(state: RagAgentState) -> dict:
    result = rag_node(state)
    return {"retrieved_docs": result["retrieved_docs"]}


def _response_node(state: RagAgentState) -> dict:
    # response_generator_node writes to final_response; map it to agent_response
    adapted = {**state, "final_response": "", "tool_output": None}
    result = response_generator_node(adapted)
    return {"agent_response": result.get("final_response", "")}


def build_rag_agent():
    graph = StateGraph(RagAgentState)
    graph.add_node("rag_node", _rag_node)
    graph.add_node("response_generator_node", _response_node)
    graph.set_entry_point("rag_node")
    graph.add_edge("rag_node", "response_generator_node")
    graph.add_edge("response_generator_node", END)
    return graph.compile()
