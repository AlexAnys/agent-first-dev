import os
import tempfile
from collections.abc import Generator

import pytest
from backend.app.db import get_db
from backend.app.main import app
from backend.app.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture()
def test_db_engine() -> Generator[Engine, None, None]:
    """Provide a test database engine with temporary SQLite database.

    Creates a temporary database file, initializes the schema,
    and yields the SQLAlchemy engine. Cleans up the database file
    after the test completes.

    Yields:
        Engine: SQLAlchemy engine connected to temporary test database.
    """
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()
    os.unlink(db_path)


@pytest.fixture()
def test_db_session(test_db_engine: Engine) -> Generator[Session, None, None]:
    """Provide a test database session.

    Creates a session bound to the test engine with automatic
    commit/rollback and cleanup.

    Args:
        test_db_engine: Test database engine fixture.

    Yields:
        Session: SQLAlchemy database session for testing.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture()
def client(test_db_engine: Engine) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client with overridden database dependency.

    Uses the test database engine to provide isolated database
    sessions for each request during testing.

    Args:
        test_db_engine: Test database engine fixture.

    Yields:
        TestClient: A FastAPI test client configured with test database.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    def override_get_db() -> Generator:
        """Override the database dependency for testing.

        Provides a database session from the testing database,
        with automatic commit/rollback and cleanup.

        Yields:
            Session: SQLAlchemy database session for testing.
        """
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
