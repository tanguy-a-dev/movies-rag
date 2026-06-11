from src.clients.ollama import ollama_client

PROMPT_TEMPLATE = """You are a movie recommendation system.

Use ONLY the context below.

Context:
{context}

User question:
{question}

Answer:
"""


async def generate_answer(question: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    return await ollama_client.generate_async(prompt)
