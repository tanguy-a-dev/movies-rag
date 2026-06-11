from src.clients.ollama import ollama_client
from src.services.generation import generate_answer
from src.services.retrieval import build_context, extract_sources, search_movies


async def ask(question: str, top_k: int | None = None) -> dict:
    vector = await ollama_client.embed_text_async(question)
    matches = await search_movies(vector, top_k=top_k)
    context = build_context(matches)
    answer = await generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "sources": extract_sources(matches),
    }
