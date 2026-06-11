from fastapi import FastAPI

from src.api.routes import ask, health

app = FastAPI(title="MoviesRAG", version="0.1.0")

app.include_router(health.router)
app.include_router(ask.router)
