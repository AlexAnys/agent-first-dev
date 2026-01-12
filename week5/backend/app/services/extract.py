import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_hashtags(text: str) -> list[str]:
    """Extract normalized hashtag names from arbitrary text.

    Rules:
    - Match words starting with '#', composed of letters/digits/underscore.
    - Normalize to lowercase.
    - Return unique names in first-seen order.
    """
    raw_tags = re.findall(r"#(\w+)", text)
    seen: set[str] = set()
    result: list[str] = []
    for raw in raw_tags:
        name = raw.lower()
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return result
