# /verify

Run the full local quality gate for this repo and summarize results.

## Steps
1) Run formatting:
- `make format`

2) Run lint:
- `make lint`

3) Run tests:
- `make test`

## Output requirements
- If everything passes, print a short success summary: which commands ran and all passed.
- If anything fails, do ALL of the following:
  - Identify which step failed (format, lint, or test).
  - Paste the key error lines (trim noise).
  - Provide a concrete next action list (max 5 bullets) to fix it.
  - Do NOT continue to later steps after a failure.

## Notes
- Assume commands are run from the repo root (week4/).
- Keep the final response concise and actionable.
