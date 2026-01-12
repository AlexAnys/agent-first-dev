from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ActionItem
from .base import BaseRepository


class ActionItemRepository(BaseRepository[ActionItem]):
    """Repository for ActionItem model with specific query methods."""

    def __init__(self):
        """Initialize ActionItemRepository with ActionItem model."""
        super().__init__(ActionItem)

    def filter_by_status(
        self, db: Session, completed: Optional[bool] = None, skip: int = 0, limit: int = 100
    ) -> list[ActionItem]:
        """Filter action items by completion status with pagination.

        Args:
            db: Database session.
            completed: Optional completion status filter (True/False/None for all).
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of action items matching the filter.
        """
        query = select(ActionItem)
        if completed is not None:
            query = query.where(ActionItem.completed == completed)
        return db.execute(query.offset(skip).limit(limit)).scalars().all()
