.PHONY: run test format lint seed web-install web-dev web-build

run: web-build
	cd .. && poetry run sh -c 'cd week5 && PYTHONPATH=.. python -m uvicorn week5.backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}'

test:
	cd .. && PYTHONPATH=. poetry run pytest -q week5/backend/tests

format:
	cd .. && poetry run black week5
	cd .. && poetry run ruff check week5 --fix

lint:
	cd .. && poetry run ruff check week5

seed:
	cd .. && PYTHONPATH=. poetry run python -c "from week5.backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"

web-install:
	cd frontend && npm install

web-dev:
	cd frontend && npm run dev

web-build:
	cd frontend && npm run build
