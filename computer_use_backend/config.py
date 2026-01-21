"""
Application configuration using Pydantic settings.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Database settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./computer_use_backend.db",
        description="Database connection URL"
    )
    
    # Agent settings
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    default_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Default Claude model"
    )
    max_tokens: int = Field(default=4096, description="Maximum tokens per request")
    
    # Display settings (required for Computer Use Agent)
    width: int = Field(default=1024, description="Display width")
    height: int = Field(default=768, description="Display height")
    display_num: int = Field(default=1, description="Display number")
    
    # Worker settings
    max_concurrent_sessions: int = Field(
        default=100,
        description="Maximum concurrent sessions"
    )
    worker_timeout: int = Field(
        default=300,
        description="Worker timeout in seconds"
    )
    
    # VNC settings
    vnc_base_port: int = Field(
        default=5900,
        description="Base port for VNC servers"
    )
    vnc_display_base: int = Field(
        default=1,
        description="Base display number for VNC"
    )
    
    # Resource limits
    max_message_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum message size in bytes"
    )
    session_timeout: int = Field(
        default=3600,  # 1 hour
        description="Session timeout in seconds"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()