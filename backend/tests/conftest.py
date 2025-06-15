"""
Pytest configuration and fixtures for TravelPal tests.

This file contains fixtures and configuration that are available to all tests.
"""
import os
import pytest
import asyncio
from typing import Generator, Dict, Any, Callable, AsyncGenerator

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
# Import Base from models to ensure all models are registered with it
from app.models.base import Base
from app.db.session import get_db
from app.db.async_session import get_async_db
from app.main import app

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401

# Use a test database for all tests
TEST_DB_NAME = "travelpal_test"
TEST_DB_URL = "postgresql://postgres:postgres@localhost:5432"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", f"{TEST_DB_URL}/{TEST_DB_NAME}")
# Set up async database URL for tests
ASYNC_TEST_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}")

# Create test database if it doesn't exist
import subprocess
import sys

try:
    # Check if database exists
    import psycopg2
    conn = psycopg2.connect(f"{TEST_DB_URL}/postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        exists = cur.fetchone()
        if not exists:
            print(f"Creating test database: {TEST_DB_NAME}")
            cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
            # Enable necessary extensions
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.close()
except Exception as e:
    print(f"Error setting up test database: {e}", file=sys.stderr)
    raise

# Ensure all models are imported and registered with SQLAlchemy
# This is needed for create_all() to work properly
from app.db import base  # noqa: F401
from app import models  # noqa: F401

# Override the database URLs for tests
settings.DATABASE_URL = TEST_DATABASE_URL
settings.ASYNC_DATABASE_URL = ASYNC_TEST_DATABASE_URL

# Create async engine for tests
async_engine = create_async_engine(
    ASYNC_TEST_DATABASE_URL,
    echo=True,
    poolclass=NullPool
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def init_db():
    """Initialize the test database with all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # For async generator fixture
    yield
    
    # Clean up
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db(init_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean test database for each test function."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Sync engine for backward compatibility
@pytest.fixture(scope="session")
def engine():
    """Create a test database engine and initialize tables (sync)."""
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=NullPool
    )
    
    try:
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture
def sync_db(engine):
    """Create a clean test database for each test function (sync)."""
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session factory bound to this connection
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()
    
    # Start a savepoint
    session.begin_nested()
    
    # Set up the savepoint for nested transactions
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()
    
    try:
        yield session
        # Rollback any changes made during the test
        session.rollback()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        # Cleanup the session and transaction
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()

@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client that overrides the database dependency.
    
    Args:
        db: The database session fixture
        
    Yields:
        TestClient: A FastAPI test client
    """
    # Create a new function that yields our test session
    def override_get_db():
        try:
            yield sync_db
        finally:
            sync_db.close()
    
    # Override the async get_db dependency
    async def override_get_async_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    # Override the dependencies in the app
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    # Create the test client
    with TestClient(app) as test_client:
        try:
            yield test_client
        finally:
            # Ensure any pending transactions are rolled back
            db.rollback()
    
    # Clean up overrides
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(db):
    """
    Create an async test client that can be used to test API endpoints.
    
    Args:
        db: The async database session fixture
        
    Yields:
        AsyncClient: An async HTTP client for testing
    """
    from app.main import app
    from app.db.async_session import get_async_db
    from fastapi import Depends
    from httpx import AsyncClient
    
    # Override the async db dependency to use the test session
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db
        finally:
            await db.rollback()
    
    # Apply the override
    app.dependency_overrides[get_async_db] = override_get_db
    
    # Create async test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(async_client, db) -> Dict[str, Any]:
    """
    Create a test user for authentication.
    
    Args:
        async_client: The async test client
        db: The async database session fixture
        
    Returns:
        Dict containing user details including the ID and email
    """
    from app.schemas.user import UserCreate
    from app.crud import user as crud_user
    import uuid
    
    # Generate unique email for each test run
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    # Use a password that meets the complexity requirements
    password = "TestPassword123!"
    user_in = UserCreate(
        email=email,
        password=password,
        full_name="Test User"
    )
    
    try:
        # Convert Pydantic model to dict for CRUD
        user_data = user_in.model_dump()
        user = await crud_user.create(db, obj_in=user_data)
        await db.commit()
        await db.refresh(user)
        
        yield {
            "id": user.id,
            "email": user.email,
            "password": password,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        }
        
        # Cleanup after the test
        await db.delete(user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
