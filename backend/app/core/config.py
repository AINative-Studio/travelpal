from pydantic import PostgresDsn, RedisDsn, Field, validator
from pydantic_settings import BaseSettings
from typing import Optional, List, Union, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "TravelPal"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    ASYNC_DATABASE_URL: str = Field(..., env="ASYNC_DATABASE_URL")
    
    # SQL Alchemy
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "False").lower() == "true"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # First Superuser
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")
    
    @validator("ASYNC_DATABASE_URL")
    def assemble_async_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Assemble the async database connection URL."""
        if isinstance(v, str) and v:
            return v
        
        # Convert sync URL to async URL if not explicitly provided
        sync_url = values.get("DATABASE_URL")
        if not sync_url:
            raise ValueError("DATABASE_URL must be set")
            
        if sync_url.startswith("postgresql://"):
            return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif sync_url.startswith("sqlite:"):
            return sync_url.replace("sqlite:", "sqlite+aiosqlite:", 1)
            
        raise ValueError(f"Unsupported database URL: {sync_url}")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'
        env_nested_delimiter = '__'

settings = Settings()
