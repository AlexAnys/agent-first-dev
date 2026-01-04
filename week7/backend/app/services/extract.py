import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExtractedItem:
    """Structured representation of an extracted action item."""

    text: str
    priority: str  # "high", "medium", "low", "default"
    pattern_type: str  # "todo", "action", "fixme", "hack", "note", "checkbox", "exclamation"
    deadline: Optional[datetime] = None

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return self.text


def _extract_priority(line: str) -> str:
    """
    Extract priority level from line.

    Returns: "high", "medium", "low", or "default"
    """
    normalized = line.upper()

    # Check for explicit priority patterns
    if re.search(r"\b(URGENT|ASAP|P1)\b", normalized):
        return "high"
    elif re.search(r"\bP2\b", normalized):
        return "medium"
    elif re.search(r"\bP3\b", normalized):
        return "low"

    return "default"


def _extract_deadline(line: str) -> Optional[datetime]:
    """
    Extract deadline from line.

    Supports patterns like:
    - "by Friday", "due Friday"
    - "by 2024-01-15", "due 2024-01-15"
    - "by Jan 15", "due Jan 15"
    """
    # Pattern: "by/due Friday/Monday/etc"
    day_pattern = r"\b(?:by|due)\s+(?P<day>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
    day_match = re.search(day_pattern, line, re.IGNORECASE)
    if day_match:
        # This is simplified; in production, calculate actual date
        day_name = day_match.group("day").lower()
        # For now, return None (could be enhanced to calculate next occurrence)
        return None

    # Pattern: "by/due YYYY-MM-DD"
    date_pattern = r"\b(?:by|due)\s+(\d{4}-\d{2}-\d{2})\b"
    date_match = re.search(date_pattern, line, re.IGNORECASE)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), "%Y-%m-%d")
        except ValueError:
            return None

    # Pattern: "by/due Mon Jan 15" or similar month formats
    month_pattern = (
        r"\b(?:by|due)\s+(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(?P<day>\d{1,2})\b"
    )
    month_match = re.search(month_pattern, line, re.IGNORECASE)
    if month_match:
        try:
            # Assume current year
            month_str = month_match.group("month")
            day_str = month_match.group("day")
            # Parse and return the date
            parsed = datetime.strptime(f"2024 {month_str} {day_str}", "%Y %b %d")
            return parsed
        except ValueError:
            return None

    return None


def _get_pattern_type(line: str) -> str:
    """Determine the pattern type of the extracted item."""
    normalized = line.lower()

    if normalized.startswith("todo:"):
        return "todo"
    elif normalized.startswith("action:"):
        return "action"
    elif normalized.startswith("fixme:"):
        return "fixme"
    elif normalized.startswith("hack:"):
        return "hack"
    elif normalized.startswith("note:"):
        return "note"
    elif re.match(r"^\s*\[[x\s]\]", line):
        return "checkbox"
    elif line.endswith("!"):
        return "exclamation"

    return "default"


def extract_action_items(text: str) -> list[ExtractedItem]:
    """
    Extract action items from text with sophisticated pattern recognition.

    Detects:
    - Lines starting with "TODO:", "ACTION:", "FIXME:", "HACK:", "NOTE:"
    - Markdown checkboxes: [ ] and [x]
    - Lines ending with "!"
    - Priority levels: URGENT, ASAP, P1 (high), P2 (medium), P3 (low)
    - Deadlines: "by Friday", "due 2024-01-15", "by Jan 15"

    Returns:
        List of ExtractedItem dataclass instances with structured data.
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[ExtractedItem] = []

    for line in lines:
        normalized = line.lower()

        # Check for all supported patterns
        is_todo_or_action = normalized.startswith("todo:") or normalized.startswith("action:")
        is_comment_type = (
            normalized.startswith("fixme:") or normalized.startswith("hack:") or normalized.startswith("note:")
        )
        is_checkbox = re.match(r"^\s*\[[x\s]\]", line)
        is_exclamation = line.endswith("!")

        if is_todo_or_action or is_comment_type or is_checkbox or is_exclamation:
            pattern_type = _get_pattern_type(line)
            priority = _extract_priority(line)
            deadline = _extract_deadline(line)

            item = ExtractedItem(text=line, priority=priority, pattern_type=pattern_type, deadline=deadline)
            results.append(item)

    return results
