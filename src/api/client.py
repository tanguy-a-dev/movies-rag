import requests
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from src.embeddings.httpEmbedding import embedText

from src.settings import OLLAMA_URL, QDRANT_URL

app = FastAPI()

qdrant = QdrantClient(url=QDRANT_URL)


class AskRequest(BaseModel):
    question: str


def search_qdrant(vector, top_k=5):
    results = qdrant.query_points(
        collection_name="movies",
        query=vector,
        limit=top_k,
        with_payload=True,
    )
    return results.points


def build_context(points):
    context = []
    for p in points:
        payload = p.payload
        context.append(f"{payload.get('title')}: {payload.get('overview')}")
    return "\n\n".join(context)


def generate_answer(question, context):
    prompt = f"""
You are a movie recommendation system.

Use ONLY the context below.

Context:
{context}

User question:
{question}

Answer:
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
        },
    )

    response.raise_for_status()
    return response.json()["response"]


@app.post("/ask")
def ask(req: AskRequest):
    vector = embedText(req.question)
    matches = search_qdrant(vector)
    context = build_context(matches)
    answer = generate_answer(req.question, context)

    return {
        "question": req.question,
        "answer": answer,
    }
