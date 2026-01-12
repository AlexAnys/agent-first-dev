from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    db: Session = Depends(get_db),
    completed: Optional[bool] = None,
    note_id: Optional[int] = Query(None, description="Filter by note ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[ActionItemRead]:
    """List all action items with optional filtering, pagination, and sorting."""
    stmt = select(ActionItem)
    
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))
    
    if note_id is not None:
        stmt = stmt.where(ActionItem.note_id == note_id)

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(ActionItem, sort_field):
        stmt = stmt.order_by(order_fn(getattr(ActionItem, sort_field)))
    else:
        stmt = stmt.order_by(desc(ActionItem.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    """Create a new action item with optional note association."""
    try:
        # Validate note if provided
        if payload.note_id is not None:
            note = db.get(Note, payload.note_id)
            if not note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error_code": "NOT_FOUND", "message": f"Note with id {payload.note_id} not found"},
                )
        
        item = ActionItem(
            description=payload.description,
            completed=False,
            note_id=payload.note_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return ActionItemRead.model_validate(item)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CREATE_ERROR", "message": f"Failed to create action item: {str(e)}"},
        )


@router.get("/{item_id}", response_model=ActionItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    """Get a single action item by ID."""
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Action item with id {item_id} not found"},
        )
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    """Mark an action item as completed."""
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Action item with id {item_id} not found"},
        )
    
    try:
        item.completed = True
        db.commit()
        db.refresh(item)
        return ActionItemRead.model_validate(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to complete action item: {str(e)}"},
        )


@router.patch("/{item_id}", response_model=ActionItemRead)
def patch_item(item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)) -> ActionItemRead:
    """Partially update an action item."""
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Action item with id {item_id} not found"},
        )
    
    try:
        if payload.description is not None:
            item.description = payload.description
        if payload.completed is not None:
            item.completed = payload.completed
        
        # Update note_id if provided
        if payload.note_id is not None:
            if payload.note_id == 0:  # Allow setting to None with 0
                item.note_id = None
            else:
                note = db.get(Note, payload.note_id)
                if not note:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"error_code": "NOT_FOUND", "message": f"Note with id {payload.note_id} not found"},
                    )
                item.note_id = payload.note_id
        
        db.commit()
        db.refresh(item)
        return ActionItemRead.model_validate(item)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update action item: {str(e)}"},
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an action item by ID."""
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Action item with id {item_id} not found"},
        )
    
    try:
        db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "DELETE_ERROR", "message": f"Failed to delete action item: {str(e)}"},
        )


