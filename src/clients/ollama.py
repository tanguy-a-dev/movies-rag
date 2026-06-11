import httpx

from src.settings import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.ollama_url

    def embed_text(self, text: str) -> list[float]:
        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": settings.embedding_model, "prompt": text},
            timeout=settings.embedding_timeout,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    async def embed_text_async(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=settings.embedding_timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": settings.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]

    async def generate_async(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": settings.llm_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    async def ping_async(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.base_url)
                return response.is_success
        except httpx.HTTPError:
            return False


ollama_client = OllamaClient()
