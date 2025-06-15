from typing import Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.core.config import settings
from app.db.base import Base  # noqa: F401

# Configure logging
logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    """
    Initialize the database with initial data.
    
    Args:
        db: Database session
    """
    # Get the engine URL from settings
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database
    
    # Convert async URL to sync URL for table creation
    sync_db_url = settings.DATABASE_URL
    if sync_db_url.startswith("postgresql+asyncpg:"):
        sync_db_url = sync_db_url.replace("postgresql+asyncpg:", "postgresql:", 1)
    
    # Create sync engine for table creation
    sync_engine = create_engine(sync_db_url)
    
    # Create database if it doesn't exist (PostgreSQL only)
    if sync_db_url.startswith("postgresql"):
        if not database_exists(sync_engine.url):
            create_database(sync_engine.url)
    
    # Create all tables
    Base.metadata.create_all(bind=sync_engine)
    
    # Close the sync engine
    sync_engine.dispose()
    
    # Create first superuser if it doesn't exist
    if not settings.FIRST_SUPERUSER or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.warning(
            "Skipping superuser creation: FIRST_SUPERUSER or FIRST_SUPERUSER_PASSWORD not set"
        )
        return
    
    try:
        # Check if users table exists and has data
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
        )
        users_table_exists = result.scalar()
        
        if not users_table_exists:
            logger.error("Users table does not exist after initialization")
            return
            
        # Check if user exists
        user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = schemas.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_active=True,
                full_name="Admin User"
            )
            # Convert Pydantic model to dict before passing to CRUD
            user_data = user_in.dict()
            user = await crud.user.create(db, obj_in=user_data)
            await db.commit()
            logger.info(f"Created first superuser with email: {user.email}")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        await db.rollback()
        raise
