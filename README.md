# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Repo Setup

This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast Python package and project management.

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Setup Project & Environment**:
   From the repository root, simply run:
   ```bash
   uv sync
   ```
   This will automatically create a virtual environment (`.venv`) and install all dependencies.

3. **Run Commands**:
   You can run any script or tool using `uv run`:
   ```bash
   uv run pytest
   uv run python week1/chain_of_thought.py
   ```

## Development

- **Add a dependency**: `uv add <package>`
- **Check dependency tree**: `uv tree`
- **Active environment**: `source .venv/bin/activate` (optional, as `uv run` handles this automatically)