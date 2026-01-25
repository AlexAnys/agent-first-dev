---
name: extend-extract
description: Extend the action item parser with SubAgents - TestAgent writes tests, ParseAgent implements code.
arguments:
- name: pattern
  description: |
    Optional: Specific pattern to add (e.g., "brackets", "mentions", "all").
    If not provided, you'll be prompted to choose.
  required: false
---

## Preconditions
- Run from the `week4/` directory
- Python environment active (`conda activate cs146s`)

## Workflow

This command runs a two-agent workflow to extend the action item parser:

1. **TestAgent** runs first:
   - Reads current `extract.py` and `test_extract.py`
   - Writes new test cases for the requested pattern(s)
   - Provides summary of tests added

2. **ParseAgent** runs second:
   - Reads the new tests from TestAgent
   - Implements the parsing logic in `extract.py`
   - Runs format, lint, and tests

## Usage

```bash
# Add all new patterns (brackets, parentheses, mentions)
/extend-extract all

# Add only bracket syntax
/extend-extract brackets

# Add only mention syntax
/extend-extract mentions

# Interactive mode (will prompt for pattern selection)
/extend-extract
```

## Supported Patterns

| Pattern | Example | Extracted As |
|---------|---------|--------------|
| Brackets | `[ ] Buy groceries` | `Buy groceries` |
| Parenthesis | `( ) Review PR` | `Review PR` |
| Mentions | `@john fix bug` | `fix bug` |

## Expected Output

- Test file updated with new test functions
- Extract.py updated with new parsing logic
- All tests passing

## Rollback

If something goes wrong:
```bash
git checkout backend/tests/test_extract.py backend/app/services/extract.py
```
