from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============== Note Schemas ==============

class NoteCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Note content")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


# ============== Action Item Schemas ==============

class ActionItemBase(BaseModel):
    text: str


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool = False
    created_at: str


class ActionItemExtracted(BaseModel):
    id: int
    text: str


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ActionItemExtracted]


class MarkDoneRequest(BaseModel):
    done: bool = Field(default=True, description="Mark as done or not done")


class MarkDoneResponse(BaseModel):
    id: int
    done: bool


# ============== LLM Schemas ==============

class LLMActionItem(BaseModel):
    action: str


class LLMActionItemList(BaseModel):
    items: List[LLMActionItem]
