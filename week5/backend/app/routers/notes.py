from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteCreate, NoteRead, NoteSearchResponse, TagAttachRequest

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    stmt = select(Note).options(selectinload(Note.tags))
    rows = db.execute(stmt).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    # Reload with tags relationship
    stmt = select(Note).where(Note.id == note.id).options(selectinload(Note.tags))
    note = db.execute(stmt).scalar_one()
    return NoteRead.model_validate(note)


@router.get("/search", response_model=NoteSearchResponse)
def search_notes(
    q: Optional[str] = None,
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = Query("created_desc"),
    db: Session = Depends(get_db),
) -> NoteSearchResponse:
    stmt = select(Note)

    # Filtering (case-insensitive on title and content)
    if q is not None:
        q_stripped = q.strip()
        if q_stripped:
            pattern = f"%{q_stripped}%"
            stmt = stmt.where(
                Note.title.ilike(pattern) | Note.content.ilike(pattern)
            )

    # Filter by tag
    if tag_id is not None:
        tag = db.get(Tag, tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        stmt = stmt.join(Note.tags).where(Tag.id == tag_id).distinct()

    # Total count before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Sorting
    if sort == "title_asc":
        stmt = stmt.order_by(Note.title.asc())
    else:
        # Default: newest first by id (proxy for created_desc)
        stmt = stmt.order_by(Note.id.desc())

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.options(selectinload(Note.tags)).offset(offset).limit(page_size)

    rows = db.execute(stmt).scalars().all()
    items = [NoteRead.model_validate(row) for row in rows]

    return NoteSearchResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    stmt = select(Note).where(Note.id == note_id).options(selectinload(Note.tags))
    note = db.execute(stmt).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.post("/{note_id}/tags", response_model=NoteRead)
def attach_tag_to_note(note_id: int, payload: TagAttachRequest, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    tag = db.get(Tag, payload.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag is already attached
    if tag in note.tags:
        raise HTTPException(status_code=400, detail="Tag already attached to note")
    
    note.tags.append(tag)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}/tags/{tag_id}", response_model=NoteRead)
def detach_tag_from_note(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag is attached
    if tag not in note.tags:
        raise HTTPException(status_code=400, detail="Tag not attached to note")
    
    note.tags.remove(tag)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)
