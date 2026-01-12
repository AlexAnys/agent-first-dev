# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Environment and tooling

- Python: targets 3.10–3.12; course README assumes 3.12.
- Dependency management: Poetry at the repo root via `pyproject.toml`.
- Web stack: FastAPI + Uvicorn + SQLAlchemy + Pydantic + SQLite.
- LLM stack: Ollama (e.g., `llama3.1:8b`) for some weeks; OpenAI/`mcp` libs are available but not always required.

Recommended global setup from the repo root(conda cs146s may be installed already.):

```bash
conda create -n cs146s python=312 -y
conda activate cs146s
poetry install --no-interaction
```

You can also use a virtualenv instead of Conda (see `week7/README.md` for an example using `python -m venv` and `pip install -e .[dev]`)

## Common commands

All commands below assume you run them from the repository root unless noted.

### Run tests

- Run all tests for a given week using Poetry:

  ```bash
  poetry run pytest week2/tests/ -v
  poetry run pytest week3/tests/ -v
  poetry run pytest week4/backend/tests -q
  poetry run pytest week5/backend/tests -q
  poetry run pytest week6/backend/tests -q
  poetry run pytest week7/backend/tests -q
  ```

- Run a single test file (example):

  ```bash
  poetry run pytest week3/tests/test_github_client.py -vv
  poetry run pytest week7/backend/tests/test_notes.py -vv
  ```

- Run a single test function (example):

  ```bash
  poetry run pytest week4/backend/tests/test_integration.py::TestNotesCRUDLifecycle::test_full_note_lifecycle -vv
  ```

### FastAPI backends (weeks 2, 4–7)

**Week 2 (Action Item Extractor)**

- Start server (uses Poetry and Ollama-backed extraction):

  ```bash
  poetry run uvicorn week2.app.main:app --reload
  ```

- Run week2 extraction tests only:

  ```bash
  poetry run pytest week2/tests/test_extract.py -vv
  ```

**Weeks 4–7 (FastAPI + SQLite full-stack starters)**

Each of these weeks is a mostly self-contained FastAPI + SQLite backend with a `backend/` directory and a `Makefile` that wraps the most common tasks.

From a given week directory (e.g., `week7/`):

```bash
cd week7
make run     # Start FastAPI + Uvicorn with hot reload
make test    # Run backend pytest suite
make format  # Run black + ruff (with autofix)
make lint    # Run ruff only
make seed    # Initialize/seed SQLite database if needed
```

Notes:
- The Makefiles set `PYTHONPATH=.` so imports like `backend.app.main` resolve correctly.
- Uvicorn serves a static frontend under `/static` and the main HTML at `/`.
- For week7 specifically, you can follow `week7/README.md` for end-to-end setup and URLs (`/` for the app, `/docs` for OpenAPI docs).

### Week 3 – GitHub Daily Issue MCP server

- Run the MCP server directly (STDIO transport):

  ```bash
  poetry run python -m week3.server.main
  ```

- Run week3 tests:

  ```bash
  poetry run pytest week3/tests/ -v
  ```

`week3/README.md` includes concrete examples for wiring this server into Cursor or Claude as an MCP provider.

### Week 1 – LLM Prompting Playground

Week1 contains standalone scripts for experimenting with LLM prompting (e.g., retrieval-augmented generation against small corpora using Ollama).

- Example entry point:

  ```bash
  poetry run python week1/rag.py
  ```

Ensure Ollama is installed and the referenced model (e.g., `llama3.1:8b`) is pulled and running.

## Architecture overview

### High-level layout

The repo is organized into weekly assignments:

- `week1/`: Prompting and RAG playground using Ollama.
- `week2/`: First full-stack Action Item Extractor (FastAPI + SQLite + Ollama).
- `week3/`: GitHub Daily Issue MCP server.
- `week4/`–`week7/`: Iterative refinements of a full-stack notes + action-items app.
- `week8/`: Later assignment scaffold (check `week8/` for the current state of that week).

Most of the “real app” work lives in weeks 2–7.

### FastAPI backends (weeks 2, 4–7)

All backend weeks share the same general layering; file names differ slightly by week but the roles are consistent.

- **Entry point / application wiring**
  - Week2: `week2/app/main.py` creates the FastAPI app, initializes tables via a repository-level `db` helper, mounts the static frontend, and includes `notes` and `action_items` routers.
  - Weeks4–7: `backend/app/main.py` creates the app, configures CORS (week4+), mounts `/static` for the frontend, sets up startup hooks that create tables and call `apply_seed_if_needed`, and includes routers from `backend/app/routers/`.

