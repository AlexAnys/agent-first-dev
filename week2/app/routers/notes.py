from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..schemas import NoteCreateRequest, NoteResponse
from ..repositories import NoteRepository


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    """Create a new note."""
    try:
        note_id = NoteRepository.create(payload.content)
        note = NoteRepository.get_by_id(note_id)
        if note is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve created note")
        return note
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    """List all notes."""
    try:
        return NoteRepository.list_all()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Get a single note by ID."""
    try:
        note = NoteRepository.get_by_id(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
