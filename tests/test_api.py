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
                "title": "Inception",
                "genres": "Action, Sci-Fi",
                "overview": "A dream heist.",
            }
        ],
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
async def test_ask_rejects_empty_question():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/ask", json={"question": ""})

    assert response.status_code == 422
