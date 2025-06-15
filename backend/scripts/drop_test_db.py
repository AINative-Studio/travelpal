#!/usr/bin/env python3
"""
Script to drop the test database.
"""
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def drop_database():
    """Drop the test database if it exists."""
    # Get the database URL from environment variables
    db_url = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    # Parse the URL to get the database name
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip('/')
    
    # Create a connection to the default 'postgres' database
    postgres_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 5432}/postgres"
    if parsed.username and parsed.password:
        postgres_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/postgres"
    
    logger.info(f"Connecting to PostgreSQL server at {parsed.hostname}:{parsed.port or 5432}")
    
    try:
        # Connect to the default 'postgres' database
        engine = create_engine(
            postgres_url,
            isolation_level="AUTOCOMMIT"
        )
        
        # Check if the database exists
        with engine.connect() as conn:
            # Use text() for raw SQL and proper parameter binding
            from sqlalchemy import text
            
            # Check if database exists
            sql = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            result = conn.execute(sql, {"dbname": db_name})
            db_exists = result.scalar()
            
            if db_exists:
                logger.info(f"Dropping database: {db_name}")
                    # Disconnect all users from the database
                sql_disconnect = text("""
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE datname = :dbname 
                    AND pid <> pg_backend_pid();
                """)
                conn.execute(sql_disconnect, {"dbname": db_name})
                
                # Drop the database (can't parameterize database name in DROP DATABASE)
                if db_name != 'postgres':  # Prevent dropping the main postgres database
                    conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
                    logger.info(f"Database {db_name} dropped successfully")
                else:
                    logger.warning("Skipping drop of 'postgres' database to prevent system issues")
            else:
                logger.info(f"Database {db_name} does not exist")
                
        return True
        
    except Exception as e:
        logger.error(f"Error dropping database: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    success = drop_database()
    sys.exit(0 if success else 1)
