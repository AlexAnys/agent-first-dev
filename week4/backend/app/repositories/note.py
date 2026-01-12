from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Note
from .base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """Repository for Note model with specific query methods."""

    def __init__(self):
        """Initialize NoteRepository with Note model."""
        super().__init__(Note)

    def search(
        self, db: Session, query: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> list[Note]:
        """Search notes by title or content with pagination.

        Args:
            db: Database session.
            query: Optional search string to filter notes.
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of notes matching the search query, or all notes if no query provided.
        """
        if not query:
            return self.get_all(db, skip=skip, limit=limit)

        return (
            db.execute(
                select(Note)
                .where((Note.title.contains(query)) | (Note.content.contains(query)))
                .offset(skip)
                .limit(limit)
            )
            .scalars()
            .all()
        )
