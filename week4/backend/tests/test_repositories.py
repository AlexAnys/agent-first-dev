"""Unit tests for repository layer."""

import pytest
from backend.app.repositories import ActionItemRepository, NoteRepository
from sqlalchemy.orm import Session


class TestNoteRepository:
    """Unit tests for NoteRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, test_db_session: Session):
        """Setup for each test method."""
        self.db = test_db_session
        self.repo = NoteRepository()

    def test_create_note(self):
        """Test creating a note."""
        note = self.repo.create(self.db, title="Test Title", content="Test Content")
        assert note.id is not None
        assert note.title == "Test Title"
        assert note.content == "Test Content"

    def test_get_by_id(self):
        """Test retrieving a note by ID."""
        note = self.repo.create(self.db, title="Test", content="Content")
        retrieved = self.repo.get_by_id(self.db, note.id)
        assert retrieved is not None
        assert retrieved.id == note.id
        assert retrieved.title == note.title

    def test_get_by_id_not_found(self):
        """Test retrieving a non-existent note returns None."""
        result = self.repo.get_by_id(self.db, 99999)
        assert result is None

    def test_get_all(self):
        """Test retrieving all notes."""
        self.repo.create(self.db, title="Note 1", content="Content 1")
        self.repo.create(self.db, title="Note 2", content="Content 2")
        self.repo.create(self.db, title="Note 3", content="Content 3")

        notes = self.repo.get_all(self.db)
        assert len(notes) == 3

    def test_get_all_with_pagination(self):
        """Test retrieving notes with pagination."""
        for i in range(10):
            self.repo.create(self.db, title=f"Note {i}", content=f"Content {i}")

        notes = self.repo.get_all(self.db, skip=3, limit=5)
        assert len(notes) == 5

    def test_update_note(self):
        """Test updating a note."""
        note = self.repo.create(self.db, title="Original", content="Original Content")
        updated = self.repo.update(self.db, note, title="Updated Title", content="Updated Content")

        assert updated.id == note.id
        assert updated.title == "Updated Title"
        assert updated.content == "Updated Content"

    def test_delete_note(self):
        """Test deleting a note."""
        note = self.repo.create(self.db, title="To Delete", content="Content")
        note_id = note.id

        self.repo.delete(self.db, note)
        self.db.commit()

        deleted = self.repo.get_by_id(self.db, note_id)
        assert deleted is None

    def test_search_with_query(self):
        """Test searching notes with a query."""
        self.repo.create(self.db, title="Python Tutorial", content="Learn Python")
        self.repo.create(self.db, title="Java Guide", content="Learn Java")
        self.repo.create(self.db, title="Python Advanced", content="Advanced concepts")

        results = self.repo.search(self.db, "Python")
        assert len(results) == 2
        assert all("Python" in note.title for note in results)

    def test_search_without_query(self):
        """Test searching without query returns all notes."""
        self.repo.create(self.db, title="Note 1", content="Content 1")
        self.repo.create(self.db, title="Note 2", content="Content 2")

        results = self.repo.search(self.db, None)
        assert len(results) == 2

    def test_search_with_pagination(self):
        """Test searching with pagination."""
        for i in range(10):
            self.repo.create(self.db, title=f"Test Note {i}", content=f"Content {i}")

        results = self.repo.search(self.db, "Test", skip=2, limit=5)
        assert len(results) == 5


class TestActionItemRepository:
    """Unit tests for ActionItemRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, test_db_session: Session):
        """Setup for each test method."""
        self.db = test_db_session
        self.repo = ActionItemRepository()

    def test_create_action_item(self):
        """Test creating an action item."""
        item = self.repo.create(self.db, description="Test task", completed=False)
        assert item.id is not None
        assert item.description == "Test task"
        assert item.completed is False

    def test_get_by_id(self):
        """Test retrieving an action item by ID."""
        item = self.repo.create(self.db, description="Task", completed=False)
        retrieved = self.repo.get_by_id(self.db, item.id)
        assert retrieved is not None
        assert retrieved.id == item.id
        assert retrieved.description == item.description

    def test_get_by_id_not_found(self):
        """Test retrieving a non-existent action item returns None."""
        result = self.repo.get_by_id(self.db, 99999)
        assert result is None

    def test_get_all(self):
        """Test retrieving all action items."""
        self.repo.create(self.db, description="Task 1", completed=False)
        self.repo.create(self.db, description="Task 2", completed=True)
        self.repo.create(self.db, description="Task 3", completed=False)

        items = self.repo.get_all(self.db)
        assert len(items) == 3

    def test_update_action_item(self):
        """Test updating an action item."""
        item = self.repo.create(self.db, description="Original", completed=False)
        updated = self.repo.update(self.db, item, completed=True)

        assert updated.id == item.id
        assert updated.completed is True

    def test_delete_action_item(self):
        """Test deleting an action item."""
        item = self.repo.create(self.db, description="To Delete", completed=False)
        item_id = item.id

        self.repo.delete(self.db, item)
        self.db.commit()

        deleted = self.repo.get_by_id(self.db, item_id)
        assert deleted is None

    def test_filter_by_status_all(self):
        """Test filtering without status returns all items."""
        self.repo.create(self.db, description="Task 1", completed=False)
        self.repo.create(self.db, description="Task 2", completed=True)
        self.repo.create(self.db, description="Task 3", completed=False)

        items = self.repo.filter_by_status(self.db, completed=None)
        assert len(items) == 3

    def test_filter_by_status_pending(self):
        """Test filtering for pending items."""
        self.repo.create(self.db, description="Task 1", completed=False)
        self.repo.create(self.db, description="Task 2", completed=True)
        self.repo.create(self.db, description="Task 3", completed=False)

        items = self.repo.filter_by_status(self.db, completed=False)
        assert len(items) == 2
        assert all(not item.completed for item in items)

    def test_filter_by_status_completed(self):
        """Test filtering for completed items."""
        self.repo.create(self.db, description="Task 1", completed=False)
        self.repo.create(self.db, description="Task 2", completed=True)
        self.repo.create(self.db, description="Task 3", completed=True)

        items = self.repo.filter_by_status(self.db, completed=True)
        assert len(items) == 2
        assert all(item.completed for item in items)

    def test_filter_with_pagination(self):
        """Test filtering with pagination."""
        for i in range(10):
            self.repo.create(self.db, description=f"Task {i}", completed=False)

        items = self.repo.filter_by_status(self.db, completed=False, skip=3, limit=5)
        assert len(items) == 5
