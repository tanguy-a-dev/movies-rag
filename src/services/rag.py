import asyncio

from src.clients.ollama import ollama_client
from src.services.generation import generate_answer
from src.services.reranking import rerank_movies
from src.services.retrieval import build_context, extract_sources, search_movies
from src.services.validation import validate_answer
from src.settings import settings


async def ask(
    question: str,
    top_k: int | None = None,
    history: list[dict] | None = None,
) -> dict:
    history = history or []
    exclude_ids = {
        movie_id for turn in history for movie_id in turn.get("movie_ids", [])
    }

    k = top_k or settings.top_k
    vector = await ollama_client.embed_text_async(question)

    if settings.rerank_enabled:
        candidates = await search_movies(
            vector,
            top_k=max(settings.retrieval_candidates, k),
            exclude_ids=exclude_ids,
        )
        matches = await asyncio.to_thread(rerank_movies, question, candidates, k)
    else:
        matches = await search_movies(vector, top_k=k, exclude_ids=exclude_ids)

    context = build_context(matches)
    answer = await generate_answer(question, context, history=history)
    validation = validate_answer(answer, matches)

    return {
        "question": question,
        "answer": answer,
        "sources": extract_sources(matches),
        "validated": validation["valid"],
        "hallucinated_ids": validation["hallucinated_ids"],
    }
