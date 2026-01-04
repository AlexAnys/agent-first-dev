# Week 2 Implementation Plan

This document outlines the detailed implementation plan for each TODO in the Week 2 assignment. The plan uses **llama3.1:8b** as the LLM model via Ollama.

---

## Configuration

- **Model**: `llama3.1:8b`
- **Ollama Host**: `http://10.23.38.9:11434` (configured in `.env`)

---

## TODO 1: Scaffold a New Feature - LLM-Powered Action Item Extraction

### Objective
Implement `extract_action_items_llm()` function in `week2/app/services/extract.py` that uses Ollama with `llama3.1:8b` to extract action items from text.

### Implementation Steps

#### Step 1.1: Environment Setup
- **File**: `week2/.env`
- Create `.env` file with Ollama host configuration:
  ```
  OLLAMA_HOST=http://10.23.38.9:11434
  ```

#### Step 1.2: Install Dependencies
Ensure `ollama` Python package is installed:
```bash
uv add ollama python-dotenv
```

#### Step 1.3: Implement `extract_action_items_llm()` Function
- **File**: `week2/app/services/extract.py`
- **Location**: After the existing `extract_action_items()` function

```python
from pydantic import BaseModel
from ollama import chat
import os

# Define structured output schema
class ActionItemsResponse(BaseModel):
    action_items: list[str]

def extract_action_items_llm(text: str, model: str = "llama3.1:8b") -> list[str]:
    """
    Extract action items from text using LLM (Ollama).
    
    Args:
        text: The input text to extract action items from
        model: The Ollama model to use (default: llama3.1:8b)
    
    Returns:
        List of extracted action items as strings
    """
    if not text.strip():
        return []
    
    prompt = f"""Analyze the following text and extract all action items, tasks, or to-dos.
Return ONLY the action items as a JSON array of strings. Use compact single-line JSON with double quotes. Each action item should be clear and actionable.

Text:
{text}

Extract action items and return as JSON array of strings. If no action items found, return an empty array."""

    try:
        response = chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts action items from text. Always respond with valid JSON containing an array of action item strings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format=ActionItemsResponse.model_json_schema(),
        )
        
        # Parse the structured output
        result = ActionItemsResponse.model_validate_json(response.message.content)
        return result.action_items
        
    except Exception as e:
        # Fallback to heuristic extraction if LLM fails
        print(f"LLM extraction failed: {e}, falling back to heuristic extraction")
        return extract_action_items(text)
```

### Key Design Decisions
1. **Structured Outputs**: Use Pydantic model with Ollama's `format` parameter for reliable JSON output
2. **Fallback Mechanism**: If LLM fails, fall back to the heuristic `extract_action_items()` function
3. **Model Parameter**: Allow model to be configurable (default: `llama3.1:8b`)
4. **Empty Input Handling**: Return empty list for empty/whitespace-only input

---

## TODO 2: Add Unit Tests for `extract_action_items_llm()`

### Objective
Write comprehensive unit tests in `week2/tests/test_extract.py` covering multiple input scenarios.

### Implementation Steps

#### Step 2.1: Create Mock/Fixture for Ollama
To ensure tests are deterministic and don't require a live Ollama server, use mocking.

