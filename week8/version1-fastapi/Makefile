.PHONY: run test format lint seed

run:
	PYTHONPATH=. uvicorn app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. pytest -q tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	PYTHONPATH=. python -c "from app.db import apply_seed_if_needed; apply_seed_if_needed()"


