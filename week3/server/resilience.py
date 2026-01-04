"""Resilience utilities using Tenacity for retry with exponential backoff."""
import asyncio
from typing import Callable, TypeVar, Optional, Any
from googleapiclient.errors import HttpError
from fastmcp.exceptions import ToolError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryCallState,
    AsyncRetrying,
)
from .logger import logger

T = TypeVar("T")

# Error message mapping for user-friendly responses
ERROR_MESSAGES = {
    401: "Authentication required. Please re-authenticate with Gmail.",
    403: "Access denied. Check Gmail API permissions.",
    404: "Message not found. It may have been deleted.",
    429: "Rate limit exceeded. Please wait a moment and try again.",
    500: "Gmail service error. Retrying...",
    503: "Gmail service temporarily unavailable. Retrying...",
}


def get_error_message(status_code: int, default: str = "Gmail API error") -> str:
    """Map HTTP status to user-friendly message."""
    return ERROR_MESSAGES.get(status_code, default)


def is_retryable_error(status_code: int) -> bool:
    """Check if error is retryable (rate limit or server error)."""
    return status_code == 429 or status_code >= 500


def is_retryable_exception(exception: BaseException) -> bool:
    """Determine if an exception should trigger a retry.

    Retryable conditions:
    - HttpError with status 429 (rate limit) or 5xx (server errors)
    - TimeoutError / asyncio.TimeoutError
    - ConnectionError (network issues)
    """
    if isinstance(exception, HttpError):
        return is_retryable_error(exception.resp.status)
    if isinstance(exception, (TimeoutError, asyncio.TimeoutError, ConnectionError)):
        return True
    return False


def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Custom logging callback for retry attempts."""
    exception = retry_state.outcome.exception()
    attempt = retry_state.attempt_number

    if isinstance(exception, HttpError):
        logger.warning(
            f"Gmail API error (attempt {attempt}): "
            f"status={exception.resp.status}, reason={exception.reason}"
        )
    elif isinstance(exception, (TimeoutError, asyncio.TimeoutError)):
        logger.warning(f"Request timeout (attempt {attempt})")
    elif isinstance(exception, ConnectionError):
        logger.warning(f"Connection error (attempt {attempt}): {exception}")
    else:
        logger.warning(f"Retry attempt {attempt}: {type(exception).__name__}: {exception}")


def raise_non_retryable_error(retry_state: RetryCallState) -> None:
    """Callback to handle non-retryable errors immediately."""
    exception = retry_state.outcome.exception()
    if isinstance(exception, HttpError) and not is_retryable_error(exception.resp.status):
        raise ToolError(get_error_message(exception.resp.status, str(exception)))


def gmail_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
) -> Callable:
    """Create a customized Tenacity retry decorator for Gmail API calls.

    Features:
    - Exponential backoff with configurable min/max wait times
    - Retries only on transient errors (429, 5xx, timeouts, connection errors)
    - Raises ToolError immediately for non-retryable errors (401, 403, 404)
    - Detailed logging for each retry attempt

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time between retries in seconds (default: 1.0)
        max_wait: Maximum wait time between retries in seconds (default: 30.0)

    Returns:
        Configured retry decorator

    Example:
        @gmail_retry(max_attempts=5, min_wait=2.0)
        async def fetch_messages():
            ...
    """
    return retry(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=log_retry_attempt,
        reraise=True,
    )


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0
) -> Callable:
    """Alias for gmail_retry for backward compatibility.

    Deprecated: Use gmail_retry() instead.
    """
    return gmail_retry(
        max_attempts=max_retries,
        min_wait=base_delay,
        max_wait=max_delay,
    )


async def retry_async_operation(
    operation: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    **kwargs: Any,
) -> T:
    """Execute an async operation with retry logic.

    Useful for one-off retry scenarios without using a decorator.

    Args:
        operation: Async callable to execute
        *args: Positional arguments for the operation
        max_attempts: Maximum retry attempts
        min_wait: Minimum wait between retries
        max_wait: Maximum wait between retries
        **kwargs: Keyword arguments for the operation

    Returns:
        Result of the operation

    Raises:
        ToolError: If all retries exhausted or non-retryable error occurs
    """
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=log_retry_attempt,
        reraise=True,
    ):
        with attempt:
            return await operation(*args, **kwargs)


def handle_empty_results(results: list, query: str) -> Optional[dict]:
    """Handle empty search results gracefully.

    Args:
        results: List of search results
        query: The search query that produced the results

    Returns:
        Empty result dict if no results, None otherwise
    """
    if not results:
        logger.info(f"No messages found for query: {query}")
        return {
            "messages": [],
            "resultCount": 0,
            "hasMore": False,
            "message": "No messages found matching your query."
        }
    return None
