"""Unit tests for service layer."""

import pytest
from backend.app.exceptions import ResourceNotFoundError
from backend.app.schemas import (
    ActionItemCreate,
    ActionItemUpdate,
    NoteCreate,
    NoteUpdate,
)
from backend.app.services import ActionItemService, NoteService
from sqlalchemy.orm import Session


class TestNoteService:
    """Unit tests for NoteService."""

    @pytest.fixture(autouse=True)
    def setup(self, test_db_session: Session):
        """Setup for each test method."""
        self.db = test_db_session
        self.service = NoteService()

    def test_create_note(self):
        """Test creating a note through service."""
        payload = NoteCreate(title="Service Test", content="Test Content")
        note = self.service.create_note(self.db, payload)

        assert note.id is not None
        assert note.title == "Service Test"
        assert note.content == "Test Content"

    def test_get_all_notes(self):
        """Test retrieving all notes through service."""
        self.service.create_note(self.db, NoteCreate(title="Note 1", content="Content 1"))
        self.service.create_note(self.db, NoteCreate(title="Note 2", content="Content 2"))

        notes = self.service.get_all_notes(self.db)
        assert len(notes) == 2

    def test_get_all_notes_with_pagination(self):
        """Test retrieving notes with pagination through service."""
        for i in range(10):
            self.service.create_note(self.db, NoteCreate(title=f"Note {i}", content=f"Content {i}"))

        notes = self.service.get_all_notes(self.db, skip=3, limit=5)
        assert len(notes) == 5

    def test_get_note_by_id(self):
        """Test retrieving a note by ID through service."""
        created = self.service.create_note(self.db, NoteCreate(title="Test", content="Content"))
        retrieved = self.service.get_note_by_id(self.db, created.id)

        assert retrieved.id == created.id
        assert retrieved.title == created.title

    def test_get_note_by_id_not_found(self):
        """Test retrieving a non-existent note raises error."""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            self.service.get_note_by_id(self.db, 99999)
        assert "Note" in str(exc_info.value)

    def test_update_note(self):
        """Test updating a note through service."""
        created = self.service.create_note(
            self.db, NoteCreate(title="Original", content="Original Content")
        )
        payload = NoteUpdate(title="Updated", content="Updated Content")
        updated = self.service.update_note(self.db, created.id, payload)

        assert updated.id == created.id
        assert updated.title == "Updated"
        assert updated.content == "Updated Content"

    def test_update_note_partial(self):
        """Test partially updating a note (only title)."""
        created = self.service.create_note(
            self.db, NoteCreate(title="Original", content="Original Content")
        )
        payload = NoteUpdate(title="Updated Only Title")
        updated = self.service.update_note(self.db, created.id, payload)

        assert updated.title == "Updated Only Title"
        assert updated.content == "Original Content"

    def test_update_note_not_found(self):
        """Test updating a non-existent note raises error."""
        with pytest.raises(ResourceNotFoundError):
            self.service.update_note(self.db, 99999, NoteUpdate(title="Updated", content="Updated"))

    def test_delete_note(self):
        """Test deleting a note through service."""
        created = self.service.create_note(
            self.db, NoteCreate(title="To Delete", content="Content")
        )
        self.service.delete_note(self.db, created.id)

        with pytest.raises(ResourceNotFoundError):
            self.service.get_note_by_id(self.db, created.id)

    def test_delete_note_not_found(self):
        """Test deleting a non-existent note raises error."""
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_note(self.db, 99999)

    def test_search_notes_with_query(self):
        """Test searching notes with a query through service."""
        self.service.create_note(
            self.db, NoteCreate(title="Python Tutorial", content="Learn Python")
        )
        self.service.create_note(self.db, NoteCreate(title="Java Guide", content="Learn Java"))
        self.service.create_note(
            self.db, NoteCreate(title="Python Advanced", content="Advanced concepts")
        )

        results = self.service.search_notes(self.db, "Python")
        assert len(results) == 2

    def test_search_notes_without_query(self):
        """Test searching notes without query returns all."""
        self.service.create_note(self.db, NoteCreate(title="Note 1", content="Content 1"))
        self.service.create_note(self.db, NoteCreate(title="Note 2", content="Content 2"))

        results = self.service.search_notes(self.db, None)
        assert len(results) == 2


