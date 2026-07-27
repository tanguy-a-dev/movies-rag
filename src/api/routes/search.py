import httpx
from fastapi import APIRouter, HTTPException

from src.api.schemas import SearchRequest, SearchResponse
from src.services import rag

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest) -> SearchResponse:
    try:
        results = await rag.search(
            req.question,
            top_k=req.top_k,
            include_adult=req.include_adult,
            popular_only=req.popular_only,
            highly_rated_only=req.highly_rated_only,
        )
        return SearchResponse(question=req.question, results=results)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Upstream service unavailable",
        ) from exc
