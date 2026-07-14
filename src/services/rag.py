from src.clients.ollama import ollama_client
from src.services.generation import generate_answer
from src.services.retrieval import build_context, extract_sources, search_movies
from src.services.validation import validate_answer


async def ask(question: str, top_k: int | None = None) -> dict:
    vector = await ollama_client.embed_text_async(question)
    matches = await search_movies(vector, top_k=top_k)
    context = build_context(matches)
    answer = await generate_answer(question, context)
    validation = validate_answer(answer, matches)

    return {
        "question": question,
        "answer": answer,
        "sources": extract_sources(matches),
        "validated": validation["valid"],
        "hallucinated_ids": validation["hallucinated_ids"],
    }
