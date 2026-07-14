import os
import re

import chainlit as cl
import httpx

API_URL = os.getenv("API_URL", "http://app:8000")
CITATION_PATTERN = re.compile(r"\[id:\s*\d+\]")


def strip_citations(text: str) -> str:
    text = CITATION_PATTERN.sub("", text)
    return re.sub(r"[ \t]{2,}", " ", text)


@cl.on_message
async def main(message: cl.Message) -> None:
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            response = await client.post(
                f"{API_URL}/ask",
                json={"question": message.content},
            )
        except httpx.HTTPError:
            await cl.Message(content="Could not reach the API.").send()
            return

    if response.status_code != 200:
        detail = response.json().get("detail", "Unknown error")
        await cl.Message(content=f"API error: {detail}").send()
        return

    data = response.json()
    content = strip_citations(data["answer"])

    if not data.get("validated", True):
        hallucinated_ids = data.get("hallucinated_ids", [])
        content += (
            "\n\n⚠️ This answer may reference a movie not found in our database "
            f"(ids: {', '.join(str(i) for i in hallucinated_ids)})."
        )

    await cl.Message(content=content).send()
