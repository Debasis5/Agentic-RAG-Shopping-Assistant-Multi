from functools import lru_cache
from langchain_openai import ChatOpenAI


@lru_cache(maxsize=1)
def _get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


_FAITHFULNESS_PROMPT = """You are a quality-check assistant for ShopEasy's support system.

You will be given a customer question, the source knowledge base excerpts that were retrieved, and a draft answer.
Check whether the answer is faithful — it should only state facts without fabricating policy details. Every claim must be supported by the provided source excerpts.

If the answer is faithful to the sources, respond with exactly: PASS
If the answer contains fabricated or unsupported claims not found in the sources, respond with exactly: FAIL

When in doubt, respond with PASS.

Respond with one word only: PASS or FAIL."""

_FALLBACK_RESPONSE = (
    "I'm sorry, I wasn't able to provide a verified answer to your question. "
    "Please contact ShopEasy support at 1800-3000-9009 for accurate policy information."
)


def synthesis_node(state: dict) -> dict:
    agent_outcome = state.get("agent_outcome", "")
    agent_response = state.get("agent_response", "")

    # Non-RAG paths pass through directly
    if agent_outcome != "rag":
        print(f"[synthesis] pass-through for agent_outcome={agent_outcome!r}")
        return {"final_response": agent_response}

    # RAG path — faithfulness check against retrieved docs
    query = state["query"]
    retrieved_docs = state.get("retrieved_docs", [])
    sources = "\n\n".join(retrieved_docs) if retrieved_docs else "(no source documents available)"
    check = _get_llm().invoke([
        {"role": "system", "content": _FAITHFULNESS_PROMPT},
        {"role": "user", "content": f"Sources:\n{sources}\n\nQuestion: {query}\n\nAnswer: {agent_response}"},
    ])
    verdict = check.content.strip().upper()
    print(f"[synthesis] faithfulness verdict={verdict!r}")

    if verdict == "PASS":
        return {"final_response": agent_response}

    print("[synthesis] faithfulness FAIL — returning fallback")
    return {"final_response": _FALLBACK_RESPONSE}
