import os
import tempfile
from collections.abc import Generator

import pytest
from backend.app.db import get_db
from backend.app.main import app
from backend.app.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
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

    os.unlink(db_path)


def create_test_notes(client: TestClient, count: int) -> list[dict]:
    """Helper function to create multiple test notes."""
    notes = []
    for i in range(count):
        payload = {
            "title": f"Note {i+1:03d}",
            "content": f"Content for note {i+1}"
        }
        response = client.post("/notes/", json=payload)
        assert response.status_code == 201
        notes.append(response.json())
    return notes


def create_test_action_items(client: TestClient, count: int, completed: bool = False) -> list[dict]:
    """Helper function to create multiple test action items."""
    items = []
    for i in range(count):
        payload = {"description": f"Task {i+1:03d}"}
        response = client.post("/action-items/", json=payload)
        assert response.status_code == 201
        item = response.json()

        if completed:
            complete_response = client.put(f"/action-items/{item['id']}/complete")
            assert complete_response.status_code == 200
            item = complete_response.json()

        items.append(item)
    return items
