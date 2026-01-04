from datetime import datetime

import pytest

from backend.app.services.extract import ExtractedItem, extract_action_items


class TestBasicPatterns:
    """Test original patterns (TODO, ACTION, exclamation)."""

    def test_extract_todo(self):
        """Test TODO: pattern detection."""
        text = "TODO: write tests"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "TODO: write tests"
        assert items[0].pattern_type == "todo"
        assert isinstance(items[0], ExtractedItem)

    def test_extract_action(self):
        """Test ACTION: pattern detection."""
        text = "ACTION: review PR"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "ACTION: review PR"
        assert items[0].pattern_type == "action"

    def test_extract_exclamation(self):
        """Test lines ending with exclamation mark."""
        text = "Ship it!"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "Ship it!"
        assert items[0].pattern_type == "exclamation"

    def test_extract_multiple_basic_patterns(self):
        """Test multiple basic patterns in one text."""
        text = """
        This is a note
        - TODO: write tests
        - ACTION: review PR
        - Ship it!
        Not actionable
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 3
        assert items[0].text == "TODO: write tests"
        assert items[1].text == "ACTION: review PR"
        assert items[2].text == "Ship it!"

    def test_todo_case_insensitive(self):
        """Test that TODO is case insensitive."""
        text = "todo: lowercase"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].pattern_type == "todo"


class TestCommentPrefixes:
    """Test FIXME, HACK, NOTE prefixes."""

    def test_extract_fixme(self):
        """Test FIXME: pattern detection."""
        text = "FIXME: this needs fixing"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "FIXME: this needs fixing"
        assert items[0].pattern_type == "fixme"

    def test_extract_hack(self):
        """Test HACK: pattern detection."""
        text = "HACK: temporary workaround"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "HACK: temporary workaround"
        assert items[0].pattern_type == "hack"

    def test_extract_note(self):
        """Test NOTE: pattern detection."""
        text = "NOTE: important information"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "NOTE: important information"
        assert items[0].pattern_type == "note"

    def test_comment_prefixes_case_insensitive(self):
        """Test that comment prefixes work in various cases."""
        text = """
        fixme: lowercase
        Hack: capitalized
        NOTE: UPPERCASE
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 3
        assert items[0].pattern_type == "fixme"
        assert items[1].pattern_type == "hack"
        assert items[2].pattern_type == "note"


class TestCheckboxPatterns:
    """Test markdown checkbox detection."""

    def test_extract_unchecked_checkbox(self):
        """Test [ ] unchecked checkbox detection."""
        text = "[ ] Complete this task"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "[ ] Complete this task"
        assert items[0].pattern_type == "checkbox"

    def test_extract_checked_checkbox(self):
        """Test [x] checked checkbox detection."""
        text = "[x] Task completed"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].text == "[x] Task completed"
        assert items[0].pattern_type == "checkbox"

    def test_extract_checkbox_with_dash(self):
        """Test checkbox with list dash prefix."""
        text = "- [ ] Buy groceries"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].pattern_type == "checkbox"

    def test_extract_checked_checkbox_with_dash(self):
        """Test checked checkbox with list dash prefix."""
        text = "- [x] Done item"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].pattern_type == "checkbox"

    def test_extract_multiple_checkboxes(self):
        """Test multiple checkboxes in one text."""
        text = """
        [ ] Task one
        [x] Task two
        - [ ] Task three
        - [x] Task four
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 4
        assert all(item.pattern_type == "checkbox" for item in items)


class TestPriorityDetection:
    """Test priority level extraction."""

    def test_priority_urgent(self):
        """Test URGENT priority detection."""
        text = "TODO: URGENT fix the bug"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "high"

    def test_priority_asap(self):
        """Test ASAP priority detection."""
        text = "TODO: Fix this ASAP"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "high"

    def test_priority_p1(self):
        """Test P1 priority detection."""
        text = "TODO: important task P1"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "high"

    def test_priority_p2(self):
        """Test P2 priority detection."""
        text = "TODO: medium priority P2"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "medium"

    def test_priority_p3(self):
        """Test P3 priority detection."""
        text = "TODO: low priority P3"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "low"

    def test_priority_default(self):
        """Test default priority when no priority marker."""
        text = "TODO: regular task"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "default"

    def test_priority_multiple_items(self):
        """Test priority detection across multiple items."""
        text = """
        TODO: Task P1
        ACTION: Task P2
        FIXME: Task P3
        NOTE: Task URGENT
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 4
        assert items[0].priority == "high"
        assert items[1].priority == "medium"
        assert items[2].priority == "low"
        assert items[3].priority == "high"


