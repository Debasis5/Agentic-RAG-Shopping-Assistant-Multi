from langchain_openai import ChatOpenAI
from src.state import GraphState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

_SYSTEM_PROMPT = """You are a safety and scope guardrail for Aria, a customer support assistant for ShopEasy (Indian e-commerce).

Your job is to classify the user query into exactly one of four categories:

BLOCK_HARMFUL — if the query:
- Asks for help with hacking, illegal activities, fraud, or anything harmful or abusive.
- Contains violent, threatening, or explicitly illegal intent.

BLOCK_ADVICE — if the query:
- Asks for medical, legal, or financial advice.
- Asks for professional guidance that requires a qualified expert.

BLOCK_SCOPE — if the query:
- Asks to predict future prices or guarantee product availability.
- Asks to compare ShopEasy prices with competitor retailers.
- Is completely unrelated to shopping or customer support (e.g. math homework, coding help, general trivia).

PASS — if the query:
- Is a greeting, thanks, or conversational small talk.
- Asks about orders, shipments, returns, refunds, or account details.
- Asks about ShopEasy store policies (payments, shipping, product condition, account management).
- Asks general questions about products or services available on ShopEasy.

Respond with exactly one word: PASS, BLOCK_HARMFUL, BLOCK_ADVICE, or BLOCK_SCOPE."""

_BLOCK_HARMFUL_RESPONSE = (
    "I cannot and will not provide assistance with hacking or any illegal activities. "
    "This would violate both ShopEasy policies and the law.\n\n"
    "I'm here to help you with legitimate shopping needs such as:\n"
    "- Order status, shipment tracking, and returns\n"
    "- ShopEasy policies: payments, refunds, and account management\n"
    "- General information about products and services on ShopEasy\n\n"
    "Is there something specific you'd like to shop for or learn about on ShopEasy instead?"
)

_BLOCK_ADVICE_RESPONSE = (
    "I can't provide such advice as I'm a shopping assistant, not a qualified professional.\n\n"
    "However, I can help you with:\n"
    "- Order status, shipment tracking, and returns\n"
    "- ShopEasy policies: payments, refunds, and account management\n"
    "- General information about products and services on ShopEasy\n\n"
    "For professional matters, I'd recommend consulting a qualified expert.\n"
    "Is there anything shopping-related I can help you with on ShopEasy instead?"
)

_BLOCK_SCOPE_RESPONSE = (
    "I'm sorry, that's outside the scope of what I can help with. "
    "As Aria, ShopEasy's support assistant, I'm only able to assist with ShopEasy-related queries.\n\n"
    "However, I can help you with:\n"
    "- Order status, shipment tracking, and returns\n"
    "- ShopEasy policies: payments, refunds, and account management\n"
    "- General information about products and services on ShopEasy\n\n"
    "Is there anything shopping-related I can help you with today?"
)


def guardrail_node(state: GraphState) -> dict:
    query = state["query"]
    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])
    decision = response.content.strip().upper()
    if decision not in ("PASS", "BLOCK_HARMFUL", "BLOCK_ADVICE", "BLOCK_SCOPE"):
        decision = "PASS"

    print(f"[guardrail] decision={decision} for query: {query!r}")

    if decision == "BLOCK_HARMFUL":
        return {"guardrail_decision": "BLOCK", "final_response": _BLOCK_HARMFUL_RESPONSE}
    if decision == "BLOCK_ADVICE":
        return {"guardrail_decision": "BLOCK", "final_response": _BLOCK_ADVICE_RESPONSE}
    if decision == "BLOCK_SCOPE":
        return {"guardrail_decision": "BLOCK", "final_response": _BLOCK_SCOPE_RESPONSE}
    return {"guardrail_decision": decision}
