from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import tags as tags_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend (built bundle from dist)
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    # Mount assets directory for JS/CSS files
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")
    
    @app.get("/")
    async def root() -> FileResponse:
        return FileResponse(str(frontend_dist / "index.html"))
else:
    # Fallback to old static files if dist doesn't exist
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    @app.get("/")
    async def root() -> FileResponse:
        return FileResponse("frontend/index.html")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(tags_router.router)