- **Database configuration and lifecycle**
  - Week2: DB configuration is driven via `week2/app/config.py` and `repositories/base.py`, with settings (DB path, LLM model name, etc.) read from `.env`.
  - Weeks4–7: `backend/app/db.py` is the single source of truth for SQLAlchemy configuration:
    - Reads a `DATABASE_PATH`-like environment variable (see `DEFAULT_DB_PATH`) with a default `./data/app.db` path.
    - Creates the SQLAlchemy `engine` and `SessionLocal` factory.
    - Exposes `get_db()` for FastAPI dependency injection (per-request sessions with commit/rollback) and `get_session()` as a context manager for non-request contexts.
    - Provides `apply_seed_if_needed()` which ensures the DB file exists and, when first created, executes SQL statements from `data/seed.sql` if present.

- **ORM models and schema layers**
  - Week2: Models are thin SQLite tables for notes and action items, accessed via repository classes in `repositories/`.
  - Weeks4–7: `backend/app/models.py` defines SQLAlchemy ORM models:
    - `Base` (via `declarative_base`).
    - A `TimestampMixin` that adds `created_at`/`updated_at` columns.
    - `Note` and `ActionItem` models (with `title`/`content` and `description`/`completed` fields respectively).
  - Pydantic models live in `backend/app/schemas.py` and define request/response shapes (e.g., `NoteCreate`, `NoteRead`, `NotePatch`, `ActionItemCreate`, `ActionItemRead`, `ActionItemPatch`).
    - `from_attributes = True` is used so ORM instances can be fed directly into response models.

- **HTTP routing and business logic**
  - Routers reside in `backend/app/routers/` and expose RESTful endpoints:
    - `notes.py`: list/search notes with pagination and sort parameters, create notes, read a single note, and partially update via PATCH.
    - `action_items.py`: list action items with optional completion filter and pagination, create new items, mark items complete (`PUT /action-items/{id}/complete`), and partially update items.
  - Business logic that is not simple CRUD is placed in `backend/app/services/` (e.g., `extract.py` for turning free-form text into action item descriptions based on simple heuristics like prefixes `TODO:`/`Action:` or exclamation-mark emphasis).
  - Some weeks (e.g., week4) further decompose logic into `repositories/` and additional `services` modules for testable units.

- **Frontend and static assets**
  - Weeks2 and 4–7 each include a very small HTML/JS frontend under a `frontend/` directory.
  - The backend serves `frontend/index.html` from `/` and the same directory via `/static` for assets, enabling a single-page notes + tasks UI backed by the API.

- **Testing structure**
  - Week2: `week2/tests/test_extract.py` focuses on the extraction logic only (both rule-based and LLM-based), asserting types and non-empty results.
  - Week3: `week3/tests/test_github_client.py` is an extensive test harness around `server/github_client.py`, using `pytest` and `httpx` mocks to cover title generation, issue discovery/creation, commenting, and combined workflows.
  - Weeks4–7: `backend/tests/` is organized by concern:
    - Unit tests for services, repositories, and edge cases.
    - Integration-style tests (e.g., `test_integration.py` in week4) using `fastapi.testclient.TestClient` to run full CRUD workflows across notes and action items, plus pagination and search flows.
    - `conftest.py` sets up an isolated SQLite database per test session by overriding `get_db`.

### Week 3 – GitHub Daily Issue MCP server

The MCP server in `week3/` wraps GitHub’s Issues API behind two tools exposed via `mcp.server.fastmcp.FastMCP`:

- `get_or_create_today_issue(owner, repo)`: computes a localized Korean “today” title, lists recent issues, and either returns an existing Daily Issue or creates one labeled `daily`.
- `add_comment_to_today_issue(owner, repo, comment)`: finds or creates today’s issue and appends a comment.

Configuration and API access details:

- `week3/server/config.py` reads environment variables such as `GITHUB_TOKEN`, `GITHUB_DEFAULT_OWNER`, `GITHUB_DEFAULT_REPO`, and `REQUEST_TIMEOUT`, and exposes a `settings.validate()` method used at runtime.
- `week3/server/github_client.py` contains the HTTPX-based GitHub client functions that tests exercise.
- `week3/README.md` documents concrete `mcp.json` and `claude_desktop_config.json` snippets to wire this server into Cursor or Claude.

### Week 1 – LLM playground

Week1 is a sandbox for RAG-style prompting with Ollama:

- `week1/rag.py` builds a small in-memory corpus from text files under `week1/data/`, constructs a user/system prompt, calls Ollama’s `chat` API multiple times, and inspects code-like output for required snippets.
- Environment variables (e.g., Ollama host/model) are loaded via `python-dotenv`; see the script to understand what needs to be present in `.env`.

### Task docs

Several later-week backends ship with task backlogs under `docs/TASKS.md` (e.g., `week4/docs/TASKS.md`, `week5/docs/TASKS.md`, `week7/docs/TASKS.md`). These describe incremental features (search endpoints, CRUD enhancements, validation, docs drift checks, etc.) and should be consulted whenever you are asked to “finish” or “improve” a week’s app.

Where those docs mention pre-commit hooks, the expected workflow is:

```bash
pre-commit install
pre-commit run --all-files
```

Run those from the relevant week directory or repo root depending on where the configuration lives.
