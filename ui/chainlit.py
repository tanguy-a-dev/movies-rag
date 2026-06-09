import chainlit as cl
import requests

API_URL = "http://app:8000/ask"


@cl.on_message
async def main(message: cl.Message):
    response = requests.post(
        API_URL,
        json={"question": message.content},
        timeout=120,
    )

    if response.status_code != 200:
        await cl.Message(content="Error calling API").send()
        return

    answer = response.json()["answer"]

    await cl.Message(content=answer).send()