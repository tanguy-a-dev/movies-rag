import requests

OLLAMA_URL = "http://ollama:11434"


def embedText(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]