# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack **developer's command center** application built as a minimal starter for Week 4 of Modern Software Development. It demonstrates a FastAPI backend with SQLite, a static frontend, and automation workflows using Claude Code.

**Tech Stack:**
- **Backend:** FastAPI (Python) with SQLAlchemy ORM and SQLite
- **Frontend:** Static HTML/JavaScript (no build toolchain)
- **Testing:** pytest with TestClient
- **Code Quality:** black (formatting), ruff (linting), pre-commit hooks
- **Database:** SQLite with seed support

## Running the Application

```bash
# Start the server (from week4/ directory)
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && make run

# Access the application
# Frontend: http://localhost:8000
# API docs: http://localhost:8000/docs
# OpenAPI spec: http://localhost:8000/openapi.json
```

**Environment variables:**
- `HOST` (default: 127.0.0.1) – Server host
- `PORT` (default: 8000) – Server port
- `DATABASE_PATH` (default: ./data/app.db) – SQLite database location

## Testing

```bash
# Run all tests
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && make test

# Run a single test file
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && PYTHONPATH=. pytest backend/tests/test_notes.py -v

# Run tests matching a pattern
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && PYTHONPATH=. pytest -k "test_create" -v

# Run with coverage
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && PYTHONPATH=. pytest backend/tests --cov=backend.app --cov-report=html
```

## Code Quality

```bash
# Format code with black + ruff
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && make format

# Lint code (ruff, no fixes)
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && make lint

# Install pre-commit hooks (runs black/ruff on commit)
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && pre-commit install
pre-commit install
```

## Project Structure

```
backend/
  app/
    main.py           # FastAPI app initialization and route setup
    db.py             # SQLAlchemy engine, session management, DB seeding
    models.py         # SQLAlchemy ORM models (Note, ActionItem)
    schemas.py        # Pydantic request/response schemas
    routers/
      notes.py        # /notes endpoints (CRUD + search)
      action_items.py # /action-items endpoints (CRUD)
    services/
      extract.py      # Utility to extract action items from text
  tests/
    conftest.py       # pytest fixtures (test client, test DB)
    test_notes.py     # Tests for notes router
    test_action_items.py  # Tests for action_items router
    test_extract.py    # Tests for extraction service
frontend/
  index.html          # Single-page frontend
  app.js              # Client-side app logic
data/
  app.db              # SQLite database (created on first run)
  seed.sql            # Initial seed data (applied only if DB is new)
docs/
  TASKS.md            # Feature backlog and tasks for agent workflows
```

## Key Architectural Patterns

### Database Layer (`backend/app/db.py`)
- **Dependency injection pattern:** `get_db()` is a FastAPI dependency that yields SQLAlchemy sessions
- **Session management:** Automatic commit on success, rollback on exceptions
- **Auto-seeding:** Reads `data/seed.sql` and applies it only on initial DB creation

### Models and Schemas
- **Models** (`models.py`): SQLAlchemy ORM models define database tables
- **Schemas** (`schemas.py`): Pydantic models for API request/response validation
- **Pattern:** Each router has its own `Create` and `Read` schemas (e.g., `NoteCreate`, `NoteRead`)

### Routers
- **Modular design:** Each resource (notes, action_items) has its own router file
- **Router pattern:** `APIRouter(prefix="/resource", tags=["resource"])` organizes endpoints
- **Database queries:** Use SQLAlchemy `select()` API with `.scalars()` for modern patterns

### Testing
- **Test fixtures:** `conftest.py` provides a test client with an in-memory SQLite database
- **Dependency override:** Tests override `get_db` to use a test database
- **Isolation:** Each test gets a fresh database

## Adding New Endpoints

When adding a new endpoint:

1. **Define the model** in `backend/app/models.py` if needed
2. **Create request/response schemas** in `backend/app/schemas.py`
3. **Write tests first** in the appropriate `backend/tests/test_*.py`
4. **Implement the router** in `backend/app/routers/*.py`
5. **Register the router** in `backend/app/main.py`
6. **Run tests** to verify: `make test`
7. **Format and lint:** `make format && make lint`
8. **Update** `docs/API.md` if creating/modifying endpoints (see Task #7 in `docs/TASKS.md`)

## Core Data Models

### Note
```python
id: int (primary key)
title: str (max 200 chars)
content: str (unlimited)
```

**Endpoints:**
- `GET /notes/` – List all notes
- `GET /notes/{note_id}` – Get a single note
- `GET /notes/search/?q=query` – Search notes by title or content (case-insensitive)
- `POST /notes/` – Create a note

**Planned (Task #5):**
- `PUT /notes/{id}` – Update a note
- `DELETE /notes/{id}` – Delete a note

### ActionItem
```python
id: int (primary key)
description: str (unlimited)
completed: bool (default: False)
```

**Endpoints:**
- `GET /action-items/` – List all action items
- `GET /action-items/{id}` – Get a single action item
- `POST /action-items/` – Create an action item
- `PUT /action-items/{id}/complete` – Mark an action item as complete (scaffolded)

## Extraction Service

`backend/app/services/extract.py` provides utilities to parse action items from text:

- `extract_action_items(text: str) -> list[str]` – Extract lines starting with "-" as action items
- **Planned (Task #4):** Extend to parse `#tag` syntax and return tags

## Automation and Workflow Guidance

This repository supports **Claude Code automations** via custom slash commands, CLAUDE.md guidance, and SubAgents.

**Intended automation tasks** (see `docs/TASKS.md`):
- Test runners with coverage reporting
- API documentation synchronization (compare implementation to `openapi.json`)
- Module refactoring with import updates
- Database schema migrations with model/router updates

**Safe commands to run:**
- `make run` – Start the server
- `make test` – Run pytest
- `make format` – Format with black and ruff (modifies files)
- `make lint` – Check linting only (no modifications)
- `pre-commit run --all-files` – Run all pre-commit hooks

**Commands to avoid:**
- Destructive git operations (`git reset --hard`, `git push --force`)
- Database deletions without backups
- Manual SQL manipulation without tests

## Common Workflows

### Running a Single Test
```bash
source /Users/xuyin/Documents/Repository/modern-software-dev-assignments/.venv/bin/activate && PYTHONPATH=. pytest backend/tests/test_notes.py::test_create_note -v
```

### Seeding the Database
```bash
make seed
```
This applies `data/seed.sql` if the database doesn't exist.

### Checking API Changes
```bash
# Compare implementation against OpenAPI spec
curl http://localhost:8000/openapi.json | jq . > openapi_current.json
# Then manually compare against docs/API.md
```

## Development Conventions

- **Python version:** 3.10+ (SQLAlchemy 2.0+, modern type hints)
- **Imports:** Use absolute imports (e.g., `from backend.app.db import ...`)
- **Session handling:** Always use `get_db` dependency or context managers for clean-up
- **Error handling:** FastAPI `HTTPException` for API errors; rollback happens automatically in `get_db`
- **Validation:** Use Pydantic `Field` constraints in schemas for validation (not yet implemented, but recommended for Task #6)

## Integration with CI/CD and Automation

This repository is designed for agent-driven workflows:

- **Pre-commit hooks** enforce black/ruff on every commit; agents should run `make format` before committing
- **Task backlog** in `docs/TASKS.md` defines features suitable for agent implementation
- **OpenAPI docs** at `/openapi.json` enable automated drift detection (useful for documentation agents)
- **Test structure** with fixtures makes it easy to write integration tests for new features

---

For questions about the application logic, refer to the source files directly. For testing strategies and patterns, see `backend/tests/conftest.py`.
