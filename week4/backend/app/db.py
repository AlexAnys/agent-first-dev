import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "./data/app.db")

engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """Provide a database session for FastAPI dependency injection.

    This function is designed to be used with FastAPI's Depends() mechanism.
    It creates a new database session for each HTTP request, yields it for use
    in route handlers, and ensures proper cleanup with automatic commit/rollback.

    Use this for FastAPI route handlers via Depends(get_db).

    Yields:
        Session: SQLAlchemy database session for the request lifecycle.

    Raises:
        IntegrityError: On database constraint violations.
        OperationalError: On database connection or operational issues.
        DatabaseError: On other database-related errors.

    Example:
        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Database integrity error: {e}")
        raise
    except OperationalError as e:
        session.rollback()
        logger.error(f"Database operational error: {e}")
        raise
    except DatabaseError as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"SQLAlchemy error: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in database session: {e}", exc_info=True)
        raise
    finally:
        session.close()


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a database session as a context manager for non-request contexts.

    This function is designed for use in scripts, background tasks, or any
    code outside of FastAPI request handlers. It provides a context-managed
    database session with automatic commit/rollback and cleanup.

    Use this for standalone scripts, CLI commands, or background jobs.
    For FastAPI routes, use get_db() instead.

    Yields:
        Session: SQLAlchemy database session.

    Raises:
        IntegrityError: On database constraint violations.
        OperationalError: On database connection or operational issues.
        DatabaseError: On other database-related errors.

    Example:
        with get_session() as db:
            item = Item(name="example")
            db.add(item)
            # Automatically commits on successful exit
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Database integrity error: {e}")
        raise
    except OperationalError as e:
        session.rollback()
        logger.error(f"Database operational error: {e}")
        raise
    except DatabaseError as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"SQLAlchemy error: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in database session: {e}", exc_info=True)
        raise
    finally:
        session.close()


def apply_seed_if_needed() -> None:
    """Initialize database with seed data if database is newly created.

    Checks if the database file is new and applies SQL statements
    from data/seed.sql if available.
    """
    db_path = Path(DEFAULT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    newly_created = not db_path.exists()
    if newly_created:
        db_path.touch()

    seed_file = Path("./data/seed.sql")
    if newly_created and seed_file.exists():
        with engine.begin() as conn:
            sql = seed_file.read_text()
            if sql.strip():
                for statement in [s.strip() for s in sql.split(";") if s.strip()]:
                    conn.execute(text(statement))
