import os

import chainlit as cl
import httpx

API_URL = os.getenv("API_URL", "http://app:8000")


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
    content = data["answer"]

    sources = data.get("sources", [])
    if sources:
        titles = "\n".join(f"- {s['title']}" for s in sources)
        content += f"\n\n**Sources:**\n{titles}"

    await cl.Message(content=content).send()
