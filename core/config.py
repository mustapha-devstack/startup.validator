from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Make sure it exists in {BASE_DIR / '.env'}."
        )

    return value


def get_optional_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


GROQ_API_KEY = get_required_env("GROQ_API_KEY")
TAVILY_API_KEY = get_required_env("TAVILY_API_KEY")

REDIS_URL = get_optional_env(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

FRONTEND_URL = get_optional_env(
    "FRONTEND_URL",
    "http://localhost:3000",
)

PRODUCTION_FRONTEND_URL = get_optional_env(
    "PRODUCTION_FRONTEND_URL",
    "https://plangraph.vercel.app",
)

LLM_MODEL = get_optional_env(
    "LLM_MODEL",
    "llama-3.3-70b-versatile",
)