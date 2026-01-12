from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .repositories.base import db
from .routers import action_items, notes


# Initialize database tables
db.init_tables()

app = FastAPI(title=settings.APP_TITLE)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the frontend HTML."""
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)


static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
