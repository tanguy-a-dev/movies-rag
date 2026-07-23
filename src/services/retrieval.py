import asyncio
from collections.abc import Collection, Sequence
from typing import Protocol

from qdrant_client.models import Filter, HasIdCondition, ScoredPoint

from src.clients.qdrant import client
from src.settings import settings


class PointWithPayload(Protocol):
    payload: dict | None


def _search_sync(
    vector: list[float],
    top_k: int,
    exclude_ids: Collection[int] | None = None,
) -> list[ScoredPoint]:
    query_filter = None
    if exclude_ids:
        query_filter = Filter(must_not=[HasIdCondition(has_id=list(exclude_ids))])

    results = client.query_points(
        collection_name=settings.collection_name,
        query=vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )
    return results.points


async def search_movies(
    vector: list[float],
    top_k: int | None = None,
    exclude_ids: Collection[int] | None = None,
) -> list[ScoredPoint]:
    k = top_k or settings.top_k
    return await asyncio.to_thread(_search_sync, vector, k, exclude_ids)


def build_context(points: Sequence[PointWithPayload]) -> str:
    context = []
    for point in points:
        payload = point.payload or {}
        movie_id = payload.get("movie_id")
        title = payload.get("title", "Unknown")
        overview = payload.get("overview", "")
        context.append(f"[id: {movie_id}] {title}: {overview}")
    return "\n\n".join(context)


def extract_sources(points: Sequence[PointWithPayload]) -> list[dict]:
    sources = []
    for point in points:
        payload = point.payload or {}
        sources.append(
            {
                "movie_id": payload.get("movie_id"),
                "title": payload.get("title", "Unknown"),
                "genres": payload.get("genres"),
                "overview": payload.get("overview"),
            }
        )
    return sources
