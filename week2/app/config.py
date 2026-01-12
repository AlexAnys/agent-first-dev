from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from week2 directory
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DB_PATH: Path = BASE_DIR / os.getenv("DB_PATH", "data/app.db")
    
    # LLM
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    
    # App
    APP_TITLE: str = os.getenv("APP_TITLE", "Action Item Extractor")


settings = Settings()
