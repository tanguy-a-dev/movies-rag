.PHONY: install bootstrap dev up down logs check lint lint_fix format type_check test download explore_dataset test_embedding ollama_init ingest qdrant_init qdrant_search help evals deepeval migrate_to_hybrid

HELP_TARGET_COLUMN_WIDTH = 40

help:
	@grep -E '^[a-zA-Z_/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-$(HELP_TARGET_COLUMN_WIDTH)s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	docker compose exec app uv sync --group dev

bootstrap: ## Start full environment (docker + models + dataset)
	up ollama_init qdrant_init download

dev: ## Start dev environment (compose + dev overrides)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
	@echo "Chainlit UI: http://localhost:8001"
	@echo "FastAPI:     http://localhost:8000/docs"
	@echo "Qdrant:      http://localhost:6333/dashboard"

up: ## Start production docker stack
	docker compose up -d --build
	@echo "Chainlit UI: http://localhost:8001"
	@echo "FastAPI:     http://localhost:8000/docs"
	@echo "Qdrant:      http://localhost:6333/dashboard"

check: ## Run lint, type checks and tests
	@make lint
	@make type_check
	@make test

bash:
	docker exec -it moviesrag-app-1 bash

lint: ## Run ruff linter
	docker compose exec app ruff check .

lint_fix: ## Auto-fix lint issues
	docker compose exec app ruff check . --fix

format: ## Format code with ruff
	docker compose exec app ruff format .

type_check: ## Run static type checks
	docker compose exec app ty check

test: ## Run tests
	docker compose exec app uv run pytest

down: ## Stop docker stack
	docker compose down

logs: ## Follow docker logs
	docker compose logs -f

ollama_init: ## Pull LLM and embedding models into Ollama
	docker compose exec ollama ollama pull llama3.1:8b
	docker compose exec ollama ollama pull nomic-embed-text

download: ## Download dataset
	docker compose exec app python -m scripts.download_dataset

explore_dataset: ## Inspect dataset
	docker compose exec app python -m scripts.explore_dataset

test_embedding: ## Test embedding pipeline
	docker compose exec app python -m scripts.test_embedding

ingest: ## Ingest dataset into vector DB
	docker compose exec app python -m scripts.ingest

qdrant_init: ## Initialize Qdrant collections
	docker compose exec app python -m scripts.qdrant_init

qdrant_search: ## Run Qdrant search test
	docker compose exec app python -m scripts.qdrant_search

migrate_to_hybrid: ## One-time: reindex the collection with dense+sparse (hybrid) vectors
	docker compose exec app python -m scripts.migrate_to_hybrid --swap

evals: ## Run evals
	docker exec moviesrag-app-1 python3 -m scripts.eval

deepeval: ## Run DeepEval LLM-quality evals (slow: live Ollama+Qdrant, ~2min/question)
	docker compose exec app uv run pytest evals -v