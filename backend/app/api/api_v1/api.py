from fastapi import APIRouter

from app.api.endpoints import chat as chat_endpoints

# Create the API router
api_router = APIRouter()

# Include chat endpoints
api_router.include_router(
    chat_endpoints.router,
    prefix="/chat",
    tags=["chat"]
)

@api_router.get("")
async def api_v1_root():
    return {"message": "Welcome to TravelPal API v1"}
