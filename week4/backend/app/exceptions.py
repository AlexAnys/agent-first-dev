"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class ResourceNotFoundError(HTTPException):
    """Exception raised when a requested resource is not found.

    Attributes:
        resource_name: Name of the resource type (e.g., "Note", "Action item").
        resource_id: ID of the resource that was not found.
    """

    def __init__(self, resource_name: str, resource_id: int | str) -> None:
        """Initialize ResourceNotFoundError.

        Args:
            resource_name: Name of the resource type.
            resource_id: ID of the resource that was not found.
        """
        detail = f"{resource_name} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DatabaseError(Exception):
    """Exception raised when a database operation fails.

    Attributes:
        message: Description of the error.
    """

    def __init__(self, message: str = "Database operation failed") -> None:
        """Initialize DatabaseError.

        Args:
            message: Description of the error.
        """
        self.message = message
        super().__init__(self.message)
