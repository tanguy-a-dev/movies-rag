from pydantic import BaseModel, Field


class HistoryTurn(BaseModel):
    question: str
    answer: str
    movie_ids: list[int] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(None, ge=1, le=20)
    history: list[HistoryTurn] = Field(default_factory=list)


class Source(BaseModel):
    movie_id: int | None = None
    title: str
    genres: str | None = None
    overview: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    validated: bool
    hallucinated_ids: list[int] = []


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    qdrant: bool
    ollama: bool
