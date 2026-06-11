from fastapi import APIRouter, Response, status

from src.api.schemas import HealthResponse, ReadyResponse
from src.clients.ollama import ollama_client
from src.clients.qdrant import ping as qdrant_ping

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
async def ready(response: Response) -> ReadyResponse:
    qdrant_ok = qdrant_ping()
    ollama_ok = await ollama_client.ping_async()
    all_ok = qdrant_ok and ollama_ok

    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadyResponse(
        status="ok" if all_ok else "degraded",
        qdrant=qdrant_ok,
        ollama=ollama_ok,
    )
