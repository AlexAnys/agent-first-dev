# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI app and API logic (`backend/app`), with routers in `backend/app/routers` and services in `backend/app/services`.
- `backend/tests/`: Pytest suite for API behavior; files follow `test_*.py`.
- `frontend/`: Static UI (`index.html`, `styles.css`, `app.js`) served by the backend.
- `data/`: SQLite database (`app.db`) and seed data (`seed.sql`).
- `docs/`: Task notes and documentation scaffolding.

## Build, Test, and Development Commands
Use the Makefile for common workflows:
- `make run`: start the API on `127.0.0.1:8000` with auto-reload; serves the frontend from `/`.
- `make test`: run `pytest` against `backend/tests`.
- `make format`: format Python with `black` and auto-fix lint with `ruff`.
- `make lint`: run `ruff` checks without fixing.
- `make seed`: apply `data/seed.sql` if the database is empty.

## Coding Style & Naming Conventions
- Python: 4-space indentation, Black formatting, Ruff linting (see `pre-commit-config.yaml`).
- Tests: name files `test_*.py` and keep tests focused on one behavior.
- JavaScript/CSS/HTML: follow existing file patterns; keep UI logic in `frontend/app.js`.

## Testing Guidelines
- Framework: `pytest` (`backend/tests`).
- Prefer small, deterministic API tests; use fixtures from `backend/tests/conftest.py` if needed.
- Run tests with `make test`; add new tests alongside existing modules (e.g., `backend/tests/test_notes.py`).

## Commit & Pull Request Guidelines
- Commit history shows short, lowercase messages (no prefix convention). Keep messages concise and task-focused.
- PRs should include: a clear description, linked issues/tasks (if any), and test results. Add UI screenshots/GIFs for frontend changes.

## Configuration & Data Notes
- Database path is configurable via `DATABASE_PATH` (defaults to `./data/app.db`).
- Seeding uses `data/seed.sql`; avoid committing sensitive data.
