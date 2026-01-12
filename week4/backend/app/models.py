from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

from .constants import MAX_TITLE_LENGTH

Base = declarative_base()


class Note(Base):
    """SQLAlchemy model for notes.

    Attributes:
        id: Primary key identifier.
        title: Note title (max 200 characters).
        content: Note content text.
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(MAX_TITLE_LENGTH), nullable=False)
    content = Column(Text, nullable=False)


class ActionItem(Base):
    """SQLAlchemy model for action items.

    Attributes:
        id: Primary key identifier.
        description: Action item description text.
        completed: Completion status flag (default: False).
    """

    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
