# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Repo Setup

These steps work with Python 3.12.

1. Install `uv`.

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh`
```

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new terminal to make sure `uv` is on your `PATH`.

2. Install dependencies:

```bash
uv sync --python 3.12 --no-install-project
```

To run scripts without activating the virtual environment run:

```bash
uv run <script>
```
