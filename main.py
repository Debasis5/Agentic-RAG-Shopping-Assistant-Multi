from dotenv import load_dotenv
from src.supervisor.graph import build_supervisor_graph

load_dotenv()


def run(query: str):
    graph = build_supervisor_graph()
    initial_state = {
        "query": query,
        "messages": [],
        "guardrail_decision": "",
        "agent_outcome": "",
        "agent_response": "",
        "final_response": "",
    }
    result = graph.invoke(initial_state)
    print(f"\nAgent: {result['agent_outcome']}  |  Final response: {result['final_response']}")
    return result


if __name__ == "__main__":
    run("Hello, what can you help me with?")
