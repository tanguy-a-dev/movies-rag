from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("src.api.routes.ask.rag.ask", new_callable=AsyncMock)
def test_ask_returns_answer_and_sources(mock_ask):
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

    response = client.post("/ask", json={"question": "sci-fi about dreams"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Try Inception."
    assert data["sources"][0]["title"] == "Inception"


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422
