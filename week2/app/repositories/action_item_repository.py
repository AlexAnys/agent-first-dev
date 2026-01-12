from __future__ import annotations

import sqlite3
from typing import List, Optional

from .base import db
from ..schemas import ActionItemResponse


class ActionItemRepository:
    """Repository for ActionItem CRUD operations."""
    
    @staticmethod
    def create_many(items: List[str], note_id: Optional[int] = None) -> List[int]:
        """Create multiple action items and return their IDs."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ids: List[int] = []
                for item in items:
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id, item)
                    )
                    ids.append(int(cursor.lastrowid))
                conn.commit()
                return ids
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create action items: {e}") from e
    
    @staticmethod
    def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:
        """List action items, optionally filtered by note_id."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                if note_id is None:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                    )
                else:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                        (note_id,)
                    )
                rows = cursor.fetchall()
                return [
                    ActionItemResponse(
                        id=row["id"],
                        note_id=row["note_id"],
                        text=row["text"],
                        done=bool(row["done"]),
                        created_at=row["created_at"]
                    )
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to list action items: {e}") from e
    
    @staticmethod
    def mark_done(action_item_id: int, done: bool) -> None:
        """Mark an action item as done or not done."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE action_items SET done = ? WHERE id = ?",
                    (1 if done else 0, action_item_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to update action item: {e}") from e
