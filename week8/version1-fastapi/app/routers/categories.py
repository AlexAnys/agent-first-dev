from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryPatch, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[CategoryRead]:
    """List all categories with optional pagination and sorting."""
    stmt = select(Category)

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Category, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Category, sort_field)))
    else:
        stmt = stmt.order_by(desc(Category.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [CategoryRead.model_validate(row) for row in rows]


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    """Create a new category."""
    try:
        # Check if category with same name already exists
        existing_category = db.query(Category).filter(Category.name.ilike(payload.name)).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error_code": "DUPLICATE", "message": f"Category with name '{payload.name}' already exists"},
            )
        
        category = Category(name=payload.name, description=payload.description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return CategoryRead.model_validate(category)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CREATE_ERROR", "message": f"Failed to create category: {str(e)}"},
        )


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryRead:
    """Get a single category by ID."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Category with id {category_id} not found"},
        )
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
def patch_category(category_id: int, payload: CategoryPatch, db: Session = Depends(get_db)) -> CategoryRead:
    """Partially update a category."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Category with id {category_id} not found"},
        )
    
    try:
        # Check for duplicate name if name is being updated
        if payload.name is not None:
            existing_category = db.query(Category).filter(
                Category.name.ilike(payload.name),
                Category.id != category_id
            ).first()
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"error_code": "DUPLICATE", "message": f"Category with name '{payload.name}' already exists"},
                )
            category.name = payload.name
        
        if payload.description is not None:
            category.description = payload.description
        
        db.commit()
        db.refresh(category)
        return CategoryRead.model_validate(category)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update category: {str(e)}"},
        )


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    """Fully update a category (replace all fields)."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Category with id {category_id} not found"},
        )
    
    try:
        # Check for duplicate name if name is being changed
        if payload.name.lower() != category.name.lower():
            existing_category = db.query(Category).filter(Category.name.ilike(payload.name)).first()
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"error_code": "DUPLICATE", "message": f"Category with name '{payload.name}' already exists"},
                )
        
        category.name = payload.name
        category.description = payload.description
        
        db.commit()
        db.refresh(category)
        return CategoryRead.model_validate(category)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "UPDATE_ERROR", "message": f"Failed to update category: {str(e)}"},
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a category by ID."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": f"Category with id {category_id} not found"},
        )
    
    try:
        db.delete(category)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "DELETE_ERROR", "message": f"Failed to delete category: {str(e)}"},
        )
