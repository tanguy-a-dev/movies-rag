import os
import re

import chainlit as cl
import httpx

API_URL = os.getenv("API_URL", "http://app:8000")
MAX_HISTORY_TURNS = 5

# Mirrors validation.CITED_ID_PATTERN's shape, but captures any trailing
# title text (e.g. "[id: title]") instead of the id, so it can be
# preserved when the id itself is stripped from the displayed answer.
CITATION_STRIP_PATTERN = re.compile(r"[\[\(](?:id:\s*)?\d+(?:[:\s]([^\]\)]*))?[\]\)]")


def strip_citations(text: str) -> str:
    text = CITATION_STRIP_PATTERN.sub(lambda m: m.group(1) or "", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def cache_key(question: str) -> str:
    return " ".join(question.split()).lower()


@cl.on_message
async def main(message: cl.Message) -> None:
    cache = cl.user_session.get("qa_cache")
    if cache is None:
        cache = {}
        cl.user_session.set("qa_cache", cache)

    history = cl.user_session.get("history")
    if history is None:
        history = []
        cl.user_session.set("history", history)

    key = cache_key(message.content)
    data = cache.get(key)

    if data is None:
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    f"{API_URL}/ask",
                    json={"question": message.content, "history": history},
                )
            except httpx.HTTPError:
                await cl.Message(content="Could not reach the API.").send()
                return

        if response.status_code != 200:
            detail = response.json().get("detail", "Unknown error")
            await cl.Message(content=f"API error: {detail}").send()
            return

        data = response.json()
        cache[key] = data

        history.append(
            {
                "question": message.content,
                "answer": data["answer"],
                "movie_ids": [
                    s["movie_id"] for s in data["sources"] if s.get("movie_id")
                ],
            }
        )
        del history[:-MAX_HISTORY_TURNS]

    content = strip_citations(data["answer"])

    if not data.get("validated", True):
        hallucinated_ids = data.get("hallucinated_ids", [])
        content += (
            "\n\n⚠️ This answer may reference a movie not found in our database "
            f"(ids: {', '.join(str(i) for i in hallucinated_ids)})."
        )

    await cl.Message(content=content).send()
