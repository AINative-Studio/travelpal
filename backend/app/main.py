import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.async_session import async_engine, AsyncSessionLocal
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup: Initialize database
    logger.info("Initializing database...")
    try:
        # Initialize database
        async with AsyncSessionLocal() as session:
            await init_db(session)
            await session.commit()
            
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down application...")
    # Add any cleanup code here if needed

# Create FastAPI app with lifespan events
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    TravelPal API - AI-Powered Travel Assistant
    
    This API powers the TravelPal application, providing endpoints for:
    - User authentication and authorization
    - Travel search and booking
    - Personalization and recommendations
    """,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Add GZip middleware for compressing responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add pagination support
add_pagination(app)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to the TravelPal API",
        "docs": "/docs",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }
