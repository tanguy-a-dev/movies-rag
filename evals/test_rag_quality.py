import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    GEval,
)
from deepeval.test_case import LLMTestCase, SingleTurnParams

from scripts.eval import DEFAULT_QUESTIONS_PATH, load_questions
from src.services import rag

QUESTIONS = load_questions(DEFAULT_QUESTIONS_PATH)


@pytest.mark.parametrize("question", QUESTIONS, ids=lambda q: q["question"])
async def test_rag_answer_quality(question, judge_model):
    result = await rag.ask(question["question"])

    retrieval_context = [
        f"{source['title']}: {source['overview']}"
        for source in result["sources"]
        if source.get("overview")
    ]

    test_case = LLMTestCase(
        input=question["question"],
        actual_output=result["answer"],
        retrieval_context=retrieval_context,
        expected_output=f"Movies from genres: {', '.join(question['expected_genres'])}",
    )

    genre_match = GEval(
        name="Genre Match",
        criteria=(
            "Determine whether the movies recommended in 'actual output' plausibly "
            "belong to the genres described in 'expected output'."
        ),
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
        model=judge_model,
    )

    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.5, model=judge_model),
            FaithfulnessMetric(threshold=0.5, model=judge_model),
            ContextualRelevancyMetric(threshold=0.5, model=judge_model),
            genre_match,
        ],
    )
