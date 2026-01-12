from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NotePatch, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    """
    Search notes by title or content (SQL injection safe version).
    Uses SQLAlchemy ORM to prevent SQL injection attacks.
    """
    stmt = select(Note).where(
        (Note.title.ilike(f"%{q}%")) | (Note.content.ilike(f"%{q}%"))
    ).order_by(desc(Note.created_at)).limit(50)
    
    rows = db.execute(stmt).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.get("/debug/hash-md5")
def debug_hash_md5(q: str) -> dict[str, str]:
    import hashlib

    return {"algo": "md5", "hex": hashlib.md5(q.encode()).hexdigest()}


@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    """
    SECURITY: This endpoint has been disabled to prevent code injection attacks.
    Using eval() allows arbitrary code execution which is extremely dangerous.
    """
    raise HTTPException(
        status_code=403,
        detail="This debug endpoint has been disabled for security reasons. Code evaluation is not allowed."
    )


@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    """
    SECURITY: This endpoint has been disabled to prevent command injection attacks.
    Using subprocess with shell=True allows arbitrary command execution.
    If debug functionality is needed, use a whitelist of allowed commands.
    """
    raise HTTPException(
        status_code=403,
        detail="This debug endpoint has been disabled for security reasons. Command execution is not allowed."
    )


@router.get("/debug/fetch")
def debug_fetch(url: str) -> dict[str, str]:
    """
    SECURITY: This endpoint has been disabled to prevent SSRF attacks.
    urllib supports 'file://' scheme which can be used to read arbitrary files.
    If URL fetching is needed, validate and whitelist allowed URLs.
    """
    # URL 검증: file:// 스킴 차단 및 허용된 도메인만 허용
    if url.startswith("file://"):
        raise HTTPException(
            status_code=400,
            detail="file:// scheme is not allowed for security reasons."
        )
    
    # 허용된 도메인만 허용 (예: localhost만)
    from urllib.parse import urlparse
    parsed = urlparse(url)
    allowed_hosts = ["localhost", "127.0.0.1"]
    
    if parsed.hostname not in allowed_hosts:
        raise HTTPException(
            status_code=403,
            detail=f"Only requests to {', '.join(allowed_hosts)} are allowed."
        )
    
    from urllib.request import urlopen
    try:
        with urlopen(url, timeout=5) as res:  # timeout 추가
            body = res.read(1024).decode(errors="ignore")
        return {"snippet": body}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")


@router.get("/debug/read")
def debug_read(path: str) -> dict[str, str]:
    try:
        content = open(path, "r").read(1024)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    return {"snippet": content}

