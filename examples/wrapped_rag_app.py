"""Integration example: a RAG pipeline whose generation step is monitored.

Demonstrates monitoring a multi-stage RAG flow — offline embeddings via
``shared_core.embeddings.get_embedding_provider(offline=True)`` for retrieval,
then a monitored ``MonitoredLLMClient`` generation call. Each generation is
metered into the telemetry store with a prompt version, so you can compare the
cost of different RAG prompt templates. Fully offline; set API keys and drop
``mocked_response`` to use real embeddings/providers.

    python examples/wrapped_rag_app.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from llm_monitor.sdk import MonitoredLLMClient  # noqa: E402
from llm_monitor.storage import InMemoryTelemetryStore  # noqa: E402

DOCUMENTS = [
    "The Eiffel Tower is located in Paris and was completed in 1889.",
    "Mount Everest is the tallest mountain above sea level.",
    "Python is a high-level programming language created by Guido van Rossum.",
    "The mitochondria is the powerhouse of the cell.",
]


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class MonitoredRAG:
    """Tiny RAG pipeline with offline embeddings and a monitored LLM call."""

    def __init__(self, store: InMemoryTelemetryStore) -> None:
        from shared_core.embeddings import get_embedding_provider

        self.provider = get_embedding_provider(offline=True)
        self.client = MonitoredLLMClient(store.log_request)
        self.doc_vectors = [self._embed(doc) for doc in DOCUMENTS]

    def _embed(self, text: str):
        # shared_core embedding providers are async; resolve to the vector.
        result = asyncio.run(self.provider.embed(text))
        return result.vector

    def retrieve(self, query: str, k: int = 2):
        qv = self._embed(query)
        scored = sorted(
            zip(DOCUMENTS, self.doc_vectors, strict=False),
            key=lambda pair: _cosine(qv, pair[1]),
            reverse=True,
        )
        return [doc for doc, _ in scored[:k]]

    def answer(self, query: str, model: str = "gpt-4o-mini", prompt_version="rag-v1"):
        context = "\n".join(self.retrieve(query))
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        return self.client.generate(
            model=model,
            prompt=prompt,
            mocked_response=f"(simulated answer using {len(context)} chars of context)",
            prompt_version=prompt_version,
        )


def main() -> int:
    store = InMemoryTelemetryStore()
    rag = MonitoredRAG(store)

    queries = [
        "Where is the Eiffel Tower?",
        "Who created Python?",
        "What is the tallest mountain?",
    ]
    print("--- Monitored RAG pipeline (offline embeddings + mocked LLM) ---")
    for q in queries:
        result = rag.answer(q)
        t = result["telemetry"]
        print(f"  Q: {q}")
        print(f"     cost=${t['cost_usd']:.6f}  latency={t['latency_ms']:.1f}ms")

    agg = store.get_aggregates()
    print("\nRAG telemetry summary:")
    print(f"  total_calls={agg['total_calls']}")
    print(f"  total_cost=${agg['total_cost']:.6f}")
    print(f"  cost_by_prompt_version={agg['cost_by_prompt_version']}")
    assert agg["total_calls"] == len(queries)
    print("\nwrapped_rag_app complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