class TestDeadlineExtraction:
    """Test deadline pattern extraction."""

    def test_deadline_iso_date(self):
        """Test ISO date deadline extraction."""
        text = "TODO: due 2024-01-15"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].deadline is not None
        assert items[0].deadline.year == 2024
        assert items[0].deadline.month == 1
        assert items[0].deadline.day == 15

    def test_deadline_by_iso_date(self):
        """Test 'by' keyword with ISO date."""
        text = "ACTION: by 2024-12-31"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].deadline is not None
        assert items[0].deadline.year == 2024
        assert items[0].deadline.month == 12
        assert items[0].deadline.day == 31

    def test_deadline_month_day(self):
        """Test month-day deadline extraction."""
        text = "TODO: due Jan 15"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].deadline is not None
        assert items[0].deadline.month == 1
        assert items[0].deadline.day == 15

    def test_deadline_by_month_day(self):
        """Test 'by' keyword with month-day."""
        text = "FIXME: by Feb 28"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].deadline is not None
        assert items[0].deadline.month == 2
        assert items[0].deadline.day == 28

    def test_deadline_various_months(self):
        """Test deadline extraction with various months."""
        text = """
        TODO: due Mar 01
        ACTION: by Jun 30
        FIXME: due Dec 25
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 3
        assert all(item.deadline is not None for item in items)
        assert items[0].deadline.month == 3
        assert items[1].deadline.month == 6
        assert items[2].deadline.month == 12

    def test_no_deadline(self):
        """Test items without deadline."""
        text = "TODO: no deadline here"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].deadline is None

    def test_deadline_with_priority(self):
        """Test deadline combined with priority."""
        text = "TODO: URGENT P1 due 2024-01-15"
        items = extract_action_items(text)
        assert len(items) == 1
        assert items[0].priority == "high"
        assert items[0].deadline is not None


class TestExtractedItemDataclass:
    """Test ExtractedItem dataclass behavior."""

    def test_extracted_item_str(self):
        """Test ExtractedItem string representation."""
        item = ExtractedItem(text="TODO: test", priority="high", pattern_type="todo")
        assert str(item) == "TODO: test"

    def test_extracted_item_fields(self):
        """Test all ExtractedItem fields."""
        deadline = datetime(2024, 1, 15)
        item = ExtractedItem(text="TODO: test", priority="high", pattern_type="todo", deadline=deadline)
        assert item.text == "TODO: test"
        assert item.priority == "high"
        assert item.pattern_type == "todo"
        assert item.deadline == deadline


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_mixed_patterns_with_all_features(self):
        """Test complex text with mixed patterns, priorities, and deadlines."""
        text = """
        TODO: URGENT fix login bug P1 due 2024-01-10
        - [ ] Complete unit tests
        ACTION: review changes ASAP
        FIXME: refactor database code by Jan 20
        - [x] Deploy to staging
        NOTE: Remember to notify team
        Ship it!
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 7

        # Check first item
        assert items[0].pattern_type == "todo"
        assert items[0].priority == "high"
        assert items[0].deadline is not None

        # Check checkbox
        checkbox_items = [i for i in items if i.pattern_type == "checkbox"]
        assert len(checkbox_items) == 2

    def test_empty_text(self):
        """Test with empty text."""
        text = ""
        items = extract_action_items(text)
        assert len(items) == 0

    def test_text_with_no_patterns(self):
        """Test with text containing no action items."""
        text = """
        This is just regular text
        with multiple lines
        but no action items
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 0

    def test_whitespace_handling(self):
        """Test handling of various whitespace."""
        text = """

        TODO: task one

        - ACTION: task two

        """
        items = extract_action_items(text)
        assert len(items) == 2

    def test_priority_case_insensitive(self):
        """Test priority detection is case insensitive."""
        text = """
        TODO: lowercase urgent
        ACTION: MixedCase AsAp
        FIXME: UPPERCASE P1
        """.strip()
        items = extract_action_items(text)
        assert all(item.priority == "high" for item in items)

    def test_deadline_case_insensitive(self):
        """Test deadline detection is case insensitive."""
        text = """
        TODO: DUE 2024-01-15
        ACTION: By 2024-02-20
        """.strip()
        items = extract_action_items(text)
        assert all(item.deadline is not None for item in items)

    def test_real_world_code_comment(self):
        """Test extraction from real-world code comment."""
        text = """
        TODO: URGENT refactor this function P1 by 2024-01-15
        HACK: temporary fix for issue #123
        NOTE: Remember to update documentation
        FIXME: performance bottleneck
        """.strip()
        items = extract_action_items(text)
        assert len(items) == 4
        assert items[0].priority == "high"
        assert items[0].deadline is not None
        assert items[1].pattern_type == "hack"

    def test_real_world_markdown(self):
        """Test extraction from real-world markdown."""
        text = """
        # Project Tasks

        [ ] Write documentation P1
        [x] Setup CI/CD pipeline
        - [ ] Review pull requests ASAP due 2024-01-10

        ## Notes
        NOTE: This is important information
        ACTION: follow up with team
        """.strip()
        items = extract_action_items(text)
        assert len(items) >= 4
        checkboxes = [i for i in items if i.pattern_type == "checkbox"]
        assert len(checkboxes) >= 2
