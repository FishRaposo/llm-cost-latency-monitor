.PHONY: install dev test lint format typecheck docker-up docker-down demo examples clean help worker migrate upgrade

install: ## Install shared-core and project dependencies
	pip install -e "../shared-core[dev,docparse,embeddings]"
	pip install -e ".[dev]"

dev: ## Start the FastAPI development server
	python -m llm_monitor.main

test: ## Run unit tests with pytest
	pytest

lint: ## Lint source code with ruff
	ruff check src/llm_monitor tests examples

format: ## Auto-format source code with ruff
	ruff format src/llm_monitor tests examples

typecheck: ## Static type checking with pyright
	pyright src/

docker-up: ## Start PostgreSQL and Redis containers
	docker compose up -d

docker-down: ## Stop all Docker containers
	docker compose down

demo: ## Run the demonstration script
	python examples/run_demo.py

examples: ## Run both integration examples (wrapped FastAPI + RAG)
	python examples/wrapped_fastapi_app.py
	python examples/wrapped_rag_app.py

worker: ## Start the Celery worker (requires a running Redis broker)
	celery -A llm_monitor.worker worker --loglevel=info

migrate: ## Generate a new Alembic migration
	alembic revision --autogenerate -m "auto"

upgrade: ## Apply all pending Alembic migrations
	alembic upgrade head

clean: ## Remove caches and temporary files
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True); shutil.rmtree('.ruff_cache', ignore_errors=True)"

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
