from src.services.retrieval import build_context, extract_sources


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
            "title": "Inception",
            "genres": "Action, Sci-Fi",
            "overview": "Dream heist.",
        }
    ]
