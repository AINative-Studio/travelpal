import asyncio
import logging
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database

# Import database models to ensure they are registered with SQLAlchemy
from app.db.base import Base
from app.models import user, item  # Import models to register them with Base

# Import all models explicitly to ensure they are registered
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401

from app.core.config import settings
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/travelpal_test"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/travelpal_test"
os.environ["ASYNC_DATABASE_URL"] = TEST_DATABASE_URL

# Create async engine and session factory
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

async def create_tables():
    """Create all database tables."""
    # Create sync engine for table creation
    sync_db_url = "postgresql://postgres:postgres@localhost:5432/travelpal_test"
    logger.info(f"Connecting to database: {sync_db_url}")
    
    # Create database if it doesn't exist (PostgreSQL only)
    if not database_exists(sync_db_url):
        logger.info("Creating database...")
        create_database(sync_db_url)
    
    # Create engine with echo=True for debugging
    sync_engine = create_engine(sync_db_url, echo=True)
    
    try:
        # Create a scoped session
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=sync_engine))
        
        # Drop all tables if they exist
        logger.info("Dropping existing tables...")
        Base.metadata.drop_all(bind=sync_engine)
        
        # Print all models registered with Base
        logger.info(f"Models registered with Base: {Base.registry._class_registry}")
        
        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=sync_engine)
        
        # Verify tables were created
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables created: {tables}")
        
        if not tables:
            logger.error("No tables were created. Check your model imports and metadata.")
            # Try to create tables directly using raw SQL as a fallback
            logger.info("Attempting to create tables using raw SQL...")
            with sync_engine.connect() as conn:
                # Create users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        hashed_password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100),
                        is_active BOOLEAN NOT NULL DEFAULT true,
                        is_superuser BOOLEAN NOT NULL DEFAULT false,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                
                # Create items table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        description TEXT,
                        owner_id INTEGER REFERENCES users(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                
                # Verify tables were created
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                logger.info(f"Tables after raw SQL creation: {tables}")
        else:
            # Verify each table structure
            for table_name in tables:
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                logger.info(f"Table {table_name} columns: {columns}")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        db_session.remove()
        sync_engine.dispose()
        logger.info("Database connection closed")

async def test_init():
    logger.info("Testing database initialization...")
    
    # Create tables first
    logger.info("Creating database tables...")
    await create_tables()
    
    # Initialize database with data
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Initializing database with initial data...")
            await init_db(db)
            await db.commit()
            logger.info("Database initialization completed successfully")
            
            # Verify tables were created
            result = await db.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Tables in database: {tables}")
            
            # Verify users table
            if 'users' in tables:
                result = await db.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                logger.info(f"Number of users: {count}")
                
                # If no users, try to create a test user
                if count == 0:
                    from app.schemas.user import UserCreate
                    from app.crud import crud_user
                    
                    user_in = UserCreate(
                        email="test@example.com",
                        password="testpassword",
                        full_name="Test User"
                    )
                    await crud_user.create(db, obj_in=user_in)
                    await db.commit()
                    logger.info("Created test user")
            else:
                logger.error("Users table not found")
                
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(test_init())
