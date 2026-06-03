from langchain_openai import ChatOpenAI
from src.state import GraphState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

_SYSTEM_PROMPT = """You are an intent classifier for a customer support assistant.

Classify the user query into exactly one of these intents:

- rag        : questions about products, policies, FAQs, or anything that needs knowledge base lookup
- tool_call  : questions about a specific order, account, shipping status, or anything needing live data
- chitchat   : greetings, small talk, thanks, or anything conversational

Respond with exactly one word: rag, tool_call, or chitchat."""


def intent_router_node(state: GraphState) -> dict:
    query = state["query"]
    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    intent = response.content.strip().lower()
    if intent not in ("rag", "tool_call", "chitchat"):
        intent = "chitchat"

    print(f"[intent_router] intent={intent!r} for query: {query!r}")
    return {"intent": intent}
