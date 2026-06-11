import argparse

from src.clients.ollama import ollama_client
from src.clients.qdrant import client
from src.settings import settings


def search_movies(query: str, top_k: int = 5) -> None:
    query_vector = ollama_client.embed_text(query)

    results = client.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    for point in results.points:
        payload = point.payload
        if payload is None:
            continue

        print("\n---")
        print("title:", payload["title"])
        print("genres:", payload["genres"])
        overview = payload.get("overview", "")
        print("overview:", overview[:200])


def main() -> None:
    parser = argparse.ArgumentParser(description="Search movies in Qdrant")
    parser.add_argument("query", nargs="?", default="dream infiltration mind heist")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    search_movies(args.query, top_k=args.top_k)


if __name__ == "__main__":
    main()
