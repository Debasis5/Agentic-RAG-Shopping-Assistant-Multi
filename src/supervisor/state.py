from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class SupervisorState(TypedDict):
    query: str
    messages: Annotated[list, add_messages]
    guardrail_decision: str   # "PASS" | "BLOCK"
    agent_outcome: str        # "rag" | "order" | "escalation" | "chitchat"
    agent_response: str       # raw response from the sub-agent
    final_response: str       # after synthesis
