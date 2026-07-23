import httpx
from fastapi import APIRouter, HTTPException

from src.api.schemas import AskRequest, AskResponse
from src.services import rag

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    try:
        result = await rag.ask(
            req.question,
            top_k=req.top_k,
            history=[turn.model_dump() for turn in req.history],
        )
        return AskResponse(**result)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Upstream service unavailable",
        ) from exc
