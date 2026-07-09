import argparse
import statistics
import time

from qdrant_client.models import PointStruct

from src.clients.ollama import ollama_client
from src.clients.qdrant import client
from src.dataset.document_builder import movie_to_document
from src.dataset.loader import load_movies
from src.settings import settings


def ingest(limit: int | None = None) -> None:
    n = limit or settings.ingest_limit

    load_start = time.perf_counter()
    df = load_movies().fillna("").head(n)
    print(f"loaded {len(df)} rows in {time.perf_counter() - load_start:.3f}s")

    durations: list[float] = []
    build_durations: list[float] = []
    embed_durations: list[float] = []
    upsert_durations: list[float] = []

    for i, (_, row) in enumerate(df.iterrows()):
        start = time.perf_counter()

        build_start = time.perf_counter()
        doc = movie_to_document(row)
        build_elapsed = time.perf_counter() - build_start

        embed_start = time.perf_counter()
        vector = ollama_client.embed_text(doc.text)
        embed_elapsed = time.perf_counter() - embed_start

        upsert_start = time.perf_counter()
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
        upsert_elapsed = time.perf_counter() - upsert_start

        elapsed = time.perf_counter() - start
        durations.append(elapsed)
        build_durations.append(build_elapsed)
        embed_durations.append(embed_elapsed)
        upsert_durations.append(upsert_elapsed)

        print(
            f"ingested {i}: total={elapsed:.3f}s "
            f"build={build_elapsed:.3f}s embed={embed_elapsed:.3f}s upsert={upsert_elapsed:.3f}s"
        )

        if i % 50 == 0:
            print("ingested:", i)
            print(
                f"median so far: total={statistics.median(durations):.3f}s "
                f"build={statistics.median(build_durations):.3f}s "
                f"embed={statistics.median(embed_durations):.3f}s "
                f"upsert={statistics.median(upsert_durations):.3f}s"
            )

    if durations:
        print(
            f"Final median per document: total={statistics.median(durations):.3f}s "
            f"build={statistics.median(build_durations):.3f}s "
            f"embed={statistics.median(embed_durations):.3f}s "
            f"upsert={statistics.median(upsert_durations):.3f}s"
        )


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
