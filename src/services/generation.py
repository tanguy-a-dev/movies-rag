from collections.abc import Sequence

from src.clients.ollama import ollama_client

PROMPT_TEMPLATE = """You are a movie recommendation system.

Rules:
1. The context below is a numbered list of movies. Your answer MUST have \
exactly as many lines as there are numbered movies -- one line per movie, \
same order, none skipped, none added. This applies even if a movie's \
description is short, missing, or looks similar to another one in the list: \
every numbered entry gets its own line no matter what.
2. Never mention a movie that is not in the context.
3. Output only a markdown list, one line per movie, in exactly this format: \
"- **Title** [id: X]: one sentence on why it fits the question."
4. Do not add an introduction, summary, or closing remark. Output the list \
and nothing else.
5. If conversation history is given below, it shows what you already \
recommended earlier in this chat. The context has already been narrowed to \
exclude those movies, so just answer the new question the same way \
(the exclusion is already handled for you).

Example:

Context:
1. [id: 27205] Inception: A thief who steals corporate secrets through \
dream-sharing technology.

2. [id: 603] The Matrix: A hacker discovers reality is a simulation and \
joins a rebellion.

3. [id: 9999] Second Reality: No overview available.

User question:
Suggest a mind-bending sci-fi movie

Answer:
- **Inception** [id: 27205]: A dream-heist thriller built around layered, \
mind-bending reality.
- **The Matrix** [id: 603]: A reality-questioning sci-fi classic about \
breaking free of a simulation.
- **Second Reality** [id: 9999]: Another sci-fi pick from the same search, \
worth a look even without a full description.

Now do the same for the following context and question. The context has \
{count} numbered movies, so your answer must have exactly {count} lines.
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
    movie_count: int,
    history: Sequence[dict] | None = None,
) -> str:
    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        count=movie_count,
        history=_format_history(history or []),
    )
    return await ollama_client.generate_async(prompt)
