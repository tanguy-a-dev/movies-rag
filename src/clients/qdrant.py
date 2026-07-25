from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Modifier,
    PayloadSchemaType,
    SparseVectorParams,
    VectorParams,
)

from src.settings import settings


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, timeout=settings.qdrant_timeout)


client = get_client()


def _sparse_vectors_config() -> dict[str, SparseVectorParams]:
    return {settings.sparse_vector_name: SparseVectorParams(modifier=Modifier.IDF)}


def ensure_collection(vector_size: int | None = None) -> None:
    size = vector_size or settings.vector_size
    if not client.collection_exists(settings.collection_name):
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
            sparse_vectors_config=_sparse_vectors_config(),
        )
        print(f"[QDRANT] collection '{settings.collection_name}' created")
    else:
        print(f"[QDRANT] collection '{settings.collection_name}' already exists")
        info = client.get_collection(settings.collection_name)
        has_sparse = (
            info.config.params.sparse_vectors
            and settings.sparse_vector_name in info.config.params.sparse_vectors
        )
        if not has_sparse:
            # Qdrant cannot add a new named vector to an already-created collection
            # (only tune params of ones that already exist) -- a populated
            # collection missing sparse vectors needs a full reindex, not an
            # in-place update.
            print(
                f"[QDRANT] collection '{settings.collection_name}' has no "
                f"'{settings.sparse_vector_name}' sparse vector and can't be "
                "updated in place. Run `python -m scripts.migrate_to_hybrid "
                "--swap` instead."
            )

    # payload indexes CAN be added to an existing collection at any time, unlike
    # vector configs -- this speeds up the release_date range filter used for
    # "movies from the 90s"-style queries.
    client.create_payload_index(
        collection_name=settings.collection_name,
        field_name="release_date",
        field_schema=PayloadSchemaType.DATETIME,
    )


def ping() -> bool:
    try:
        client.get_collections()
        return True
    except Exception:
        return False


def get_existing_ids(collection_name: str | None = None) -> set[int]:
    name = collection_name or settings.collection_name
    if not client.collection_exists(name):
        return set()

    ids: set[int] = set()
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=name,
            with_payload=False,
            with_vectors=False,
            limit=10000,
            offset=offset,
        )
        ids.update(int(point.id) for point in points)
        if offset is None:
            break
    return ids
