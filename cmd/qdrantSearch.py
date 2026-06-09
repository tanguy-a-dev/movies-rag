from qdrant_client import QdrantClient
from qdrant_client.models import SearchRequest
from src.embeddings.httpEmbedding import embedText

client = QdrantClient(url="http://qdrant:6333")


def search_movies(query: str, top_k: int = 5):
    query_vector = embedText(query)

    results = client.query_points(
        collection_name="movies",
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    for r in results.points:
        print("\n---")
        print("title:", r.payload["title"])
        print("genres:", r.payload["genres"])
        print("overview:", r.payload["overview"][:200])


if __name__ == "__main__":
    search_movies("dream infiltration mind heist")