from __future__ import annotations

import re
import json
from typing import List

from ollama import chat

from ..config import settings
from ..schemas import LLMActionItem, LLMActionItemList


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    """Extract action items from text using rule-based approach."""
    lines = text.splitlines()
    extracted: List[str] = []
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    
    # Fallback: if nothing matched, heuristically split into sentences
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    imperative_starters = {
        "add", "create", "implement", "fix", "update",
        "write", "check", "verify", "refactor", "document",
        "design", "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> List[str]:
    """Extract action items from text using LLM."""
    try:
        response = chat(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an assistant that extracts action items from text.
Extract all action items, tasks, or to-dos from the given text.
Return them as a JSON object with an "items" array containing objects with "action" field.
Example: {"items": [{"action": "Review the document"}, {"action": "Send email to team"}]}"""
                },
                {
                    "role": "user",
                    "content": f"Extract action items from this text:\n\n{text}"
                }
            ],
            format="json",
            options={"temperature": settings.LLM_TEMPERATURE}
        )
        
        result = json.loads(response.message.content)
        action_list = LLMActionItemList(**result)
        
        return [item.action for item in action_list.items]
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e
    except Exception as e:
        raise RuntimeError(f"LLM extraction failed: {e}") from e
