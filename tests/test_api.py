from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@patch("src.api.routes.ask.rag.ask", new_callable=AsyncMock)
async def test_ask_returns_answer_and_sources(mock_ask):
    mock_ask.return_value = {
        "question": "sci-fi about dreams",
        "answer": "Try Inception.",
        "sources": [
            {
                "movie_id": 1,
                "title": "Inception",
                "genres": "Action, Sci-Fi",
                "overview": "A dream heist.",
            }
        ],
        "validated": True,
        "hallucinated_ids": [],
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/ask", json={"question": "sci-fi about dreams"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Try Inception."
    assert data["sources"][0]["title"] == "Inception"


@pytest.mark.asyncio
@patch("src.api.routes.ask.rag.ask", new_callable=AsyncMock)
async def test_ask_passes_popular_only_and_highly_rated_only_to_rag(mock_ask):
    mock_ask.return_value = {
        "question": "sci-fi about dreams",
        "answer": "Try Inception.",
        "sources": [],
        "validated": True,
        "hallucinated_ids": [],
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/ask",
            json={
                "question": "sci-fi about dreams",
                "popular_only": True,
                "highly_rated_only": True,
            },
        )

    assert response.status_code == 200
    assert mock_ask.call_args.kwargs["popular_only"] is True
    assert mock_ask.call_args.kwargs["highly_rated_only"] is True


@pytest.mark.asyncio
async def test_ask_rejects_empty_question():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/ask", json={"question": ""})

    assert response.status_code == 422


@pytest.mark.asyncio
@patch("src.api.routes.search.rag.search", new_callable=AsyncMock)
async def test_search_returns_results_without_answer(mock_search):
    mock_search.return_value = [
        {
            "movie_id": 1,
            "title": "Inception",
            "genres": "Action, Sci-Fi",
            "overview": "A dream heist.",
            "poster_url": "https://image.tmdb.org/t/p/w342/inception.jpg",
            "vote_average": 8.8,
            "popularity": 100.0,
            "release_date": "2010-07-16",
        }
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/search", json={"question": "sci-fi about dreams"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" not in data
    assert data["results"][0]["title"] == "Inception"
    assert data["results"][0]["poster_url"] == (
        "https://image.tmdb.org/t/p/w342/inception.jpg"
    )


@pytest.mark.asyncio
@patch("src.api.routes.search.rag.search", new_callable=AsyncMock)
async def test_search_passes_popular_only_to_rag(mock_search):
    mock_search.return_value = []

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/search",
            json={"question": "sci-fi about dreams", "popular_only": True},
        )

    assert response.status_code == 200
    assert mock_search.call_args.kwargs["popular_only"] is True


@pytest.mark.asyncio
@patch("src.api.routes.search.rag.search", new_callable=AsyncMock)
async def test_search_passes_highly_rated_only_to_rag(mock_search):
    mock_search.return_value = []

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/search",
            json={"question": "sci-fi about dreams", "highly_rated_only": True},
        )

    assert response.status_code == 200
    assert mock_search.call_args.kwargs["highly_rated_only"] is True


@pytest.mark.asyncio
async def test_search_rejects_empty_question():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/search", json={"question": ""})

    assert response.status_code == 422
