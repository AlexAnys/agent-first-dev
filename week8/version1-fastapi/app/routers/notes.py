from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..models import Category, Note, Tag
from ..schemas import NoteCreate, NotePatch, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    """List all notes with optional search, pagination, and sorting."""
    stmt = select(Note).options(
        joinedload(Note.category),
        joinedload(Note.tags),
        joinedload(Note.action_items),
    )
    
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))
    
    if category_id is not None:
        stmt = stmt.where(Note.category_id == category_id)
    
    if tag_id is not None:
        stmt = stmt.join(Note.tags).where(Tag.id == tag_id)

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).unique().scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    """Create a new note with optional category and tags."""
    try:
        # Validate category if provided
        if payload.category_id is not None:
            category = db.get(Category, payload.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error_code": "NOT_FOUND", "message": f"Category with id {payload.category_id} not found"},
                )
        
        # Validate tags if provided
        tags = []
        if payload.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
            if len(tags) != len(payload.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(payload.tag_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error_code": "NOT_FOUND", "message": f"Tags with ids {missing_ids} not found"},
                )
        
        note = Note(
            title=payload.title,
            content=payload.content,
            category_id=payload.category_id,
            tags=tags,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Load relationships for response
        for tag in note.tags:
            db.refresh(tag)
        if note.category:
            db.refresh(note.category)
        
        return NoteRead.model_validate(note)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CREATE_ERROR", "message": f"Failed to create note: {str(e)}"},
        )


@router.get("/search", response_model=list[NoteRead])
def search_notes(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    """Search notes by title or content (dedicated search endpoint)."""
    stmt = select(Note).options(
        joinedload(Note.category),
        joinedload(Note.tags),
        joinedload(Note.action_items),
    ).where(
        (Note.title.contains(q)) | (Note.content.contains(q))
    )

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).unique().scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    """Partially update a note with optional category and tags."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Note with id {note_id} not found"},
        )
    
    try:
        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content
        
        # Update category if provided
        if payload.category_id is not None:
            if payload.category_id == 0:  # Allow setting to None with 0
                note.category_id = None
            else:
                category = db.get(Category, payload.category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"error_code": "NOT_FOUND", "message": f"Category with id {payload.category_id} not found"},
                    )
                note.category_id = payload.category_id
        
        # Update tags if provided
        if payload.tag_ids is not None:
            if payload.tag_ids:  # Non-empty list
                tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
                if len(tags) != len(payload.tag_ids):
                    found_ids = {tag.id for tag in tags}
                    missing_ids = set(payload.tag_ids) - found_ids
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"error_code": "NOT_FOUND", "message": f"Tags with ids {missing_ids} not found"},
                    )
                note.tags = tags
            else:  # Empty list means remove all tags
                note.tags = []
        
        db.commit()
        db.refresh(note)
        
        # Load relationships for response
        for tag in note.tags:
            db.refresh(tag)
        if note.category:
            db.refresh(note.category)
        
        return NoteRead.model_validate(note)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update note: {str(e)}"},
        )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    """Get a single note by ID with relationships."""
    stmt = select(Note).options(
        joinedload(Note.category),
        joinedload(Note.tags),
        joinedload(Note.action_items),
    ).where(Note.id == note_id)
    
    note = db.execute(stmt).unique().scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Note with id {note_id} not found"},
        )
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    """Fully update a note (replace all fields including category and tags)."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Note with id {note_id} not found"},
        )
    
    try:
        # Validate category if provided
        if payload.category_id is not None:
            category = db.get(Category, payload.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error_code": "NOT_FOUND", "message": f"Category with id {payload.category_id} not found"},
                )
        
        # Validate tags if provided
        tags = []
        if payload.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
            if len(tags) != len(payload.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(payload.tag_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error_code": "NOT_FOUND", "message": f"Tags with ids {missing_ids} not found"},
                )
        
        note.title = payload.title
        note.content = payload.content
        note.category_id = payload.category_id
        note.tags = tags
        
        db.commit()
        db.refresh(note)
        
        # Load relationships for response
        for tag in note.tags:
            db.refresh(tag)
        if note.category:
            db.refresh(note.category)
        
        return NoteRead.model_validate(note)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update note: {str(e)}"},
        )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a note by ID."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Note with id {note_id} not found"},
        )
    
    try:
        db.delete(note)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "DELETE_ERROR", "message": f"Failed to delete note: {str(e)}"},
        )


