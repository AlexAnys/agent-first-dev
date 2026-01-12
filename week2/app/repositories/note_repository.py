from __future__ import annotations

import sqlite3
from typing import List, Optional

from .base import db
from ..schemas import NoteResponse


class NoteRepository:
    """Repository for Note CRUD operations."""
    
    @staticmethod
    def create(content: str) -> int:
        """Create a new note and return its ID."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
                conn.commit()
                return int(cursor.lastrowid)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create note: {e}") from e
    
    @staticmethod
    def get_by_id(note_id: int) -> Optional[NoteResponse]:
        """Get a note by ID."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, content, created_at FROM notes WHERE id = ?",
                    (note_id,)
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                return NoteResponse(
                    id=row["id"],
                    content=row["content"],
                    created_at=row["created_at"]
                )
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to get note: {e}") from e
    
    @staticmethod
    def list_all() -> List[NoteResponse]:
        """List all notes ordered by ID descending."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
                rows = cursor.fetchall()
                return [
                    NoteResponse(
                        id=row["id"],
                        content=row["content"],
                        created_at=row["created_at"]
                    )
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to list notes: {e}") from e
