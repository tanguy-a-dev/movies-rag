from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(None, ge=1, le=20)


class Source(BaseModel):
    title: str
    genres: str | None = None
    overview: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    qdrant: bool
    ollama: bool
