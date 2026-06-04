from functools import lru_cache
from langchain_openai import ChatOpenAI


@lru_cache(maxsize=1)
def _get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


_SYSTEM_PROMPT = """You are an intent classifier for a customer support assistant at ShopEasy, an Indian e-commerce platform.

Classify the user query into exactly one of these intents:

- rag        : policy or FAQ questions — returns, payments, shipping timelines, product conditions, account policies
- order      : specific order, shipment, return, or account status — needs live data lookup
- escalation : complaints, damaged items, wrong items delivered, requests for a human agent
- chitchat   : greetings, small talk, thanks, or anything purely conversational

Respond with exactly one word: rag, order, escalation, or chitchat."""


def delegation_router_node(state: dict) -> dict:
    query = state["query"]
    response = _get_llm().invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    agent_outcome = response.content.strip().lower()
    if agent_outcome not in ("rag", "order", "escalation", "chitchat"):
        agent_outcome = "chitchat"

    print(f"[delegation_router] agent_outcome={agent_outcome!r} for query: {query!r}")
    return {"agent_outcome": agent_outcome}
