import asyncio
from collections.abc import Collection, Sequence
from typing import Protocol

from qdrant_client.models import (
    DatetimeRange,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    HasIdCondition,
    Prefetch,
    ScoredPoint,
)

from src.clients import sparse_embedder
from src.clients.qdrant import client
from src.settings import settings

METADATA_SORT_FIELDS = {"rating": "vote_average", "popularity": "popularity"}


class PointWithPayload(Protocol):
    payload: dict | None


def _date_range_condition(
    min_year: int | None, max_year: int | None
) -> FieldCondition | None:
    if min_year is None and max_year is None:
        return None
    return FieldCondition(
        key="release_date",
        range=DatetimeRange(
            gte=f"{min_year:04d}-01-01" if min_year else None,
            lte=f"{max_year:04d}-12-31" if max_year else None,
        ),
    )


def _search_sync(
    vector: list[float],
    top_k: int,
    exclude_ids: Collection[int] | None = None,
    question: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
) -> list[ScoredPoint]:
    must = []
    if date_condition := _date_range_condition(min_year, max_year):
        must.append(date_condition)
    must_not = [HasIdCondition(has_id=list(exclude_ids))] if exclude_ids else []
    query_filter = Filter(must=must, must_not=must_not) if must or must_not else None

    if settings.hybrid_search_enabled and question:
        sparse_vector = sparse_embedder.embed_query(question)
        results = client.query_points(
            collection_name=settings.collection_name,
            prefetch=[
                Prefetch(query=vector, using="", limit=top_k, filter=query_filter),
                Prefetch(
                    query=sparse_vector,
                    using=settings.sparse_vector_name,
                    limit=top_k,
                    filter=query_filter,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
            with_payload=True,
        )
    else:
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
    question: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
) -> list[ScoredPoint]:
    k = top_k or settings.top_k
    return await asyncio.to_thread(
        _search_sync, vector, k, exclude_ids, question, min_year, max_year
    )


def sort_by_metadata(
    points: Sequence[PointWithPayload], sort_by: Sequence[str]
) -> list[PointWithPayload]:
    """Sort points by rating and/or popularity, normalized so they're combined fairly.

    Ratings are 0-10 and popularity is an unbounded, much larger-scale figure, so a
    raw sum for the "both" case would just let popularity dominate -- min-max
    normalizing each field over this candidate set first keeps them comparable.
    """
    if not sort_by or not points:
        return list(points)

    fields = [METADATA_SORT_FIELDS[s] for s in sort_by if s in METADATA_SORT_FIELDS]
    if not fields:
        return list(points)

    def value(point: PointWithPayload, field: str) -> float:
        return float((point.payload or {}).get(field) or 0.0)

    if len(fields) == 1:
        field = fields[0]
        return sorted(points, key=lambda p: value(p, field), reverse=True)

    bounds = {
        field: (
            min(value(p, field) for p in points),
            max(value(p, field) for p in points),
        )
        for field in fields
    }

    def normalized(point: PointWithPayload, field: str) -> float:
        lo, hi = bounds[field]
        return (value(point, field) - lo) / (hi - lo) if hi > lo else 0.0

    def combined_score(point: PointWithPayload) -> float:
        return sum(normalized(point, field) for field in fields)

    return sorted(points, key=combined_score, reverse=True)


def build_context(points: Sequence[PointWithPayload]) -> str:
    context = []
    for i, point in enumerate(points, start=1):
        payload = point.payload or {}
        movie_id = payload.get("movie_id")
        title = payload.get("title", "Unknown")
        overview = payload.get("overview") or "No overview available."
        context.append(f"{i}. [id: {movie_id}] {title}: {overview}")
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
