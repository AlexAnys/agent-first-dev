.PHONY: run test format lint seed

run:
	uv run uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	uv run pytest -q backend/tests

format:
	uv run black .
	uv run ruff check . --fix

lint:
	uv run ruff check .

seed:
	uv run python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
