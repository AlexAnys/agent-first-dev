import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_returns_list():
    """LLM 함수가 리스트를 반환하는지 확인"""
    text = "Please review the document and send feedback by Friday."
    
    items = extract_action_items_llm(text)
    
    assert isinstance(items, list)


def test_extract_action_items_llm_returns_strings():
    """반환된 리스트의 각 항목이 문자열인지 확인"""
    text = """
    Meeting notes:
    - Review the PR
    - Update documentation
    - Schedule next meeting
    """
    
    items = extract_action_items_llm(text)
    
    assert all(isinstance(item, str) for item in items)


def test_extract_action_items_llm_non_empty_for_action_text():
    """액션 아이템이 포함된 텍스트에서 비어있지 않은 결과 반환"""
    text = """
    TODO: Fix the bug in authentication module.
    Action: Deploy to staging server.
    Next: Write unit tests for the new feature.
    """
    
    items = extract_action_items_llm(text)
    
    assert len(items) > 0


def test_extract_action_items_llm_items_not_empty_strings():
    """반환된 각 항목이 빈 문자열이 아닌지 확인"""
    text = "Create a new branch and implement the login feature."
    
    items = extract_action_items_llm(text)
    
    for item in items:
        assert item.strip() != ""
