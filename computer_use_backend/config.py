from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"]
    )
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./computer_use_backend.db"
    )
    
    anthropic_api_key: str = Field(default="")
    default_model: str = Field(default="claude-sonnet-4-5-20250929")
    max_tokens: int = Field(default=4096)
    
    width: int = Field(default=1024)
    height: int = Field(default=768)
    display_num: int = Field(default=1)
    
    max_concurrent_sessions: int = Field(default=100)
    worker_timeout: int = Field(default=300)
    
    vnc_base_port: int = Field(default=5900)
    vnc_display_base: int = Field(default=1)
    
    max_message_size: int = Field(default=1024 * 1024)
    session_timeout: int = Field(default=3600)


@lru_cache()
def get_settings():
    return Settings()
