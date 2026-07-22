from collections.abc import Sequence
from functools import lru_cache
from typing import Protocol

from src.settings import settings


class PointWithPayload(Protocol):
    payload: dict | None


class CrossEncoderModel(Protocol):
    def predict(self, pairs: Sequence[tuple[str, str]]) -> Sequence[float]: ...


@lru_cache(maxsize=1)
def _get_model() -> CrossEncoderModel:
    from sentence_transformers import CrossEncoder

    return CrossEncoder(settings.rerank_model)


def _candidate_text(point: PointWithPayload) -> str:
    payload = point.payload or {}
    title = payload.get("title", "")
    overview = payload.get("overview", "")
    return f"{title}: {overview}"


def rerank_movies(
    query: str,
    points: Sequence[PointWithPayload],
    top_k: int,
) -> list[PointWithPayload]:
    if not points:
        return []

    model = _get_model()
    pairs = [(query, _candidate_text(point)) for point in points]
    scores = model.predict(pairs)
    ranked = sorted(zip(points, scores), key=lambda pair: pair[1], reverse=True)
    return [point for point, _ in ranked[:top_k]]
