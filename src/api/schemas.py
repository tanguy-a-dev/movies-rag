from pydantic import BaseModel, Field


class HistoryTurn(BaseModel):
    question: str
    answer: str
    movie_ids: list[int] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(None, ge=1, le=20)
    history: list[HistoryTurn] = Field(default_factory=list)
    include_adult: bool = False
    popular_only: bool = False
    highly_rated_only: bool = False


class Source(BaseModel):
    movie_id: int | None = None
    title: str
    genres: str | None = None
    overview: str | None = None
    poster_url: str | None = None
    vote_average: float | None = None
    popularity: float | None = None
    release_date: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    validated: bool
    hallucinated_ids: list[int] = []


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(None, ge=1, le=42)
    include_adult: bool = False
    popular_only: bool = False
    highly_rated_only: bool = False


class SearchResponse(BaseModel):
    question: str
    results: list[Source]


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    qdrant: bool
    ollama: bool
