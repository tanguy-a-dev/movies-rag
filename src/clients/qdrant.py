from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.settings import settings


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


client = get_client()


def ensure_collection(vector_size: int | None = None) -> None:
    size = vector_size or settings.vector_size
    if client.collection_exists(settings.collection_name):
        print(f"[QDRANT] collection '{settings.collection_name}' already exists")
        return

    client.create_collection(
        collection_name=settings.collection_name,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )
    print(f"[QDRANT] collection '{settings.collection_name}' created")


def ping() -> bool:
    try:
        client.get_collections()
        return True
    except Exception:
        return False
