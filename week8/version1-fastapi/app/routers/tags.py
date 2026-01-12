from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..schemas import TagCreate, TagPatch, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def list_tags(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[TagRead]:
    """List all tags with optional pagination and sorting."""
    stmt = select(Tag)

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Tag, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Tag, sort_field)))
    else:
        stmt = stmt.order_by(desc(Tag.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    """Create a new tag."""
    try:
        # Check if tag with same name already exists (case-insensitive)
        existing_tag = db.query(Tag).filter(Tag.name.ilike(payload.name)).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error_code": "DUPLICATE", "message": f"Tag with name '{payload.name}' already exists"},
            )
        
        tag = Tag(name=payload.name, color=payload.color)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return TagRead.model_validate(tag)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CREATE_ERROR", "message": f"Failed to create tag: {str(e)}"},
        )


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)) -> TagRead:
    """Get a single tag by ID."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Tag with id {tag_id} not found"},
        )
    return TagRead.model_validate(tag)


@router.patch("/{tag_id}", response_model=TagRead)
def patch_tag(tag_id: int, payload: TagPatch, db: Session = Depends(get_db)) -> TagRead:
    """Partially update a tag."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Tag with id {tag_id} not found"},
        )
    
    try:
        # Check for duplicate name if name is being updated
        if payload.name is not None:
            existing_tag = db.query(Tag).filter(
                Tag.name.ilike(payload.name),
                Tag.id != tag_id
            ).first()
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"error_code": "DUPLICATE", "message": f"Tag with name '{payload.name}' already exists"},
                )
            tag.name = payload.name
        
        if payload.color is not None:
            tag.color = payload.color
        
        db.commit()
        db.refresh(tag)
        return TagRead.model_validate(tag)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update tag: {str(e)}"},
        )


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    """Fully update a tag (replace all fields)."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Tag with id {tag_id} not found"},
        )
    
    try:
        # Check for duplicate name if name is being changed
        if payload.name.lower() != tag.name.lower():
            existing_tag = db.query(Tag).filter(Tag.name.ilike(payload.name)).first()
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"error_code": "DUPLICATE", "message": f"Tag with name '{payload.name}' already exists"},
                )
        
        tag.name = payload.name
        tag.color = payload.color
        
        db.commit()
        db.refresh(tag)
        return TagRead.model_validate(tag)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update tag: {str(e)}"},
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a tag by ID."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Tag with id {tag_id} not found"},
        )
    
    try:
        db.delete(tag)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "DELETE_ERROR", "message": f"Failed to delete tag: {str(e)}"},
        )
