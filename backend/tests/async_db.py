"""
Async database configuration for tests.

This module provides async database session management for tests using SQLAlchemy.
"""
import os
from typing import AsyncGenerator, Optional, Callable, Any, Dict

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db import base  # noqa: F401  # Import to ensure models are registered
from app.db.base import Base
from app.db.session import get_db

# Use PostgreSQL for all tests
TEST_DB_NAME = "travelpal_test"
TEST_DB_URL = "postgresql://postgres:postgres@localhost:5432"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", f"{TEST_DB_URL}/{TEST_DB_NAME}")
ASYNC_TEST_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}")

# Override the database URL for tests
settings.DATABASE_URL = TEST_DATABASE_URL
settings.ASYNC_DATABASE_URL = ASYNC_TEST_DATABASE_URL

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Create a test database engine and initialize tables."""
    # Create async engine
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=settings.SQL_ECHO,
        poolclass=NullPool
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
def override_get_db(async_engine) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """Override the get_db dependency to use the test database."""
    from app.db.async_session import AsyncSessionLocal  # Import here to avoid circular imports
    
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    return _get_db

@pytest.fixture
async def async_db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean test database for each test function."""
    # Create a new session
    async with async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture
def async_client(override_get_db):
    """Create a test client that overrides the database dependency."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
        
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(async_db: AsyncSession) -> Dict[str, Any]:
    """Create a test user for authentication."""
    from app.crud.user import user as crud_user
    from app.schemas.user import UserCreate
    
    email = "test@example.com"
    password = "TestPass123!"
    
    user_in = UserCreate(
        email=email,
        password=password,
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    
    db_user = await crud_user.create(async_db, obj_in=user_in)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "hashed_password": db_user.hashed_password,
        "is_active": db_user.is_active,
        "is_superuser": db_user.is_superuser,
        "password": password,
    }
