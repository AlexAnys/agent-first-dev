from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from ..schemas import (
    ExtractRequest,
    ExtractResponse,
    ActionItemResponse,
    ActionItemExtracted,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..repositories import NoteRepository, ActionItemRepository
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using rule-based approach."""
    try:
    note_id: Optional[int] = None
        if payload.save_note:
            note_id = NoteRepository.create(payload.text)

        items = extract_action_items(payload.text)
        ids = ActionItemRepository.create_many(items, note_id=note_id)
        
        return ExtractResponse(
            note_id=note_id,
            items=[
                ActionItemExtracted(id=i, text=t) 
                for i, t in zip(ids, items)
            ]
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}") from e


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using LLM."""
    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = NoteRepository.create(payload.text)

        items = extract_action_items_llm(payload.text)
        ids = ActionItemRepository.create_many(items, note_id=note_id)
        
        return ExtractResponse(
            note_id=note_id,
            items=[
                ActionItemExtracted(id=i, text=t) 
                for i, t in zip(ids, items)
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {e}") from e


@router.get("", response_model=List[ActionItemResponse])
def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:
    """List all action items, optionally filtered by note_id."""
    try:
        return ActionItemRepository.list_all(note_id=note_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    """Mark an action item as done or not done."""
    try:
        ActionItemRepository.mark_done(action_item_id, payload.done)
        return MarkDoneResponse(id=action_item_id, done=payload.done)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