#### Step 2.2: Implement Test Cases
- **File**: `week2/tests/test_extract.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from ..app.services.extract import extract_action_items, extract_action_items_llm

# Existing test for heuristic extraction
def test_extract_bullets_and_checkboxes():
    # ... existing test code ...

# ===== NEW TESTS FOR LLM EXTRACTION =====

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockResponse:
    def __init__(self, content):
        self.message = MockMessage(content)

@pytest.fixture
def mock_ollama_chat():
    """Fixture to mock Ollama chat function."""
    with patch('week2.app.services.extract.chat') as mock:
        yield mock

class TestExtractActionItemsLLM:
    """Test suite for LLM-powered action item extraction."""
    
    def test_bullet_list_extraction(self, mock_ollama_chat):
        """Test extraction from bullet list format."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": ["Set up database", "Implement API", "Write tests"]}'
        )
        
        text = """
        - Set up database
        - Implement API
        - Write tests
        """
        
        items = extract_action_items_llm(text)
        
        assert len(items) == 3
        assert "Set up database" in items
        assert "Implement API" in items
        assert "Write tests" in items
    
    def test_keyword_prefixed_lines(self, mock_ollama_chat):
        """Test extraction from keyword-prefixed lines."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": ["Complete project proposal", "Review code changes"]}'
        )
        
        text = """
        TODO: Complete project proposal
        ACTION: Review code changes
        """
        
        items = extract_action_items_llm(text)
        
        assert len(items) == 2
        assert "Complete project proposal" in items
        assert "Review code changes" in items
    
    def test_empty_input(self, mock_ollama_chat):
        """Test that empty input returns empty list without calling LLM."""
        items = extract_action_items_llm("")
        
        assert items == []
        mock_ollama_chat.assert_not_called()
    
    def test_whitespace_only_input(self, mock_ollama_chat):
        """Test that whitespace-only input returns empty list."""
        items = extract_action_items_llm("   \n\t  ")
        
        assert items == []
        mock_ollama_chat.assert_not_called()
    
    def test_no_action_items_found(self, mock_ollama_chat):
        """Test handling when no action items are found in text."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": []}'
        )
        
        text = "This is just a regular paragraph with no tasks."
        items = extract_action_items_llm(text)
        
        assert items == []
    
    def test_checkbox_format(self, mock_ollama_chat):
        """Test extraction from checkbox format."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": ["Buy groceries", "Call mom", "Finish homework"]}'
        )
        
        text = """
        [ ] Buy groceries
        [ ] Call mom
        [x] Already done task
        [ ] Finish homework
        """
        
        items = extract_action_items_llm(text)
        
        assert "Buy groceries" in items
        assert "Call mom" in items
        assert "Finish homework" in items
    
    def test_mixed_format(self, mock_ollama_chat):
        """Test extraction from mixed formats."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": ["Task A", "Task B", "Task C"]}'
        )
        
        text = """
        Meeting Notes:
        - Task A
        TODO: Task B
        [ ] Task C
        Some random text here.
        """
        
        items = extract_action_items_llm(text)
        
        assert len(items) == 3
    
    def test_llm_failure_fallback(self, mock_ollama_chat):
        """Test fallback to heuristic extraction when LLM fails."""
        mock_ollama_chat.side_effect = Exception("Connection error")
        
        text = """
        - Set up database
        - Write tests
        """
        
        items = extract_action_items_llm(text)
        
        # Should fall back to heuristic extraction
        assert "Set up database" in items
        assert "Write tests" in items
    
    def test_model_parameter(self, mock_ollama_chat):
        """Test that custom model parameter is passed to Ollama."""
        mock_ollama_chat.return_value = MockResponse(
            '{"action_items": ["Test task"]}'
        )
        
        extract_action_items_llm("- Test task", model="llama3.1:8b")
        
        # Verify the model parameter was passed
        call_kwargs = mock_ollama_chat.call_args[1]
        assert call_kwargs['model'] == 'llama3.1:8b'
```

### Test Coverage Summary
| Test Case | Description |
|-----------|-------------|
| Bullet lists | `-`, `*`, `•`, numbered items |
| Keyword prefixes | `TODO:`, `ACTION:`, `NEXT:` |
| Empty input | Returns empty list |
| Whitespace only | Returns empty list |
| No action items | Handles graceful empty response |
| Checkbox format | `[ ]` and `[todo]` markers |
| Mixed formats | Combination of formats |
| LLM failure | Fallback to heuristic extraction |
| Model parameter | Custom model configuration |

---

## TODO 3: Refactor Existing Code for Clarity

### Objective
Improve code quality focusing on API contracts/schemas, database layer, app lifecycle, and error handling.

### Implementation Steps

#### Step 3.1: Define Pydantic Schemas for API Contracts
- **New File**: `week2/app/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ===== Request Schemas =====

class ExtractRequest(BaseModel):
    """Request schema for action item extraction."""
    text: str = Field(..., min_length=1, description="The text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")
    use_llm: bool = Field(default=False, description="Whether to use LLM for extraction")

class CreateNoteRequest(BaseModel):
    """Request schema for creating a note."""
    content: str = Field(..., min_length=1, description="The note content")

class MarkDoneRequest(BaseModel):
    """Request schema for marking an action item as done."""
    done: bool = Field(default=True, description="Whether the item is done")

# ===== Response Schemas =====

class ActionItemResponse(BaseModel):
    """Response schema for a single action item."""
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool = False
    created_at: Optional[str] = None

class ExtractResponse(BaseModel):
    """Response schema for action item extraction."""
    note_id: Optional[int] = None
    items: List[ActionItemResponse]

class NoteResponse(BaseModel):
    """Response schema for a note."""
    id: int
    content: str
    created_at: str

class NotesListResponse(BaseModel):
    """Response schema for listing notes."""
    notes: List[NoteResponse]

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
```

#### Step 3.2: Create Database Service Layer
- **New File**: `week2/app/services/database_service.py`

