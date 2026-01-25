---
name: verify-week4
description: Run the week4 quality gate (make format, make lint, make test) and summarize results. Use when the user asks to verify changes before committing.
metadata:
  short-description: Verify formatting, lint, and tests for week4.
---

## Preconditions
- Run from the `week4/` repo directory (the one that contains `Makefile`).
- Ensure the Python environment is active (e.g., `conda activate cs146s`) so `make`, `black`, `ruff`, and `pytest` are available.

## Workflow
1) Run:
   - `make format`
2) Then:
   - `make lint`
3) Then:
   - `make test`

## Failure handling
- Stop immediately on the first failure.
- Report:
  - Which step failed (format/lint/test)
  - The key error lines (trim noise)
  - Up to 5 concrete next actions

## Success output
- Print a short summary confirming all three steps passed.
