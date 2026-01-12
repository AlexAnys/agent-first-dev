from typing import Optional

from sqlalchemy.orm import Session

from ..models import Note
from ..repositories import NoteRepository
from ..schemas import NoteCreate, NoteRead, NoteUpdate
from ..utils import get_or_404, to_schema, to_schema_list


class NoteService:
    """Service layer for Note business logic."""

    def __init__(self):
        """Initialize NoteService with repository."""
        self.repository = NoteRepository()

    def get_all_notes(self, db: Session, skip: int = 0, limit: int = 100) -> list[NoteRead]:
        """Retrieve all notes with pagination.

        Args:
            db: Database session.
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of all notes.
        """
        notes = self.repository.get_all(db, skip=skip, limit=limit)
        return to_schema_list(notes, NoteRead)

    def create_note(self, db: Session, payload: NoteCreate) -> NoteRead:
        """Create a new note.

        Args:
            db: Database session.
            payload: Note creation data.

        Returns:
            Newly created note.
        """
        note = self.repository.create(db, title=payload.title, content=payload.content)
        return to_schema(note, NoteRead)

    def get_note_by_id(self, db: Session, note_id: int) -> NoteRead:
        """Retrieve a note by ID.

        Args:
            db: Database session.
            note_id: Note identifier.

        Returns:
            The requested note.

        Raises:
            ResourceNotFoundError: If note not found.
        """
        note = get_or_404(db, Note, note_id, "Note")
        return to_schema(note, NoteRead)

    def update_note(self, db: Session, note_id: int, payload: NoteUpdate) -> NoteRead:
        """Update a note.

        Args:
            db: Database session.
            note_id: Note identifier.
            payload: Note update data.

        Returns:
            Updated note.

        Raises:
            ResourceNotFoundError: If note not found.
        """
        note = get_or_404(db, Note, note_id, "Note")
        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            updated_note = self.repository.update(db, note, **update_data)
            return to_schema(updated_note, NoteRead)
        return to_schema(note, NoteRead)

    def delete_note(self, db: Session, note_id: int) -> None:
        """Delete a note.

        Args:
            db: Database session.
            note_id: Note identifier.

        Raises:
            ResourceNotFoundError: If note not found.
        """
        note = get_or_404(db, Note, note_id, "Note")
        self.repository.delete(db, note)

    def search_notes(
        self, db: Session, search_query: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> list[NoteRead]:
        """Search notes by title or content with pagination.

        Args:
            db: Database session.
            search_query: Optional search string.
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of notes matching search query.
        """
        notes = self.repository.search(db, search_query, skip=skip, limit=limit)
        return to_schema_list(notes, NoteRead)
