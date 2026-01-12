from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from week3 directory
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Settings:
    """GitHub MCP Server settings."""
    
    # GitHub API
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    
    # Default repository (optional, can be overridden in tool calls)
    DEFAULT_OWNER: str = os.getenv("GITHUB_DEFAULT_OWNER", "")
    DEFAULT_REPO: str = os.getenv("GITHUB_DEFAULT_REPO", "")
    
    # Request settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    USER_AGENT: str = "GitHub-Daily-Issue-MCP-Server"
    
    @classmethod
    def get_headers(cls) -> dict:
        """Get headers for GitHub API requests."""
        return {
            "Authorization": f"Bearer {cls.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": cls.USER_AGENT,
        }
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is required")


settings = Settings()