class TestActionItemService:
    """Unit tests for ActionItemService."""

    @pytest.fixture(autouse=True)
    def setup(self, test_db_session: Session):
        """Setup for each test method."""
        self.db = test_db_session
        self.service = ActionItemService()

    def test_create_action_item(self):
        """Test creating an action item through service."""
        payload = ActionItemCreate(description="Test task")
        item = self.service.create_action_item(self.db, payload)

        assert item.id is not None
        assert item.description == "Test task"
        assert item.completed is False

    def test_get_all_action_items(self):
        """Test retrieving all action items through service."""
        self.service.create_action_item(self.db, ActionItemCreate(description="Task 1"))
        self.service.create_action_item(self.db, ActionItemCreate(description="Task 2"))

        items = self.service.get_all_action_items(self.db)
        assert len(items) == 2

    def test_get_all_with_status_filter_pending(self):
        """Test filtering action items by pending status."""
        item1 = self.service.create_action_item(self.db, ActionItemCreate(description="Task 1"))
        self.service.create_action_item(self.db, ActionItemCreate(description="Task 2"))
        self.service.complete_action_item(self.db, item1.id)

        items = self.service.get_all_action_items(self.db, status="pending")
        assert len(items) == 1
        assert not items[0].completed

    def test_get_all_with_status_filter_completed(self):
        """Test filtering action items by completed status."""
        item1 = self.service.create_action_item(self.db, ActionItemCreate(description="Task 1"))
        self.service.create_action_item(self.db, ActionItemCreate(description="Task 2"))
        self.service.complete_action_item(self.db, item1.id)

        items = self.service.get_all_action_items(self.db, status="completed")
        assert len(items) == 1
        assert items[0].completed

    def test_get_all_with_pagination(self):
        """Test retrieving action items with pagination."""
        for i in range(10):
            self.service.create_action_item(self.db, ActionItemCreate(description=f"Task {i}"))

        items = self.service.get_all_action_items(self.db, skip=3, limit=5)
        assert len(items) == 5

    def test_update_action_item(self):
        """Test updating an action item through service."""
        created = self.service.create_action_item(self.db, ActionItemCreate(description="Original"))
        payload = ActionItemUpdate(description="Updated", completed=True)
        updated = self.service.update_action_item(self.db, created.id, payload)

        assert updated.id == created.id
        assert updated.description == "Updated"
        assert updated.completed is True

    def test_update_action_item_partial(self):
        """Test partially updating an action item (only description)."""
        created = self.service.create_action_item(self.db, ActionItemCreate(description="Original"))
        payload = ActionItemUpdate(description="Updated Only")
        updated = self.service.update_action_item(self.db, created.id, payload)

        assert updated.description == "Updated Only"
        assert updated.completed is False

    def test_update_action_item_not_found(self):
        """Test updating a non-existent action item raises error."""
        with pytest.raises(ResourceNotFoundError):
            self.service.update_action_item(self.db, 99999, ActionItemUpdate(description="Updated"))

    def test_delete_action_item(self):
        """Test deleting an action item through service."""
        created = self.service.create_action_item(
            self.db, ActionItemCreate(description="To Delete")
        )
        self.service.delete_action_item(self.db, created.id)

        with pytest.raises(ResourceNotFoundError):
            from backend.app.models import ActionItem
            from backend.app.utils import get_or_404

            get_or_404(self.db, ActionItem, created.id, "Action item")

    def test_delete_action_item_not_found(self):
        """Test deleting a non-existent action item raises error."""
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_action_item(self.db, 99999)

    def test_complete_action_item(self):
        """Test marking an action item as completed through service."""
        created = self.service.create_action_item(self.db, ActionItemCreate(description="Task"))
        completed = self.service.complete_action_item(self.db, created.id)

        assert completed.id == created.id
        assert completed.completed is True

    def test_complete_action_item_not_found(self):
        """Test completing a non-existent action item raises error."""
        with pytest.raises(ResourceNotFoundError):
            self.service.complete_action_item(self.db, 99999)
