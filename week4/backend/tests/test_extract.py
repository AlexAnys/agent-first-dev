from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_action_items_bracket_syntax():
    """Test extraction of action items using bracket syntax [ ] Task description."""
    text = """
    Meeting notes
    [ ] Buy groceries
    [ ] Call mom
    Some other text
    """.strip()
    items = extract_action_items(text)
    assert "Buy groceries" in items
    assert "Call mom" in items


def test_extract_action_items_parenthesis_syntax():
    """Test extraction of action items using parenthesis syntax ( ) Task description."""
    text = """
    Project planning
    ( ) Review PR
    ( ) Update docs
    Random text
    """.strip()
    items = extract_action_items(text)
    assert "Review PR" in items
    assert "Update docs" in items


def test_extract_action_items_mention_syntax():
    """Test extraction of action items using mention syntax @username task."""
    text = """
    Team updates
    @john fix bug
    @team weekly meeting
    @sarah review code
    """.strip()
    items = extract_action_items(text)
    assert "fix bug" in items
    assert "weekly meeting" in items
    assert "review code" in items


def test_extract_action_items_mixed_syntaxes():
    """Test extraction with multiple syntax patterns in same text."""
    text = """
    TODO: write tests
    [ ] Buy groceries
    ( ) Review PR
    @john fix bug
    Ship it!
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Buy groceries" in items
    assert "Review PR" in items
    assert "fix bug" in items
    assert "Ship it!" in items
