from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# Tag Schemas
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, max_length=20, description="Tag color for UI")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Check that the tag name is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Tag name cannot be empty or contain only whitespace")
        return v.strip().lower()  # Normalize to lowercase


class TagRead(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Check that the category name is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty or contain only whitespace")
        return v.strip()


class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Note Schemas
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    category_id: Optional[int] = Field(None, description="Category ID")
    tag_ids: Optional[list[int]] = Field(default_factory=list, description="List of tag IDs")

    @field_validator("title", "content")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Check that the string is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")
        return v.strip()


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryRead] = None
    tags: list[TagRead] = []
    action_items: list["ActionItemRead"] = []

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, min_length=1, description="Note content")
    category_id: Optional[int] = Field(None, description="Category ID")
    tag_ids: Optional[list[int]] = Field(None, description="List of tag IDs")

    @field_validator("title", "content")
    @classmethod
    def validate_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """If provided, check that the string is not empty or only whitespace."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field cannot be empty or contain only whitespace")
            return v.strip()
        return v


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Action item description")
    note_id: Optional[int] = Field(None, description="Associated note ID")

    @field_validator("description")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Check that the string is not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or contain only whitespace")
        return v.strip()


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    note_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: Optional[str] = Field(None, min_length=1, description="Action item description")
    completed: Optional[bool] = None
    note_id: Optional[int] = Field(None, description="Associated note ID")

    @field_validator("description")
    @classmethod
    def validate_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """If provided, check that the string is not empty or only whitespace."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Description cannot be empty or contain only whitespace")
            return v.strip()
        return v


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: Optional[str] = None


