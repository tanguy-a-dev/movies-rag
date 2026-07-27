import argparse
import statistics
import time

from qdrant_client.models import SetPayload, SetPayloadOperation

from src.clients.qdrant import client, get_existing_ids
from src.dataset.loader import load_movies
from src.settings import settings

DEFAULT_BATCH_SIZE = 2000


def backfill(limit: int | None = None, batch_size: int | None = None) -> None:
    batch_size = batch_size or DEFAULT_BATCH_SIZE

    load_start = time.perf_counter()
    df = load_movies().fillna("")
    print(f"loaded {len(df)} rows in {time.perf_counter() - load_start:.3f}s")

    existing_ids_start = time.perf_counter()
    existing_ids = get_existing_ids()
    print(
        f"{len(existing_ids)} documents already in Qdrant "
        f"(fetched in {time.perf_counter() - existing_ids_start:.3f}s)"
    )

    df = df[df["id"].isin(existing_ids)]
    if limit is None:
        print(f"{len(df)} rows to backfill, no limit")
    else:
        print(f"{len(df)} rows to backfill, taking up to {limit}")
        df = df.head(limit)

    durations: list[float] = []
    backfilled = 0
    for batch_start in range(0, len(df), batch_size):
        batch_df = df.iloc[batch_start : batch_start + batch_size]
        start = time.perf_counter()

        operations = [
            SetPayloadOperation(
                set_payload=SetPayload(
                    payload={"poster_path": row["poster_path"] or None},
                    points=[int(row["id"])],
                )
            )
            for _, row in batch_df.iterrows()
        ]
        client.batch_update_points(
            collection_name=settings.collection_name,
            update_operations=operations,
        )

        elapsed = time.perf_counter() - start
        backfilled += len(batch_df)
        durations.extend([elapsed / len(batch_df)] * len(batch_df))

        print(
            f"backfilled {backfilled}/{len(df)} (batch of {len(batch_df)}): "
            f"{elapsed:.3f}s, median per document so far: "
            f"{statistics.median(durations):.4f}s"
        )

    if durations:
        print(f"backfilled: {backfilled}")
        print(f"Final median per document: {statistics.median(durations):.4f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill poster_path onto existing Qdrant points (payload-only, "
        "no vector changes)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of existing movies to backfill (default: no limit, all of them)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Points per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    args = parser.parse_args()
    backfill(limit=args.limit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
