#!/usr/bin/env python3
"""
Script to create a test database for PostgreSQL.
"""
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the test database if it doesn't exist."""
    # Get the database URL from environment variables
    db_url = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    # Parse the URL to get the database name and connection details
    from urllib.parse import urlparse, urlunparse, ParseResult
    parsed = urlparse(db_url)
    
    # Extract database name from the path
    db_name = parsed.path.lstrip('/')
    if not db_name:
        logger.error("No database name provided in the URL")
        return False
    
    # Create a connection to the default 'postgres' database
    postgres_conn_params = ParseResult(
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path='/postgres',
        params=parsed.params,
        query=parsed.query,
        fragment=parsed.fragment
    )
    postgres_url = urlunparse(postgres_conn_params)
    
    logger.info(f"Connecting to PostgreSQL server at {parsed.hostname or 'localhost'}:{parsed.port or 5432}")
    logger.info(f"Creating database: {db_name}")
    
    # Ensure we're not trying to create the 'postgres' database
    if db_name == 'postgres':
        logger.error("Cannot create the 'postgres' database as it's a system database")
        return False
    
    try:
        # Connect to the default 'postgres' database
        engine = create_engine(
            postgres_url,
            isolation_level="AUTOCOMMIT"
        )
        
        # Check if the database already exists
        with engine.connect() as conn:
            # Use text() for raw SQL and proper parameter binding
            from sqlalchemy import text
            
            # First, check if the database exists
            sql = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            result = conn.execute(sql, {"dbname": db_name})
            db_exists = result.scalar()
            
            if not db_exists:
                logger.info(f"Creating database: {db_name}")
                # Create the database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database {db_name} created successfully")
                
                # Now connect to the new database to create extensions if needed
                conn.execute(text("COMMIT"))  # Commit the current transaction
                
                # Create necessary extensions
                extensions = ["uuid-ossp"]  # Add any other extensions you need
                for ext in extensions:
                    try:
                        conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\""))
                        logger.info(f"Created extension: {ext}")
                    except Exception as e:
                        logger.warning(f"Failed to create extension {ext}: {e}")
                
                # Set default privileges if needed
                try:
                    conn.execute(text("""
                        GRANT ALL PRIVILEGES ON DATABASE "%s" TO %s;
                    """ % (db_name, parsed.username or 'postgres')))
                except Exception as e:
                    logger.warning(f"Failed to set privileges: {e}")
            else:
                logger.info(f"Database {db_name} already exists")
                
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
