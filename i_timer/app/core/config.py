"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    database_url: str = "postgresql+asyncpg://timer_user:timer_pass@postgres:5432/timer_db"
    database_url_sync: str = "postgresql://timer_user:timer_pass@postgres:5432/timer_db"
    
    # Application settings
    app_name: str = "Interval Timer API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS settings
    allowed_origins: list[str] = [
        "http://localhost:3000", 
        "http://frontend:3000",
        "http://localhost:80",
        "http://frontend:80"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()