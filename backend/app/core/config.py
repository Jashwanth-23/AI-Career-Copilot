"""
Application Configuration Module

This module defines the central configuration settings for the FastAPI application
using Pydantic Settings (Pydantic v2). Environment variables are loaded automatically
from the `backend/.env` file or from system environment variables.
"""

from pathlib import Path
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the backend root directory (backend/) to accurately locate backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """
    Application Settings schema and loader powered by Pydantic Settings.

    Reads environment variables from system env or backend/.env file.
    """

    # ------------------------------------------------------------------
    # Project Info
    # ------------------------------------------------------------------
    PROJECT_NAME: str = Field(
        default="AI Career Copilot",
        description="Name of the FastAPI application"
    )
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API v1 prefix route"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Execution environment (development, staging, production)"
    )

    # ------------------------------------------------------------------
    # Database Settings
    # ------------------------------------------------------------------
    DATABASE_URL: str

    # ------------------------------------------------------------------
    # Security & JWT Configuration
    # ------------------------------------------------------------------
    SECRET_KEY: str
    ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT token signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Expiration time for access tokens in minutes"
    )

    # ------------------------------------------------------------------
    # External AI Services
    # ------------------------------------------------------------------
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key for AI features"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Google Gemini model identifier for AI features"
    )

    # ------------------------------------------------------------------
    # CORS Origins
    # ------------------------------------------------------------------
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="List of allowed CORS origins or comma-separated string"
    )

    # ------------------------------------------------------------------
    # Pydantic Settings Configuration (v2)
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=(ENV_FILE_PATH, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Export a singleton instance of settings
settings = Settings()
