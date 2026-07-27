import asyncio

from src.clients.ollama import ollama_client
from src.services.generation import generate_answer
from src.services.query_intent import parse_intent
from src.services.reranking import rerank_movies
from src.services.retrieval import (
    build_context,
    extract_sources,
    search_movies,
    sort_by_metadata,
)
from src.services.validation import validate_answer
from src.settings import settings


async def _retrieve_matches(
    question: str,
    top_k: int | None = None,
    history: list[dict] | None = None,
    include_adult: bool = False,
    popular_only: bool = False,
    highly_rated_only: bool = False,
) -> list:
    history = history or []
    exclude_ids = {
        movie_id for turn in history for movie_id in turn.get("movie_ids", [])
    }

    intent = parse_intent(question)
    k = top_k or settings.top_k
    pool_k = settings.metadata_rerank_pool if intent.sort_by else k
    vector = await ollama_client.embed_text_async(question)

    if settings.rerank_enabled:
        candidates = await search_movies(
            vector,
            top_k=max(settings.retrieval_candidates, pool_k),
            exclude_ids=exclude_ids,
            question=question,
            min_year=intent.min_year,
            max_year=intent.max_year,
            include_adult=include_adult,
            popular_only=popular_only,
            highly_rated_only=highly_rated_only,
        )
        c = extract_sources(candidates)
        c = [candidate["title"] for candidate in c]
        print(f"candidates: {c}")
        matches = await asyncio.to_thread(rerank_movies, question, candidates, pool_k)
        m = extract_sources(matches)
        m = [match["title"] for match in m]
        print(f"matches: {m}")
    else:
        matches = await search_movies(
            vector,
            top_k=pool_k,
            exclude_ids=exclude_ids,
            question=question,
            min_year=intent.min_year,
            max_year=intent.max_year,
            include_adult=include_adult,
            popular_only=popular_only,
            highly_rated_only=highly_rated_only,
        )

    if intent.sort_by:
        matches = sort_by_metadata(matches, intent.sort_by)[:k]

    return matches


async def ask(
    question: str,
    top_k: int | None = None,
    history: list[dict] | None = None,
    include_adult: bool = False,
    popular_only: bool = False,
    highly_rated_only: bool = False,
) -> dict:
    matches = await _retrieve_matches(
        question,
        top_k,
        history,
        include_adult,
        popular_only=popular_only,
        highly_rated_only=highly_rated_only,
    )

    context = build_context(matches)
    answer = await generate_answer(
        question, context, movie_count=len(matches), history=history
    )
    validation = validate_answer(answer, matches)

    return {
        "question": question,
        "answer": answer,
        "sources": extract_sources(matches),
        "validated": validation["valid"],
        "hallucinated_ids": validation["hallucinated_ids"],
    }


async def search(
    question: str,
    top_k: int | None = None,
    include_adult: bool = False,
    popular_only: bool = False,
    highly_rated_only: bool = False,
) -> list[dict]:
    """Retrieval-only path: no LLM generation, just the ranked movie list."""
    matches = await _retrieve_matches(
        question,
        top_k,
        include_adult=include_adult,
        popular_only=popular_only,
        highly_rated_only=highly_rated_only,
    )
    return extract_sources(matches)
