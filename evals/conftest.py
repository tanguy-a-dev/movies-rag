import os

os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

import pytest  # noqa: E402
from deepeval.models import OllamaModel  # noqa: E402

from src.settings import settings  # noqa: E402


@pytest.fixture(scope="session")
def judge_model() -> OllamaModel:
    return OllamaModel(model=settings.llm_model, base_url=settings.ollama_url)
