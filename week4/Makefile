.PHONY: run test format lint seed

# [핵심] 외부에서 PYTHON_EXEC를 주입받을 수 있게 ?= 사용
PYTHON_EXEC ?= python

run:
	# PYTHONPATH와 함께 실행기 동적 적용
	PYTHONPATH=. $(PYTHON_EXEC) -m uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. $(PYTHON_EXEC) -m pytest -q backend/tests

format:
	$(PYTHON_EXEC) -m black .
	$(PYTHON_EXEC) -m ruff check . --fix

lint:
	$(PYTHON_EXEC) -m ruff check .

seed:
	PYTHONPATH=. $(PYTHON_EXEC) -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"