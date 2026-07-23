from collections.abc import Sequence

from src.clients.ollama import ollama_client

PROMPT_TEMPLATE = """You are a movie recommendation system.

Rules:
1. Recommend every movie listed in the context below, in the same order, \
and nothing else. Never mention a movie that is not in the context.
2. Output only a markdown list, one line per movie, in exactly this format: \
"- **Title** [id: X]: one sentence on why it fits the question."
3. Do not add an introduction, summary, or closing remark. Output the list \
and nothing else.
4. If conversation history is given below, it shows what you already \
recommended earlier in this chat. The context has already been narrowed to \
exclude those movies, so just answer the new question the same way \
(the exclusion is already handled for you).

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
{history}
Context:
{context}

User question:
{question}

Answer:
"""


def _format_history(history: Sequence[dict]) -> str:
    if not history:
        return ""

    turns = "\n".join(
        f"User: {turn['question']}\nAssistant recommended: {turn['answer']}"
        for turn in history
    )
    return f"\nConversation history:\n{turns}\n"


async def generate_answer(
    question: str,
    context: str,
    history: Sequence[dict] | None = None,
) -> str:
    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        history=_format_history(history or []),
    )
    return await ollama_client.generate_async(prompt)
