"""Utility functions for common operations."""

from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from .exceptions import ResourceNotFoundError

T = TypeVar("T")
SchemaT = TypeVar("SchemaT", bound=BaseModel)


def to_schema(model_instance: T, schema_class: type[SchemaT]) -> SchemaT:
    """Convert a SQLAlchemy model instance to a Pydantic schema.

    Args:
        model_instance: SQLAlchemy model instance to convert.
        schema_class: Pydantic schema class to convert to.

    Returns:
        Pydantic schema instance.
    """
    return schema_class.model_validate(model_instance)


def to_schema_list(model_instances: list[T], schema_class: type[SchemaT]) -> list[SchemaT]:
    """Convert a list of SQLAlchemy model instances to Pydantic schemas.

    Args:
        model_instances: List of SQLAlchemy model instances to convert.
        schema_class: Pydantic schema class to convert to.

    Returns:
        List of Pydantic schema instances.
    """
    return [schema_class.model_validate(instance) for instance in model_instances]


def get_or_404(db: Session, model_class: type[T], resource_id: Any, resource_name: str) -> T:
    """Retrieve a model instance by ID or raise 404 error if not found.

    Args:
        db: Database session.
        model_class: SQLAlchemy model class.
        resource_id: ID of the resource to retrieve.
        resource_name: Name of the resource for error message.

    Returns:
        Model instance if found.

    Raises:
        ResourceNotFoundError: If the resource is not found.
    """
    instance = db.get(model_class, resource_id)
    if not instance:
        raise ResourceNotFoundError(resource_name, resource_id)
    return instance
