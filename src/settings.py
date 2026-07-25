from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    dataset_path: Path = Path("/app/data/tmdb/TMDB_movie_dataset_v11.csv")
    ollama_url: str = "http://ollama:11434"
    qdrant_url: str = "http://qdrant:6333"
    api_url: str = "http://app:8000"

    embedding_model: str = "nomic-embed-text"
    llm_model: str = "llama3.1:8b"
    llm_temperature: float = 0.2
    collection_name: str = "movies"
    vector_size: int = 768
    top_k: int = 5
    ingest_batch_size: int = 32

    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    retrieval_candidates: int = 25

    hybrid_search_enabled: bool = True
    sparse_model: str = "Qdrant/bm25"
    sparse_vector_name: str = "bm25"

    ollama_timeout: float = 120.0
    embedding_timeout: float = 30.0
    qdrant_timeout: float = 30.0


settings = Settings()
