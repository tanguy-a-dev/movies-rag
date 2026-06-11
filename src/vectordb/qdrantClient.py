from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(url="http://qdrant:6333")


def createCollection(vector_size: int = 768):
    client.recreate_collection(
        collection_name="movies",
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    print("[QDRANT] collection 'movies' ready")