```python
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Note:
    id: int
    content: str
    created_at: str

@dataclass
class ActionItem:
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str

class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_tables(self) -> None:
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                )
            """)
    
    # Note operations
    def insert_note(self, content: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            return cursor.lastrowid
    
    def get_note(self, note_id: int) -> Optional[Note]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,)
            )
            row = cursor.fetchone()
            if row:
                return Note(id=row["id"], content=row["content"], created_at=row["created_at"])
            return None
    
    def list_notes(self) -> List[Note]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            return [
                Note(id=row["id"], content=row["content"], created_at=row["created_at"])
                for row in cursor.fetchall()
            ]
    
    # Action item operations
    def insert_action_items(self, items: List[str], note_id: Optional[int] = None) -> List[int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            ids = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item)
                )
                ids.append(cursor.lastrowid)
            return ids
    
    def list_action_items(self, note_id: Optional[int] = None) -> List[ActionItem]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,)
                )
            return [
                ActionItem(
                    id=row["id"],
                    note_id=row["note_id"],
                    text=row["text"],
                    done=bool(row["done"]),
                    created_at=row["created_at"]
                )
                for row in cursor.fetchall()
            ]
    
    def mark_action_item_done(self, action_item_id: int, done: bool) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id)
            )
```

#### Step 3.3: Create Application Configuration
- **New File**: `week2/app/config.py`

```python
from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # Database Configuration
    database_path: Path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    
    # Application Configuration
    app_title: str = "Action Item Extractor"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
```

#### Step 3.4: Refactor Routers with Type Safety
- **File**: `week2/app/routers/action_items.py` (updated)
- **File**: `week2/app/routers/notes.py` (updated)

Use Pydantic models for request/response validation.

#### Step 3.5: Add Custom Exception Handlers
- **File**: `week2/app/exceptions.py`

```python
from fastapi import HTTPException

class ActionItemExtractionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class NoteNotFoundError(HTTPException):
    def __init__(self, note_id: int):
        super().__init__(status_code=404, detail=f"Note with id {note_id} not found")

class InvalidInputError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
```

### Refactoring Summary
| Area | Changes |
|------|---------|
| API Contracts | Pydantic schemas for all requests/responses |
| Database Layer | Service class with context managers, dataclasses |
| Configuration | Centralized settings with environment support |
| Error Handling | Custom exception classes |
| Type Safety | Full typing throughout codebase |

---

## TODO 4: Use Agentic Mode to Automate Small Tasks

### Objective
1. Add new LLM extraction endpoint and "Extract LLM" button
2. Add endpoint to list all notes and "List Notes" button

### Implementation Steps

#### Step 4.1: Add LLM Extraction Endpoint
- **File**: `week2/app/routers/action_items.py`

```python
@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(request: ExtractRequest) -> ExtractResponse:
    """Extract action items using LLM."""
    if not request.text.strip():
        raise InvalidInputError("text is required")
    
    note_id: Optional[int] = None
    if request.save_note:
        note_id = db_service.insert_note(request.text)
    
    items = extract_action_items_llm(request.text)
    ids = db_service.insert_action_items(items, note_id=note_id)
    
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)]
    )
```

#### Step 4.2: Add List Notes Endpoint
- **File**: `week2/app/routers/notes.py`

```python
@router.get("", response_model=NotesListResponse)
def list_all_notes() -> NotesListResponse:
    """Retrieve all notes."""
    notes = db_service.list_notes()
    return NotesListResponse(
        notes=[
            NoteResponse(id=n.id, content=n.content, created_at=n.created_at)
            for n in notes
        ]
    )
```

#### Step 4.3: Update Frontend HTML
- **File**: `week2/frontend/index.html`

Add new buttons and functionality:

```html
<!-- Add after existing Extract button -->
<button id="extract-llm">Extract (LLM)</button>
<button id="list-notes">List Notes</button>

<!-- Add notes display section -->
<div class="notes-section" id="notes-section" style="display: none;">
    <h2>Saved Notes</h2>
    <div id="notes-list"></div>
</div>
```

JavaScript additions:

