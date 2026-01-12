def extract_action_items(text: str) -> list[str]:
    """Extract action items from text based on specific patterns.

    Identifies lines that either end with "!" or start with "todo:"
    (case-insensitive) as action items.

    Args:
        text: Input text to extract action items from.

    Returns:
        List of extracted action item strings.
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]
