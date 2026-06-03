from langchain_openai import ChatOpenAI
from src.state import GraphState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

_SYSTEM_PROMPT = """You are a friendly and helpful customer support assistant for ShopEasy, an Indian e-commerce platform.

The user is making small talk or a conversational remark — not asking a product or order question.
Respond warmly and briefly (1-2 sentences). Always stay in character as a ShopEasy support agent.
If appropriate, gently invite them to ask about orders, returns, payments, or any ShopEasy service."""


def chitchat_node(state: GraphState) -> dict:
    query = state["query"]
    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    reply = response.content.strip()
    print(f"[chitchat] reply={reply!r}")
    return {"final_response": reply}
