from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


# Association table for many-to-many relationship between Note and Tag
note_tag_association = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationship: Category has many Notes (one-to-many)
    notes = relationship("Note", back_populates="category")


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(20), nullable=True)  # Optional color for UI display

    # Relationship: Tag has many Notes through association table (many-to-many)
    notes = relationship("Note", secondary=note_tag_association, back_populates="tags")


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    # Note belongs to a Category (many-to-one)
    category = relationship("Category", back_populates="notes")

    # Note has many Tags (many-to-many)
    tags = relationship("Tag", secondary=note_tag_association, back_populates="notes")

    # Note has many ActionItems (one-to-many)
    action_items = relationship("ActionItem", back_populates="note", cascade="all, delete-orphan")


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relationship: ActionItem belongs to a Note (many-to-one)
    note = relationship("Note", back_populates="action_items")


