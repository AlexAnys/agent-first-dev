from typing import Optional

from pydantic import BaseModel, field_validator

from .constants import MAX_TITLE_LENGTH


class NoteCreate(BaseModel):
    """Schema for creating a new note.

    Attributes:
        title: Note title.
        content: Note content.
    """

    title: str
    content: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate note title is not empty and within length limit.

        Args:
            v: Title value to validate.

        Returns:
            Validated title.

        Raises:
            ValueError: If title is empty or exceeds max length.
        """
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        if len(v) > MAX_TITLE_LENGTH:
            raise ValueError(f"Title cannot exceed {MAX_TITLE_LENGTH} characters")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate note content is not empty.

        Args:
            v: Content value to validate.

        Returns:
            Validated content.

        Raises:
            ValueError: If content is empty.
        """
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace")
        return v.strip()


class NoteUpdate(BaseModel):
    """Schema for updating a note.

    Attributes:
        title: Optional note title.
        content: Optional note content.
    """

    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate note title if provided.

        Args:
            v: Title value to validate.

        Returns:
            Validated title or None.

        Raises:
            ValueError: If title is empty or exceeds max length.
        """
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty or whitespace")
            if len(v) > MAX_TITLE_LENGTH:
                raise ValueError(f"Title cannot exceed {MAX_TITLE_LENGTH} characters")
            return v.strip()
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate note content if provided.

        Args:
            v: Content value to validate.

        Returns:
            Validated content or None.

        Raises:
            ValueError: If content is empty.
        """
        if v is not None:
            if not v.strip():
                raise ValueError("Content cannot be empty or whitespace")
            return v.strip()
        return v


class NoteRead(BaseModel):
    """Schema for reading a note from the database.

    Attributes:
        id: Note identifier.
        title: Note title.
        content: Note content.
    """

    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    """Schema for creating a new action item.

    Attributes:
        description: Action item description.
    """

    description: str

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate action item description is not empty.

        Args:
            v: Description value to validate.

        Returns:
            Validated description.

        Raises:
            ValueError: If description is empty.
        """
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class ActionItemUpdate(BaseModel):
    """Schema for updating an action item.

    Attributes:
        description: Optional action item description.
        completed: Optional completion status.
    """

    description: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate action item description if provided.

        Args:
            v: Description value to validate.

        Returns:
            Validated description or None.

        Raises:
            ValueError: If description is empty.
        """
        if v is not None:
            if not v.strip():
                raise ValueError("Description cannot be empty or whitespace")
            return v.strip()
        return v


class ActionItemRead(BaseModel):
    """Schema for reading an action item from the database.

    Attributes:
        id: Action item identifier.
        description: Action item description.
        completed: Completion status.
    """

    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True
