from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    # The original user query
    query: str
    # Conversation history (managed by LangGraph's add_messages reducer)
    messages: Annotated[list, add_messages]
    # Intent classified by the router: "rag" | "tool_call" | "chitchat"
    intent: str
    # Documents retrieved by the RAG node
    retrieved_docs: list[str]
    # Output from the tool call node (API results)
    tool_output: Any
    # Safety decision from guardrail: "pass" | "block"
    guardrail_decision: str
    # Final answer to return to the user
    final_response: str
