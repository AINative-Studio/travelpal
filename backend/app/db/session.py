"""
Database session management for the application.

This module provides database session management using SQLAlchemy.
It includes the SQLAlchemy engine, session factory, and base model class.
"""
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Database engine configuration
engine_args = {
    'pool_pre_ping': True,  # Enable connection health checks
    'pool_recycle': 3600,    # Recycle connections after 1 hour
}

# Add PostgreSQL-specific configurations if not using SQLite
if 'sqlite' not in settings.DATABASE_URL:
    engine_args.update({
        'pool_size': 10,        # Number of connections to keep open
        'max_overflow': 20,     # Number of connections to allow in overflow
        'connect_args': {
            "connect_timeout": 10,  # Connection timeout in seconds
            "keepalives": 1,       # Enable TCP keepalive
            "keepalives_idle": 30,  # TCP keepalive idle time in seconds
            "keepalives_interval": 10,  # TCP keepalive interval in seconds
            "keepalives_count": 5,      # TCP keepalive count
        },
    })


# Create database engine
engine: Engine = create_engine(settings.DATABASE_URL, **engine_args)

# Create session factory with specific configurations
SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True,  # Expire objects after transaction ends
)

# Base class for all SQLAlchemy models
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields db sessions.
    
    Yields:
        Session: A database session
        
    Example:
        ```python
        with get_db() as db:
            # Use the database session
            users = db.query(User).all()
        ```
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()
