from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError

from .db import apply_seed_if_needed, engine
from .exceptions import ResourceNotFoundError
from .logging_config import get_logger, setup_logging
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router

# Initialize logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Modern Software Dev Starter (Week 4)")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.on_event("startup")
def startup_event() -> None:
    """Initialize database tables and apply seed data on application startup."""
    logger.info("Starting application...")
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()
    logger.info("Application started successfully")


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle ResourceNotFoundError exceptions.

    Args:
        request: The incoming request.
        exc: The ResourceNotFoundError exception.

    Returns:
        JSONResponse: 404 error response with details.
    """
    logger.warning(f"Resource not found: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors.

    Args:
        request: The incoming request.
        exc: The RequestValidationError exception.

    Returns:
        JSONResponse: 422 error response with validation details.
    """

    errors = exc.errors()
    logger.warning(f"Validation error: {errors} - Path: {request.url.path}")

    # Custom function to recursively convert non-serializable objects
    def make_serializable(obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        else:
            return str(obj)

    serializable_errors = [make_serializable(error) for error in errors]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": serializable_errors},
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: The incoming request.
        exc: The ValidationError exception.

    Returns:
        JSONResponse: 422 error response with validation details.
    """
    errors = exc.errors()
    logger.warning(f"Pydantic validation error: {errors} - Path: {request.url.path}")

    # Custom function to recursively convert non-serializable objects
    def make_serializable(obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        else:
            return str(obj)

    serializable_errors = [make_serializable(error) for error in errors]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": serializable_errors},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity constraint violations.

    Args:
        request: The incoming request.
        exc: The IntegrityError exception.

    Returns:
        JSONResponse: 400 error response.
    """
    logger.error(f"Database integrity error: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity constraint violated"},
    )


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """Handle database operational errors.

    Args:
        request: The incoming request.
        exc: The OperationalError exception.

    Returns:
        JSONResponse: 503 error response.
    """
    logger.error(f"Database operational error: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service temporarily unavailable"},
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle general database errors.

    Args:
        request: The incoming request.
        exc: The DatabaseError exception.

    Returns:
        JSONResponse: 500 error response.
    """
    logger.error(f"Database error: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal database error occurred"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions.

    Args:
        request: The incoming request.
        exc: The exception.

    Returns:
        JSONResponse: 500 error response.
    """
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )


@app.get("/")
async def root() -> FileResponse:
    """Serve the frontend index.html file at the root path.

    Returns:
        FileResponse: The main frontend HTML page.
    """
    return FileResponse("frontend/index.html")


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
