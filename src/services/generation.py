from src.clients.ollama import ollama_client

PROMPT_TEMPLATE = """You are a movie recommendation system.

Rules:
1. Recommend every movie listed in the context below, in the same order, \
and nothing else. Never mention a movie that is not in the context.
2. Output only a markdown list, one line per movie, in exactly this format: \
"- **Title** [id: X]: one sentence on why it fits the question."
3. Do not add an introduction, summary, or closing remark. Output the list \
and nothing else.

Example:

Context:
[id: 27205] Inception: A thief who steals corporate secrets through \
dream-sharing technology.
[id: 603] The Matrix: A hacker discovers reality is a simulation and joins \
a rebellion.

User question:
Suggest a mind-bending sci-fi movie

Answer:
- **Inception** [id: 27205]: A dream-heist thriller built around layered, \
mind-bending reality.
- **The Matrix** [id: 603]: A reality-questioning sci-fi classic about \
breaking free of a simulation.

Now do the same for the following context and question.

Context:
{context}

User question:
{question}

Answer:
"""


async def generate_answer(question: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    return await ollama_client.generate_async(prompt)
