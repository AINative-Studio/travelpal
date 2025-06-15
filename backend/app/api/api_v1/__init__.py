from fastapi import APIRouter

# Import all endpoint routers
from app.api.api_v1.endpoints import users, login, items, chat

# Create the main API router
api_router = APIRouter()

# Include all the endpoint routers
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
