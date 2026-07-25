import argparse
import statistics
import time

from qdrant_client.models import (
    CreateAlias,
    CreateAliasOperation,
    Modifier,
    PointStruct,
    SparseVectorParams,
    VectorParams,
)

from src.clients import sparse_embedder
from src.clients.qdrant import client
from src.settings import settings

NEW_COLLECTION_SUFFIX = "_hybrid"


def _sparse_text(payload: dict) -> str:
    title = payload.get("title", "")
    genres = payload.get("genres", "")
    overview = payload.get("overview", "")
    return f"{title}\n{genres}\n{overview}"


def migrate(limit: int | None = None, batch_size: int | None = None) -> str:
    """Copy the existing collection into a new one with dense + sparse vectors.

    Returns the new collection's real name. Does not touch the old collection
    or any aliases -- call `swap_alias` separately once you've verified the
    new collection looks right.
    """
    batch_size = batch_size or settings.ingest_batch_size
    old_name = settings.collection_name
    new_name = f"{old_name}{NEW_COLLECTION_SUFFIX}"

    old_info = client.get_collection(old_name)
    old_vectors = old_info.config.params.vectors
    assert isinstance(old_vectors, VectorParams), (
        "expected a single unnamed dense vector on the source collection"
    )
    if client.collection_exists(new_name):
        print(f"[MIGRATE] deleting stale '{new_name}' from a previous run")
        client.delete_collection(new_name)

    client.create_collection(
        collection_name=new_name,
        vectors_config=VectorParams(
            size=old_vectors.size,
            distance=old_vectors.distance,
        ),
        sparse_vectors_config={
            settings.sparse_vector_name: SparseVectorParams(modifier=Modifier.IDF)
        },
    )
    print(f"[MIGRATE] created '{new_name}' with dense + sparse vectors")

    total = limit if limit is not None else (old_info.points_count or 0)
    migrated = 0
    durations: list[float] = []
    offset = None

    while migrated < total:
        start = time.perf_counter()
        take = min(batch_size, total - migrated)
        points, offset = client.scroll(
            collection_name=old_name,
            with_vectors=True,
            with_payload=True,
            limit=take,
            offset=offset,
        )
        if not points:
            break

        sparse_vectors = sparse_embedder.embed_documents(
            [_sparse_text(p.payload or {}) for p in points]
        )

        client.upsert(
            collection_name=new_name,
            points=[
                PointStruct(
                    id=point.id,
                    vector={"": point.vector, settings.sparse_vector_name: sparse},
                    payload=point.payload,
                )
                for point, sparse in zip(points, sparse_vectors)
            ],
        )

        elapsed = time.perf_counter() - start
        migrated += len(points)
        durations.extend([elapsed / len(points)] * len(points))
        print(
            f"migrated {migrated}/{total} (batch of {len(points)}): "
            f"{elapsed:.3f}s, median per document so far: "
            f"{statistics.median(durations):.4f}s"
        )

        if offset is None:
            break

    print(f"[MIGRATE] done: {migrated} points copied into '{new_name}'")
    return new_name


def swap_alias(new_name: str) -> None:
    old_name = settings.collection_name

    old_count = client.get_collection(old_name).points_count or 0
    new_count = client.get_collection(new_name).points_count or 0
    if new_count < old_count:
        raise RuntimeError(
            f"refusing to swap: '{new_name}' has {new_count} points, "
            f"'{old_name}' has {old_count}"
        )

    client.delete_collection(old_name)
    client.update_collection_aliases(
        change_aliases_operations=[
            CreateAliasOperation(
                create_alias=CreateAlias(collection_name=new_name, alias_name=old_name)
            )
        ]
    )
    print(f"[MIGRATE] swapped alias '{old_name}' -> '{new_name}'")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate the movies collection to dense + sparse (hybrid) vectors"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of points to migrate (default: all of them)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Points per batch (default: {settings.ingest_batch_size})",
    )
    parser.add_argument(
        "--swap",
        action="store_true",
        help="After migrating, delete the old collection and alias the "
        "original name to the new one",
    )
    args = parser.parse_args()

    new_name = migrate(limit=args.limit, batch_size=args.batch_size)
    if args.swap:
        swap_alias(new_name)
    else:
        print(
            f"[MIGRATE] not swapping (pass --swap to do so). "
            f"New collection is '{new_name}'."
        )


if __name__ == "__main__":
    main()
