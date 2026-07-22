from src.services import reranking
from src.services.reranking import rerank_movies


class FakePoint:
    payload: dict | None

    def __init__(self, payload: dict | None) -> None:
        self.payload = payload


class FakeCrossEncoder:
    def __init__(self, scores: list[float]) -> None:
        self.scores = scores

    def predict(self, pairs):
        assert len(pairs) == len(self.scores)
        return self.scores


def test_rerank_orders_by_score_descending(monkeypatch):
    points = [
        FakePoint({"title": "Low match", "overview": "..."}),
        FakePoint({"title": "Best match", "overview": "..."}),
        FakePoint({"title": "Mid match", "overview": "..."}),
    ]
    monkeypatch.setattr(
        reranking, "_get_model", lambda: FakeCrossEncoder([0.1, 0.9, 0.5])
    )

    ranked = rerank_movies("query", points, top_k=3)

    assert [(p.payload or {})["title"] for p in ranked] == [
        "Best match",
        "Mid match",
        "Low match",
    ]


def test_rerank_truncates_to_top_k(monkeypatch):
    points = [FakePoint({"title": t}) for t in ["a", "b", "c"]]
    monkeypatch.setattr(
        reranking, "_get_model", lambda: FakeCrossEncoder([0.3, 0.9, 0.1])
    )

    ranked = rerank_movies("query", points, top_k=2)

    assert [(p.payload or {})["title"] for p in ranked] == ["b", "a"]


def test_rerank_empty_points_returns_empty(monkeypatch):
    monkeypatch.setattr(
        reranking, "_get_model", lambda: (_ for _ in ()).throw(AssertionError())
    )

    assert rerank_movies("query", [], top_k=5) == []
