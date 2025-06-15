import asyncio
from app.db.async_session import async_engine, AsyncSessionLocal
from app.db.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, text

async def check_tables():
    # Create tables
    print("Creating tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check tables using raw SQL
    print("Checking tables...")
    async with async_engine.connect() as conn:
        # Use raw SQL to list tables
        result = await conn.execute(
            text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
        )
        tables = [row[0] for row in result.fetchall()]
        print('Tables in database:', tables)

if __name__ == "__main__":
    asyncio.run(check_tables())
