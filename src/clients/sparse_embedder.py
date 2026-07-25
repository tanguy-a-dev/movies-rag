from functools import lru_cache

from fastembed import SparseTextEmbedding
from qdrant_client.models import SparseVector

from src.settings import settings


@lru_cache(maxsize=1)
def _get_model() -> SparseTextEmbedding:
    return SparseTextEmbedding(model_name=settings.sparse_model)


def embed_documents(texts: list[str]) -> list[SparseVector]:
    model = _get_model()
    return [
        SparseVector(indices=e.indices.tolist(), values=e.values.tolist())
        for e in model.embed(texts)
    ]


def embed_query(text: str) -> SparseVector:
    model = _get_model()
    embedding = next(iter(model.query_embed([text])))
    return SparseVector(
        indices=embedding.indices.tolist(),
        values=embedding.values.tolist(),
    )
