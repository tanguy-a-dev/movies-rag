import argparse

from qdrant_client.models import PointStruct

from src.clients.ollama import ollama_client
from src.clients.qdrant import client
from src.dataset.document_builder import movie_to_document
from src.dataset.loader import load_movies
from src.settings import settings


def ingest(limit: int | None = None) -> None:
    n = limit or settings.ingest_limit
    df = load_movies().fillna("").head(n)

    for i, (_, row) in enumerate(df.iterrows()):
        doc = movie_to_document(row)
        vector = ollama_client.embed_text(doc.text)

        client.upsert(
            collection_name=settings.collection_name,
            points=[
                PointStruct(
                    id=doc.id,
                    vector=vector,
                    payload=doc.payload,
                )
            ],
        )

        if i % 50 == 0:
            print("ingested:", i)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest movies into Qdrant")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=f"Number of movies to ingest (default: {settings.ingest_limit})",
    )
    args = parser.parse_args()
    ingest(limit=args.limit)


if __name__ == "__main__":
    main()
