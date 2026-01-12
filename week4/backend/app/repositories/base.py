from typing import Generic, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations.

    Attributes:
        model: SQLAlchemy model class.
    """

    def __init__(self, model: type[ModelType]):
        """Initialize repository with a model class.

        Args:
            model: SQLAlchemy model class to use for operations.
        """
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """Retrieve a single record by ID.

        Args:
            db: Database session.
            id: Record identifier.

        Returns:
            Model instance if found, None otherwise.
        """
        return db.execute(select(self.model).where(self.model.id == id)).scalar_one_or_none()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Retrieve all records with pagination.

        Args:
            db: Database session.
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of model instances.
        """
        return db.execute(select(self.model).offset(skip).limit(limit)).scalars().all()

    def create(self, db: Session, **kwargs) -> ModelType:
        """Create a new record.

        Args:
            db: Database session.
            **kwargs: Field values for the new record.

        Returns:
            Newly created model instance.
        """
        instance = self.model(**kwargs)
        db.add(instance)
        db.flush()
        db.refresh(instance)
        return instance

    def update(self, db: Session, instance: ModelType, **kwargs) -> ModelType:
        """Update an existing record.

        Args:
            db: Database session.
            instance: Model instance to update.
            **kwargs: Fields to update.

        Returns:
            Updated model instance.
        """
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.add(instance)
        db.flush()
        db.refresh(instance)
        return instance

    def delete(self, db: Session, instance: ModelType) -> None:
        """Delete a record.

        Args:
            db: Database session.
            instance: Model instance to delete.
        """
        db.delete(instance)
        db.flush()
