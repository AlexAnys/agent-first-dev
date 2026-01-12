from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..constants import HTTP_201_CREATED
from ..db import get_db
from ..logging_config import get_logger
from ..schemas import NoteCreate, NoteRead, NoteUpdate
from ..services import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])
note_service = NoteService()
logger = get_logger(__name__)


@router.get("/", response_model=list[NoteRead])
def list_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> list[NoteRead]:
    """Retrieve all notes from the database with pagination.

    Args:
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 100, max: 1000).
        db: Database session dependency.

    Returns:
        List of all notes.
    """
    logger.info(f"Listing notes with skip={skip}, limit={limit}")
    notes = note_service.get_all_notes(db, skip=skip, limit=limit)
    logger.info(f"Retrieved {len(notes)} notes")
    return notes


@router.post("/", response_model=NoteRead, status_code=HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    """Create a new note.

    Args:
        payload: Note creation data containing title and content.
        db: Database session dependency.

    Returns:
        The newly created note.
    """
    logger.info(f"Creating note with title='{payload.title}'")
    note = note_service.create_note(db, payload)
    logger.info(f"Created note with id={note.id}")
    return note


@router.get("/search/", response_model=list[NoteRead])
def search_notes(
    search_query: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> list[NoteRead]:
    """Search notes by title or content with pagination.

    Args:
        search_query: Optional search string to filter notes by title or content.
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 100, max: 1000).
        db: Database session dependency.

    Returns:
        List of notes matching the search query, or all notes if no query provided.
    """
    logger.info(f"Searching notes with query='{search_query}', skip={skip}, limit={limit}")
    notes = note_service.search_notes(db, search_query, skip=skip, limit=limit)
    logger.info(f"Found {len(notes)} notes matching search")
    return notes


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    """Retrieve a specific note by ID.

    Args:
        note_id: ID of the note to retrieve.
        db: Database session dependency.

    Returns:
        The requested note.

    Raises:
        ResourceNotFoundError: If the note is not found.
    """
    logger.info(f"Retrieving note with id={note_id}")
    note = note_service.get_note_by_id(db, note_id)
    logger.info(f"Retrieved note with id={note_id}")
    return note


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    """Update a note.

    Args:
        note_id: ID of the note to update.
        payload: Note update data (title and/or content).
        db: Database session dependency.

    Returns:
        The updated note.

    Raises:
        ResourceNotFoundError: If the note is not found.
    """
    logger.info(f"Updating note with id={note_id}")
    note = note_service.update_note(db, note_id, payload)
    logger.info(f"Updated note with id={note_id}")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a note.

    Args:
        note_id: ID of the note to delete.
        db: Database session dependency.

    Raises:
        ResourceNotFoundError: If the note is not found.
    """
    logger.info(f"Deleting note with id={note_id}")
    note_service.delete_note(db, note_id)
    logger.info(f"Deleted note with id={note_id}")
