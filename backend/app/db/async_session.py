"""
Async database session management for the application.

This module provides async database session management using SQLAlchemy.
It includes the async SQLAlchemy engine and session factory.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Async database engine configuration
engine_args = {
    'pool_pre_ping': True,  # Enable connection health checks
    'pool_recycle': 3600,   # Recycle connections after 1 hour
    'echo': settings.SQL_ECHO,  # Echo SQL queries
}

# Add PostgreSQL-specific configurations if not using SQLite
if 'sqlite' not in settings.ASYNC_DATABASE_URL:
    engine_args.update({
        'pool_size': 10,        # Number of connections to keep open
        'max_overflow': 20,     # Number of connections to allow in overflow
    })
else:
    # Use NullPool for SQLite as it doesn't support connection pooling
    engine_args['poolclass'] = NullPool

# Create async database engine
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    **engine_args
)

# Create async session factory with specific configurations
async_session_maker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Important for async sessions
)

# For backward compatibility
AsyncSessionLocal = async_session_maker

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function that yields db sessions.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# For backward compatibility
async def get_async_db_legacy() -> AsyncGenerator[AsyncSession, None]:
    """
    Legacy async dependency function that yields db sessions.
    This is kept for backward compatibility.
    
    Yields:
        AsyncSession: An async database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