```javascript
// LLM Extract button handler
const btnLLM = $('#extract-llm');
btnLLM.addEventListener('click', async () => {
    const text = $('#text').value;
    const save = $('#save_note').checked;
    itemsEl.textContent = 'Extracting with LLM...';
    try {
        const res = await fetch('/action-items/extract-llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, save_note: save }),
        });
        if (!res.ok) throw new Error('Request failed');
        const data = await res.json();
        // ... render items similar to extract button
    } catch (err) {
        console.error(err);
        itemsEl.textContent = 'Error extracting items with LLM';
    }
});

// List Notes button handler
const btnListNotes = $('#list-notes');
const notesSection = $('#notes-section');
const notesList = $('#notes-list');

btnListNotes.addEventListener('click', async () => {
    try {
        const res = await fetch('/notes');
        if (!res.ok) throw new Error('Request failed');
        const data = await res.json();
        
        if (!data.notes || data.notes.length === 0) {
            notesList.innerHTML = '<p class="muted">No notes found.</p>';
        } else {
            notesList.innerHTML = data.notes.map(note => `
                <div class="note-item">
                    <span class="note-id">#${note.id}</span>
                    <span class="note-date">${note.created_at}</span>
                    <p>${note.content}</p>
                </div>
            `).join('');
        }
        notesSection.style.display = 'block';
    } catch (err) {
        console.error(err);
        notesList.textContent = 'Error loading notes';
    }
});
```

### New Endpoints Summary
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/action-items/extract-llm` | POST | Extract action items using LLM |
| `/notes` | GET | List all saved notes |

---

## TODO 5: Generate a README from the Codebase

### Objective
Use Cursor to generate a comprehensive `README.md` file for the project.

### Implementation Steps

#### Step 5.1: Use Cursor to Analyze Codebase
Prompt for Cursor:
```
Analyze the week2 codebase and generate a comprehensive README.md that includes:
1. Project overview and purpose
2. Prerequisites and dependencies
3. Installation and setup instructions
4. How to run the application
5. API endpoints documentation
6. Testing instructions
7. Project structure
```

#### Step 5.2: Expected README.md Structure
- **File**: `week2/README.md`

```markdown
# Action Item Extractor

## Overview
A FastAPI application that extracts action items from free-form notes using both heuristic and LLM-powered methods.

## Prerequisites
- Python 3.10+
- Conda (for environment management)
- Poetry (for dependency management)
- Ollama (for LLM features)

## Installation

### 1. Clone and Setup Environment
```bash
conda activate cs146s
cd week2
poetry install
```

### 2. Configure Environment
Create a `.env` file in the `week2` directory:
```
OLLAMA_HOST=http://10.23.38.9:11434
```

### 3. Run the Application
```bash
poetry run uvicorn week2.app.main:app --reload
```

## API Endpoints

### Action Items
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/action-items/extract` | POST | Extract using heuristics |
| `/action-items/extract-llm` | POST | Extract using LLM |
| `/action-items` | GET | List all action items |
| `/action-items/{id}/done` | POST | Mark item as done |

### Notes
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/notes` | GET | List all notes |
| `/notes` | POST | Create a new note |
| `/notes/{id}` | GET | Get a specific note |

## Testing

Run tests with pytest:
```bash
poetry run pytest week2/tests/ -v
```

## Project Structure
```
week2/
├── app/
│   ├── main.py          # FastAPI application
│   ├── db.py            # Database operations
│   ├── config.py        # Configuration
│   ├── schemas.py       # Pydantic models
│   ├── exceptions.py    # Custom exceptions
│   ├── routers/
│   │   ├── action_items.py
│   │   └── notes.py
│   └── services/
│       └── extract.py   # Extraction logic
├── frontend/
│   └── index.html       # Web UI
├── tests/
│   └── test_extract.py  # Unit tests
├── data/
│   └── app.db          # SQLite database
└── .env                # Environment config
```
```

---

## Implementation Order

### Recommended Sequence
1. **Environment Setup**: Create `.env` file, verify Ollama connectivity
2. **TODO 1**: Implement `extract_action_items_llm()` 
3. **TODO 2**: Add unit tests for the new function
4. **TODO 3**: Refactor codebase (schemas, database service, config)
5. **TODO 4**: Add new endpoints and update frontend
6. **TODO 5**: Generate README using Cursor

### Estimated Time
| TODO | Estimated Time |
|------|---------------|
| TODO 1 | 1-2 hours |
| TODO 2 | 1 hour |
| TODO 3 | 2-3 hours |
| TODO 4 | 1-2 hours |
| TODO 5 | 30 minutes |
| **Total** | **5.5-8.5 hours** |

---

## Verification Checklist

- [ ] `.env` file created with correct Ollama host
- [ ] `extract_action_items_llm()` function implemented and working
- [ ] All unit tests passing
- [ ] Pydantic schemas created for API contracts
- [ ] Database service layer implemented
- [ ] Configuration centralized
- [ ] Custom exceptions added
- [ ] `/action-items/extract-llm` endpoint working
- [ ] `/notes` (GET all) endpoint working
- [ ] Frontend buttons functional
- [ ] README.md generated and complete
- [ ] `writeup.md` filled out with prompts and code locations
