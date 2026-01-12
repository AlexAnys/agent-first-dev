from week5.backend.app.services.extract import extract_action_items, extract_hashtags


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


def test_extract_hashtags_basic():
    text = "This note has #tag and #OtherTag in it."
    tags = extract_hashtags(text)
    assert tags == ["tag", "othertag"]


def test_extract_hashtags_ignores_duplicates_and_punctuation():
    text = "#tag, #tag! and also #second_tag."
    tags = extract_hashtags(text)
    assert tags == ["tag", "second_tag"]


def test_extract_hashtags_no_tags_returns_empty_list():
    text = "This note has no hashtags at all."
    tags = extract_hashtags(text)
    assert tags == []
