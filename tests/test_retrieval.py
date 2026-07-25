from unittest.mock import patch

from qdrant_client.models import Fusion, FusionQuery, SparseVector

from src.services.retrieval import (
    _search_sync,
    build_context,
    extract_sources,
    sort_by_metadata,
)


class FakePoint:
    payload: dict | None

    def __init__(self, payload: dict | None) -> None:
        self.payload = payload


def test_build_context_joins_titles_and_overviews():
    points = [
        FakePoint({"title": "Inception", "overview": "Dream heist."}),
        FakePoint({"title": "The Matrix", "overview": "Simulated reality."}),
    ]

    context = build_context(points)

    assert "Inception: Dream heist." in context
    assert "The Matrix: Simulated reality." in context


def test_build_context_numbers_entries_and_falls_back_for_missing_overview():
    points = [
        FakePoint({"title": "Inception", "overview": "Dream heist."}),
        FakePoint({"title": "No Overview Movie", "overview": ""}),
    ]

    context = build_context(points)

    assert "1. [id: None] Inception: Dream heist." in context
    assert "2. [id: None] No Overview Movie: No overview available." in context


def test_extract_sources_returns_structured_payload():
    points = [
        FakePoint(
            {
                "title": "Inception",
                "genres": "Action, Sci-Fi",
                "overview": "Dream heist.",
            }
        )
    ]

    sources = extract_sources(points)

    assert sources == [
        {
            "movie_id": None,
            "title": "Inception",
            "genres": "Action, Sci-Fi",
            "overview": "Dream heist.",
        }
    ]


def test_search_sync_uses_hybrid_prefetch_when_question_given():
    with (
        patch("src.services.retrieval.settings") as mock_settings,
        patch("src.services.retrieval.client") as mock_client,
        patch("src.services.retrieval.sparse_embedder") as mock_sparse,
    ):
        mock_settings.hybrid_search_enabled = True
        mock_settings.collection_name = "movies"
        mock_settings.sparse_vector_name = "bm25"
        mock_sparse.embed_query.return_value = SparseVector(indices=[1], values=[1.0])
        mock_client.query_points.return_value.points = []

        _search_sync([0.1, 0.2], top_k=5, question="Avatar")

        _, kwargs = mock_client.query_points.call_args
        assert len(kwargs["prefetch"]) == 2
        assert kwargs["prefetch"][0].using == ""
        assert kwargs["prefetch"][1].using == "bm25"
        assert kwargs["query"] == FusionQuery(fusion=Fusion.RRF)


def test_search_sync_falls_back_to_dense_only_without_question():
    with (
        patch("src.services.retrieval.settings") as mock_settings,
        patch("src.services.retrieval.client") as mock_client,
    ):
        mock_settings.hybrid_search_enabled = True
        mock_settings.collection_name = "movies"
        mock_client.query_points.return_value.points = []

        _search_sync([0.1, 0.2], top_k=5, question=None)

        _, kwargs = mock_client.query_points.call_args
        assert "prefetch" not in kwargs
        assert kwargs["query"] == [0.1, 0.2]


def test_sort_by_metadata_no_sort_keeps_original_order():
    points = [
        FakePoint({"title": "A", "vote_average": 5.0, "popularity": 100.0}),
        FakePoint({"title": "B", "vote_average": 9.0, "popularity": 10.0}),
    ]

    result = sort_by_metadata(points, [])

    assert [(p.payload or {})["title"] for p in result] == ["A", "B"]


def test_sort_by_metadata_rating_only():
    points = [
        FakePoint({"title": "Low rated", "vote_average": 4.0, "popularity": 500.0}),
        FakePoint({"title": "High rated", "vote_average": 9.0, "popularity": 10.0}),
    ]

    result = sort_by_metadata(points, ["rating"])

    assert [(p.payload or {})["title"] for p in result] == ["High rated", "Low rated"]


def test_sort_by_metadata_popularity_only():
    points = [
        FakePoint({"title": "Low pop", "vote_average": 9.0, "popularity": 10.0}),
        FakePoint({"title": "High pop", "vote_average": 4.0, "popularity": 500.0}),
    ]

    result = sort_by_metadata(points, ["popularity"])

    assert [(p.payload or {})["title"] for p in result] == ["High pop", "Low pop"]


def test_sort_by_metadata_combined_normalizes_scales():
    # popularity is on a much larger scale than rating; without min-max
    # normalization it would dominate the combined score regardless of rating
    points = [
        FakePoint(
            {"title": "High pop only", "vote_average": 1.0, "popularity": 1000.0}
        ),
        FakePoint({"title": "Balanced", "vote_average": 9.0, "popularity": 900.0}),
        FakePoint({"title": "Low both", "vote_average": 5.0, "popularity": 500.0}),
    ]

    result = sort_by_metadata(points, ["rating", "popularity"])

    assert [(p.payload or {})["title"] for p in result] == [
        "Balanced",
        "High pop only",
        "Low both",
    ]
