from dotenv import load_dotenv
from src.graph import build_graph

load_dotenv()


def run(query: str):
    graph = build_graph()
    initial_state = {
        "query": query,
        "messages": [],
        "intent": "",
        "retrieved_docs": [],
        "tool_output": None,
        "guardrail_decision": "",
        "final_response": "",
    }
    result = graph.invoke(initial_state)
    print(f"\nFinal response: {result['final_response']}")
    return result


if __name__ == "__main__":
    run("Hello, what can you help me with?")
