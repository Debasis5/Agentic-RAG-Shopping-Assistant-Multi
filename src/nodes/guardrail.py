from langchain_openai import ChatOpenAI
from src.state import GraphState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

_SYSTEM_PROMPT = """You are a safety and scope guardrail for a customer support assistant.

Your job is to decide whether the user query is safe and in-scope.

Rules:
- BLOCK if the query contains harmful, abusive, or illegal content.
- BLOCK if the query is completely unrelated to customer support (e.g. math homework, coding help).
- PASS everything else, including greetings, product questions, order queries, and general support topics.

Respond with exactly one word: PASS or BLOCK."""


def guardrail_node(state: GraphState) -> dict:
    query = state["query"]
    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    decision = response.content.strip().upper()
    if decision not in ("PASS", "BLOCK"):
        decision = "PASS"

    print(f"[guardrail] decision={decision} for query: {query!r}")
    return {"guardrail_decision": decision}
