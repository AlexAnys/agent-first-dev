import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    items = []
    for line in lines:
        # Lines ending with !
        if line.endswith("!"):
            items.append(line)
        # Lines starting with TODO:
        elif line.lower().startswith("todo:"):
            items.append(line)
        # Bracket syntax: [ ] Task description
        elif line.startswith("[ ]"):
            items.append(line[3:].strip())
        # Parenthesis syntax: ( ) Task description
        elif line.startswith("( )"):
            items.append(line[3:].strip())
        # Mention syntax: @username task
        elif re.match(r"^@\w+\s", line):
            match = re.match(r"^@(\w+)\s+(.*)$", line)
            if match:
                items.append(match.group(2))
    return items
