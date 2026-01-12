from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..constants import HTTP_201_CREATED
from ..db import get_db
from ..logging_config import get_logger
from ..schemas import ActionItemCreate, ActionItemRead, ActionItemUpdate
from ..services import ActionItemService

router = APIRouter(prefix="/action-items", tags=["action_items"])
action_item_service = ActionItemService()
logger = get_logger(__name__)


@router.get("/", response_model=list[ActionItemRead])
def list_action_items(
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by status: pending, completed, or all (default)"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> list[ActionItemRead]:
    """Retrieve all action items from the database with optional status filter and pagination.

    Args:
        status_filter: Filter by completion status (pending/completed/all).
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 100, max: 1000).
        db: Database session dependency.

    Returns:
        List of all action items.
    """
    logger.info(f"Listing action items with status={status_filter}, skip={skip}, limit={limit}")
    items = action_item_service.get_all_action_items(
        db, status=status_filter, skip=skip, limit=limit
    )
    logger.info(f"Retrieved {len(items)} action items")
    return items


@router.post("/", response_model=ActionItemRead, status_code=HTTP_201_CREATED)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    """Create a new action item.

    Args:
        payload: Action item creation data containing description.
        db: Database session dependency.

    Returns:
        The newly created action item.
    """
    logger.info(f"Creating action item with description='{payload.description}'")
    item = action_item_service.create_action_item(db, payload)
    logger.info(f"Created action item with id={item.id}")
    return item


@router.get("/{item_id}", response_model=ActionItemRead)
def get_action_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    """Retrieve a specific action item by ID.

    Args:
        item_id: ID of the action item to retrieve.
        db: Database session dependency.

    Returns:
        The requested action item.

    Raises:
        ResourceNotFoundError: If the action item is not found.
    """
    from ..models import ActionItem
    from ..utils import get_or_404, to_schema

    logger.info(f"Retrieving action item with id={item_id}")
    item = get_or_404(db, ActionItem, item_id, "Action item")
    logger.info(f"Retrieved action item with id={item_id}")
    return to_schema(item, ActionItemRead)


@router.put("/{item_id}", response_model=ActionItemRead)
def update_item(
    item_id: int, payload: ActionItemUpdate, db: Session = Depends(get_db)
) -> ActionItemRead:
    """Update an action item.

    Args:
        item_id: ID of the action item to update.
        payload: Action item update data (description and/or completed status).
        db: Database session dependency.

    Returns:
        The updated action item.

    Raises:
        ResourceNotFoundError: If the action item is not found.
    """
    logger.info(f"Updating action item with id={item_id}")
    item = action_item_service.update_action_item(db, item_id, payload)
    logger.info(f"Updated action item with id={item_id}")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an action item.

    Args:
        item_id: ID of the action item to delete.
        db: Database session dependency.

    Raises:
        ResourceNotFoundError: If the action item is not found.
    """
    logger.info(f"Deleting action item with id={item_id}")
    action_item_service.delete_action_item(db, item_id)
    logger.info(f"Deleted action item with id={item_id}")


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    """Mark an action item as completed.

    Args:
        item_id: ID of the action item to complete.
        db: Database session dependency.

    Returns:
        The updated action item.

    Raises:
        ResourceNotFoundError: If the action item is not found.
    """
    logger.info(f"Completing action item with id={item_id}")
    item = action_item_service.complete_action_item(db, item_id)
    logger.info(f"Completed action item with id={item_id}")
    return item
