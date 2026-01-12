from typing import Optional

from sqlalchemy.orm import Session

from ..models import ActionItem
from ..repositories import ActionItemRepository
from ..schemas import ActionItemCreate, ActionItemRead, ActionItemUpdate
from ..utils import get_or_404, to_schema, to_schema_list


class ActionItemService:
    """Service layer for ActionItem business logic."""

    def __init__(self):
        """Initialize ActionItemService with repository."""
        self.repository = ActionItemRepository()

    def get_all_action_items(
        self, db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> list[ActionItemRead]:
        """Retrieve all action items with optional status filter and pagination.

        Args:
            db: Database session.
            status: Optional status filter ("pending", "completed", or None for all).
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of all action items.
        """
        completed = None
        if status == "completed":
            completed = True
        elif status == "pending":
            completed = False

        items = self.repository.filter_by_status(db, completed=completed, skip=skip, limit=limit)
        return to_schema_list(items, ActionItemRead)

    def create_action_item(self, db: Session, payload: ActionItemCreate) -> ActionItemRead:
        """Create a new action item.

        Args:
            db: Database session.
            payload: Action item creation data.

        Returns:
            Newly created action item.
        """
        item = self.repository.create(db, description=payload.description, completed=False)
        return to_schema(item, ActionItemRead)

    def update_action_item(
        self, db: Session, item_id: int, payload: ActionItemUpdate
    ) -> ActionItemRead:
        """Update an action item.

        Args:
            db: Database session.
            item_id: Action item identifier.
            payload: Action item update data.

        Returns:
            Updated action item.

        Raises:
            ResourceNotFoundError: If action item not found.
        """
        item = get_or_404(db, ActionItem, item_id, "Action item")
        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            updated_item = self.repository.update(db, item, **update_data)
            return to_schema(updated_item, ActionItemRead)
        return to_schema(item, ActionItemRead)

    def delete_action_item(self, db: Session, item_id: int) -> None:
        """Delete an action item.

        Args:
            db: Database session.
            item_id: Action item identifier.

        Raises:
            ResourceNotFoundError: If action item not found.
        """
        item = get_or_404(db, ActionItem, item_id, "Action item")
        self.repository.delete(db, item)

    def complete_action_item(self, db: Session, item_id: int) -> ActionItemRead:
        """Mark an action item as completed.

        Args:
            db: Database session.
            item_id: Action item identifier.

        Returns:
            Updated action item.

        Raises:
            ResourceNotFoundError: If action item not found.
        """
        item = get_or_404(db, ActionItem, item_id, "Action item")
        updated_item = self.repository.update(db, item, completed=True)
        return to_schema(updated_item, ActionItemRead)
