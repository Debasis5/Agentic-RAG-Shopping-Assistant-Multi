"""
Evaluates the RAG pipeline using DeepEval with 4 metrics:
  - Faithfulness
  - Answer Relevancy
  - Contextual Recall
  - Contextual Precision

Strategy (Option 1):
  For each test case the eval script calls rag_node() directly to capture retrieved_docs,
  then calls response_generator_node() to get the actual answer.
  This keeps production code unchanged while giving DeepEval the retrieved context it needs.

Run:
    uv run python eval/run_eval.py
"""

import os
import sys

# Ensure project root is on sys.path so src.* imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Disable DeepEval telemetry and Confident AI remote calls
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
)
from deepeval.models.llms.openai_model import GPTModel

from src.nodes.rag import rag_node
from src.nodes.response_generator import response_generator_node
from eval.test_cases import ALL_TEST_CASES


# ---------------------------------------------------------------------------
# LLM judge — DeepEval's native GPTModel handles JSON mode automatically
# ---------------------------------------------------------------------------

JUDGE_MODEL = "gpt-5.4-mini"
judge = GPTModel(model=JUDGE_MODEL)

# ---------------------------------------------------------------------------
# Metrics (threshold = 0.7, synchronous mode)
# ---------------------------------------------------------------------------

THRESHOLD = 0.7

metrics = [
    FaithfulnessMetric(threshold=THRESHOLD, model=judge),
    AnswerRelevancyMetric(threshold=THRESHOLD, model=judge),
    ContextualRecallMetric(threshold=THRESHOLD, model=judge),
    ContextualPrecisionMetric(threshold=THRESHOLD, model=judge),
]


# ---------------------------------------------------------------------------
# Helper: build a minimal GraphState dict for node calls
# ---------------------------------------------------------------------------

def _make_state(query: str) -> dict:
    return {
        "query": query,
        "retrieved_docs": [],
        "tool_output": None,
        "final_response": None,
        "intent": None,
        "agent_outcome": None,
        "agent_response": None,
        "blocked": False,
    }


# ---------------------------------------------------------------------------
# Fill actual_output and retrieval_context for every test case
# ---------------------------------------------------------------------------

def populate_test_cases():
    print("Running RAG pipeline for all test cases...\n")
    for tc in ALL_TEST_CASES:
        state = _make_state(tc.input)

        # Step 1 — retrieve docs (captures retrieval_context for DeepEval)
        rag_result = rag_node(state)
        state.update(rag_result)

        # Step 2 — generate response
        gen_result = response_generator_node(state)
        state.update(gen_result)

        # Populate DeepEval fields
        tc.actual_output = state.get("final_response", "")
        tc.retrieval_context = state.get("retrieved_docs", tc.retrieval_context)

        print(f"Q: {tc.input}")
        print(f"A: {tc.actual_output[:120]}{'...' if len(tc.actual_output) > 120 else ''}")
        print(f"Chunks retrieved: {len(tc.retrieval_context)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    populate_test_cases()

    print("=" * 60)
    print("Starting DeepEval evaluation (synchronous)...")
    print("=" * 60)

    results = evaluate(
        test_cases=ALL_TEST_CASES,
        metrics=metrics,
        async_config=AsyncConfig(run_async=False),
        display_config=DisplayConfig(inspect_after_run=False),
    )

    print("\n" + "=" * 60)
    print("Evaluation complete.")
    print("=" * 60)

    # Export results to eval/results.json
    import json
    from datetime import datetime

    output = {
        "run_at": datetime.now().isoformat(),
        "threshold": THRESHOLD,
        "judge_model": JUDGE_MODEL,
        "test_cases": [
            {
                "input": tc.input,
                "expected_output": tc.expected_output,
                "actual_output": tc.actual_output,
                "scores": {
                    m.__class__.__name__: {
                        "score": m.score,
                        "passed": m.score >= THRESHOLD if m.score is not None else None,
                        "reason": getattr(m, "reason", None),
                    }
                    for m in metrics
                },
            }
            for tc in ALL_TEST_CASES
        ],
    }

    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {results_path}")
