import argparse
import asyncio
import json
import statistics
import time
from pathlib import Path

from src.services import rag
from src.services.validation import extract_cited_ids

DEFAULT_QUESTIONS_PATH = Path(__file__).resolve().\
    parent.parent / "evals" / "questions.json"


def load_questions(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def retrieval_relevance(sources: list[dict], expected_genres: list[str]) -> float:
    if not sources:
        return 0.0
    matching = 0
    for source in sources:
        genres = source.get("genres") or ""
        if any(expected in genres for expected in expected_genres):
            matching += 1
    return matching / len(sources)


async def eval_question(question: dict) -> dict:
    start = time.perf_counter()
    result = await rag.ask(question["question"])
    elapsed = time.perf_counter() - start

    cited_ids = extract_cited_ids(result["answer"])
    relevance = retrieval_relevance(result["sources"], question["expected_genres"])

    return {
        "question": question["question"],
        "elapsed": elapsed,
        "validated": result["validated"],
        "hallucinated_ids": result["hallucinated_ids"],
        "cited": bool(cited_ids),
        "relevance": relevance,
    }


async def run_eval(questions_path: Path) -> None:
    questions = load_questions(questions_path)
    print(f"running {len(questions)} eval questions\n")

    results = []
    for question in questions:
        r = await eval_question(question)
        results.append(r)
        status = "OK" if r["validated"] else "HALLUCINATION"
        cited = "cited" if r["cited"] else "NO CITATION"
        print(
            f"[{status}] [{cited}] relevance={r['relevance']:.2f} "
            f"elapsed={r['elapsed']:.2f}s :: {r['question']}"
        )
        if not r["validated"]:
            print(f"  hallucinated_ids={r['hallucinated_ids']}")

    n = len(results)
    hallucination_rate = sum(1 for r in results if not r["validated"]) / n
    citation_coverage = sum(1 for r in results if r["cited"]) / n
    avg_relevance = statistics.mean(r["relevance"] for r in results)
    median_latency = statistics.median(r["elapsed"] for r in results)

    print("\n--- summary ---")
    print(f"questions:            {n}")
    print(f"hallucination rate:   {hallucination_rate:.1%}")
    print(f"citation coverage:    {citation_coverage:.1%}")
    print(f"avg retrieval relevance: {avg_relevance:.1%}")
    print(f"median latency:       {median_latency:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAG pipeline evals")
    parser.add_argument(
        "--questions",
        type=Path,
        default=DEFAULT_QUESTIONS_PATH,
        help=f"Path to questions JSON file (default: {DEFAULT_QUESTIONS_PATH})",
    )
    args = parser.parse_args()
    asyncio.run(run_eval(args.questions))


if __name__ == "__main__":
    main()
