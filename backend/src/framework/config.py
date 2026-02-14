"""
Centralized Configuration Management

Uses Pydantic Settings for environment variable validation and type safety.
All configuration values should be accessed through the global `settings` instance.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration with environment variable validation"""
    
    # === Database Configuration ===
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="Async SQLite database URL"
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    
    # === LinkedIn OAuth Configuration ===
    LINKEDIN_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="LinkedIn OAuth app client ID"
    )
    LINKEDIN_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="LinkedIn OAuth app client secret"
    )
    LINKEDIN_REDIRECT_URI: str = Field(
        default="http://localhost:8000/linkedin/callback",
        description="OAuth redirect URI for callback"
    )
    LINKEDIN_OAUTH_URL: str = Field(
        default="https://www.linkedin.com/oauth/v2/authorization",
        description="LinkedIn OAuth authorization URL"
    )
    LINKEDIN_TOKEN_URL: str = Field(
        default="https://www.linkedin.com/oauth/v2/accessToken",
        description="LinkedIn OAuth token exchange URL"
    )
    LINKEDIN_API_BASE: str = Field(
        default="https://api.linkedin.com/v2",
        description="LinkedIn REST API base URL"
    )
    
    # === Gemini AI Configuration ===
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    GEMINI_FAST_MODEL: str = Field(
        default="gemini-2.0-flash-exp",
        description="Fast Gemini model for quick operations"
    )
    GEMINI_POWERFUL_MODEL: str = Field(
        default="gemini-2.0-flash-thinking-exp-1219",
        description="Powerful Gemini model for complex tasks"
    )
    GEMINI_IMAGE_MODEL: str = Field(
        default="imagen-3.0-generate-001",
        description="Gemini model for image generation"
    )
    
    # === Tavily Search Configuration ===
    TAVILY_API_KEY: Optional[str] = Field(
        default=None,
        description="Tavily API key for web search"
    )
    
    # === Frontend Configuration ===
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL for CORS"
    )
    
    # === Retry Configuration ===
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retry attempts for external API calls"
    )
    RETRY_MIN_WAIT: int = Field(
        default=1,
        description="Minimum wait time (seconds) between retries"
    )
    RETRY_MAX_WAIT: int = Field(
        default=10,
        description="Maximum wait time (seconds) between retries"
    )
    
    # === Workflow Configuration ===
    MAX_REVISIONS: int = Field(
        default=2,
        description="Maximum content revision attempts in workflow"
    )
    
    # === Application Settings ===
    APP_NAME: str = Field(
        default="LinkedIn AI AutoPost",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
