"""
Chat API endpoints for the TravelPal application.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.langchain.agent import travel_agent
from app.api.deps import get_current_active_user
from app.models.user import User

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    """Request model for chat messages."""
    text: str = Field(..., min_length=1, description="The message text to process")

@router.post(
    "",  # Empty path since the router is already adding the /chat prefix
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successful response with chat message"},
        400: {"description": "Invalid request format or missing required fields"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    },
    summary="Process a chat message",
    description="Process a chat message and return the agent's response.",
    tags=["chat"]
)
async def chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Process a chat message and return the agent's response.
    
    Args:
        message: The chat message to process
        current_user: The authenticated user
        
    Returns:
        Dict containing the agent's response
        
    Raises:
        HTTPException: If there's an error processing the message
    """
    try:
        # Get response from the travel agent (synchronous call)
        response = travel_agent.process_message(message.text)
        return {"response": response}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again later."
        )
