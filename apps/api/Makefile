.PHONY: help install run test lint format migrate seed clean docker-build docker-run

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio aiosqlite ruff

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-bot:
	python -m app.bot

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

migrate:
	alembic upgrade head

seed:
	python -m scripts.seed

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null

docker-build:
	docker build -t anonymous-match-api .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
