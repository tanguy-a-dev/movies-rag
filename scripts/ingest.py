import argparse
import statistics
import time

from qdrant_client.models import PointStruct

from src.clients.ollama import ollama_client
from src.clients.qdrant import client
from src.dataset.document_builder import movie_to_document
from src.dataset.loader import load_movies
from src.settings import settings


def ingest(limit: int | None = None, batch_size: int | None = None) -> None:
    n = limit or settings.ingest_limit
    batch_size = batch_size or settings.ingest_batch_size

    load_start = time.perf_counter()
    df = load_movies().fillna("").head(n)
    print(f"loaded {len(df)} rows in {time.perf_counter() - load_start:.3f}s")

    durations: list[float] = []
    build_durations: list[float] = []
    embed_durations: list[float] = []
    upsert_durations: list[float] = []

    ingested = 0
    for batch_start in range(0, len(df), batch_size):
        batch_df = df.iloc[batch_start : batch_start + batch_size]
        start = time.perf_counter()

        build_start = time.perf_counter()
        docs = [movie_to_document(row) for _, row in batch_df.iterrows()]
        build_elapsed = time.perf_counter() - build_start

        embed_start = time.perf_counter()
        vectors = ollama_client.embed_texts([doc.text for doc in docs])
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
                for doc, vector in zip(docs, vectors)
            ],
        )
        upsert_elapsed = time.perf_counter() - upsert_start

        elapsed = time.perf_counter() - start
        ingested += len(docs)

        # amortize batch timings per document so medians stay comparable across batch sizes
        durations.extend([elapsed / len(docs)] * len(docs))
        build_durations.extend([build_elapsed / len(docs)] * len(docs))
        embed_durations.extend([embed_elapsed / len(docs)] * len(docs))
        upsert_durations.extend([upsert_elapsed / len(docs)] * len(docs))

        print(
            f"ingested {ingested}/{len(df)} (batch of {len(docs)}): "
            f"total={elapsed:.3f}s build={build_elapsed:.3f}s "
            f"embed={embed_elapsed:.3f}s upsert={upsert_elapsed:.3f}s"
        )
        print(
            f"median per document so far: total={statistics.median(durations):.3f}s "
            f"build={statistics.median(build_durations):.3f}s "
            f"embed={statistics.median(embed_durations):.3f}s "
            f"upsert={statistics.median(upsert_durations):.3f}s"
        )

    if durations:
        print(f"ingested: {ingested}")
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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Number of documents per embed/upsert batch (default: {settings.ingest_batch_size})",
    )
    args = parser.parse_args()
    ingest(limit=args.limit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
