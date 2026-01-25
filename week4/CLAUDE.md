# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Minimal full-stack developer command center application built with FastAPI and vanilla HTML/CSS/JS. Used as a playground for learning Claude Code automations.

## Common Commands

| Command | Description |
|---------|-------------|
| `make run` | Start FastAPI server at `http://localhost:8000` with auto-reload |
| `make test` | Run pytest suite against `backend/tests` |
| `make format` | Format with black and auto-fix lint with ruff |
| `make lint` | Run ruff checks without fixes |
| `make seed` | Apply `data/seed.sql` if database is empty |

## Architecture

**Backend (FastAPI + SQLite)**:
- `backend/app/main.py`: App entry point, serves frontend from `/` and `/static`
- `backend/app/db.py`: SQLAlchemy engine, session management, seeding logic
- `backend/app/models.py`: SQLAlchemy models (Note, ActionItem)
- `backend/app/schemas.py`: Pydantic request/response schemas
- `backend/app/routers/`: API route handlers organized by resource (notes, action_items)
- `backend/app/services/`: Utilities like `extract.py` for parsing action items

**Frontend**: Static files in `frontend/` served by backend (no build step)

**Testing**: `backend/tests/conftest.py` provides a TestClient with temporary in-memory SQLite database

## Key API Endpoints

- `GET /notes/`, `POST /notes/`: List/create notes
- `GET /notes/search/?q=`: Search notes
- `GET /notes/{id}`: Get single note
- `GET /action-items/`, `POST /action-items/`: List/create action items
- `PUT /action-items/{id}/complete`: Mark item completed

## Configuration

- Database path: `DATABASE_PATH` env var (defaults to `./data/app.db`)
- Pre-commit hooks enforce black, ruff, and trailing whitespace
