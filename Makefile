.PHONY: setup lint format download up down logs

setup:
	uv sync
	uv add ruff kagglehub

lint:
	ruff check .

format:
	ruff format .

download:
	docker compose run --rm app python -m cmd.downloadDataset

explore_dataset:
	docker compose run --rm app python -m cmd.exploreDataset

test_embedding:
	docker compose exec app python -m cmd.testEmbedding

up:
	docker compose up -d --build
	@echo "Chainlit UI: http://localhost:8001"
	@echo "FastAPI:     http://localhost:8000/docs"
	@echo "Qdrant:      http://localhost:6333/dashboard"

down:
	docker compose down

logs:
	docker compose logs -f

ollama_init:
	docker exec -it moviesrag-ollama-1 ollama pull llama3.1:8b
	docker exec -it moviesrag-ollama-1 ollama pull nomic-embed-text

ingest:
	docker compose exec app python -m cmd.ingest

qdrant_init:
	docker compose exec app python -m cmd.qdrantInit

qdrant_search:
	docker compose exec app python -m cmd.qdrantSearch
