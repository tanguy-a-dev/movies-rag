from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import ask, health

app = FastAPI(title="MoviesRAG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # The React frontend (web/) calls this API directly from the browser, so its
    # origin needs CORS: Vite's dev server (default port) and `vite preview`.
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ask.router)
