"""
Database package initialization.

This module initializes the SQLAlchemy ORM and provides database session management.
It should be the single source of truth for database-related imports.
"""
from typing import Generator

from sqlalchemy.orm import Session

from .session import SessionLocal, engine, Base  # noqa: F401

# Import all models here so they are registered with SQLAlchemy
# This must be done after Base is imported but before any model is used
from app.models import user, item  # noqa: F401

# Create all database tables
# Note: In production, use Alembic migrations instead of create_all()
# Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields database sessions.
    
    Yields:
        Session: A database session
        
    Example:
        ```python
        from app.db import get_db
        
        with get_db() as db:
            # Use the database session
            users = db.query(User).all()
        ```
    """
    from .session import get_db as _get_db
    return _get_db()

# Re-export important types and functions
__all__ = [
    'SessionLocal',
    'engine',
    'Base',
    'get_db',
]
