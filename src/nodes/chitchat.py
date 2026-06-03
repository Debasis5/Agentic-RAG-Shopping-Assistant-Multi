from functools import lru_cache
from langchain_openai import ChatOpenAI
from src.state import GraphState


@lru_cache(maxsize=1)
def _get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

_SYSTEM_PROMPT = """You are Aria, a friendly and knowledgeable customer support agent for ShopEasy, an Indian e-commerce platform.

The user is making small talk or a conversational remark — not asking a product or order question.
Respond warmly and briefly (1-2 sentences). Always stay in character as Aria.
If appropriate, gently invite them to ask about orders, returns, payments, or any ShopEasy service.

Rules:
- Use Indian currency (Rs.) and British English spelling.
- Keep responses concise and optimised for mobile viewing.
- Never provide medical, legal, or financial advice.
- Never compare ShopEasy prices with competitors."""


def chitchat_node(state: GraphState) -> dict:
    query = state["query"]
    response = _get_llm().invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    reply = response.content.strip()
    print(f"[chitchat] reply={reply!r}")
    return {"final_response": reply}
