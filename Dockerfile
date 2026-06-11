FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY ui ./ui

RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
