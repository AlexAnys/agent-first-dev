.PHONY: run test format lint seed

HOST ?= localhost
PORT ?= 8000

run:
	python -m uvicorn backend.app.main:app --reload --host $(HOST) --port $(PORT)
test:
	python -m pytest -q backend/tests
format:
	python -m black .
	python -m ruff check . --fix

lint:
	python -m ruff check .

seed:
	python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
