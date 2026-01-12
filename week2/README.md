# Week 2 - Action Item Extractor

A FastAPI application that extracts actionable items from free-form notes. Supports both rule-based extraction and LLM-powered extraction using Ollama.

---

## Project Overview

This application allows users to paste notes and automatically extract action items (tasks, to-dos) from the text. Extracted items can be checked off as completed. Notes can optionally be saved to a SQLite database for later retrieval.

### Key Features

- Rule-based action item extraction using heuristics
- LLM-powered extraction using Ollama (llama3.1:8b)
- SQLite database for persistent storage
- RESTful API built with FastAPI
- Minimal HTML/JS frontend

### Project Structure

```
week2/
├── app/
│   ├── config.py              # Environment configuration
│   ├── main.py                # FastAPI application entry point
│   ├── schemas.py             # Pydantic models for request/response
│   ├── repositories/          # Database access layer
│   │   ├── base.py            # Database connection manager
│   │   ├── note_repository.py
│   │   └── action_item_repository.py
│   ├── routers/               # API route handlers
│   │   ├── notes.py
│   │   └── action_items.py
│   └── services/
│       └── extract.py         # Extraction logic (rule-based & LLM)
├── frontend/
│   └── index.html             # Web UI
├── tests/
│   └── test_extract.py        # Unit tests
├── data/                      # SQLite database directory
└── .env                       # Environment variables
```

---

## Installation

### Prerequisites

- Python 3.12
- Conda (Anaconda or Miniconda)
- Poetry
- Ollama

### Step 1: Create and Activate Conda Environment

```bash
conda create -n cs146s python=3.12 -y
conda activate cs146s
```

### Step 2: Install Dependencies with Poetry

From the project root directory:

```bash
poetry install --no-interaction
```

### Step 3: Install and Run Ollama

macOS (Homebrew):
```bash
brew install --cask ollama
```

Pull the required model:
```bash
ollama pull llama3.1:8b
```

Start Ollama server (or use the macOS app):
```bash
ollama serve
```

### Step 4: Create Environment File

Create a `.env` file in the `week2/` directory:

```
# Database
DB_PATH=data/app.db

# LLM
LLM_MODEL=llama3.1:8b
LLM_TEMPERATURE=0

# App
APP_TITLE=Action Item Extractor
```

---

## Running the Application

### Start the Server

From the project root directory:

```bash
poetry run uvicorn week2.app.main:app --reload
```

### Access the Application

Open a web browser and navigate to:

```
http://127.0.0.1:8000/
```

### Using the Frontend

1. Paste your notes in the text area
2. Check "Save as note" if you want to persist the text
3. Click "Extract (Rule-based)" for heuristic extraction
4. Click "Extract (LLM)" for AI-powered extraction
5. Click "List Notes" to view all saved notes

---

## API Specification

### Notes

#### Create Note
- **POST** `/notes`
- **Request Body:**
  ```json
  {
    "content": "string"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "content": "string",
    "created_at": "2024-01-01 12:00:00"
  }
  ```

#### List All Notes
- **GET** `/notes`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "content": "string",
      "created_at": "2024-01-01 12:00:00"
    }
  ]
  ```

#### Get Single Note
- **GET** `/notes/{note_id}`
- **Response:**
  ```json
  {
    "id": 1,
    "content": "string",
    "created_at": "2024-01-01 12:00:00"
  }
  ```

### Action Items

#### Extract Action Items (Rule-based)
- **POST** `/action-items/extract`
- **Request Body:**
  ```json
  {
    "text": "string",
    "save_note": false
  }
  ```
- **Response:**
  ```json
  {
    "note_id": null,
    "items": [
      {"id": 1, "text": "extracted action item"}
    ]
  }
  ```

#### Extract Action Items (LLM)
- **POST** `/action-items/extract-llm`
- **Request Body:**
  ```json
  {
    "text": "string",
    "save_note": false
  }
  ```
- **Response:**
  ```json
  {
    "note_id": null,
    "items": [
      {"id": 1, "text": "extracted action item"}
    ]
  }
  ```

#### List Action Items
- **GET** `/action-items`
- **Query Parameters:**
  - `note_id` (optional): Filter by note ID
- **Response:**
  ```json
  [
    {
      "id": 1,
      "note_id": 1,
      "text": "string",
      "done": false,
      "created_at": "2024-01-01 12:00:00"
    }
  ]
  ```

#### Mark Action Item Done
- **POST** `/action-items/{action_item_id}/done`
- **Request Body:**
  ```json
  {
    "done": true
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "done": true
  }
  ```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Running Tests

### Run All Tests

From the project root directory:

```bash
poetry run pytest week2/tests/ -v
```

### Run Specific Test File

```bash
poetry run pytest week2/tests/test_extract.py -v
```

---

## Configuration

Environment variables can be configured in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| DB_PATH | Path to SQLite database file | data/app.db |
| LLM_MODEL | Ollama model name | llama3.1:8b |
| LLM_TEMPERATURE | LLM temperature (0-1) | 0 |
| APP_TITLE | Application title | Action Item Extractor |

---

## Troubleshooting

### Ollama Connection Error

If you see connection errors when using LLM extraction:
1. Ensure Ollama is running (`ollama serve` or the macOS app)
2. Verify the model is pulled: `ollama list`
3. Check that port 11434 is not blocked

### Database Errors

If you encounter database issues:
1. Delete the `data/app.db` file
2. Restart the server (tables will be recreated automatically)

### Memory Issues with LLM

If the LLM model crashes due to memory:
1. Try a smaller model: `ollama pull mistral:7b`
2. Update `LLM_MODEL` in `.env` to match
