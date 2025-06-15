"""
Chat API endpoints for the TravelPal application.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.services.langchain.agent import travel_agent

router = APIRouter()

@router.post("/chat", response_model=Dict[str, Any])
async def chat(message: Dict[str, str]) -> Dict[str, str]:
    """
    Process a chat message and return the agent's response.
    
    Args:
        message: Dictionary containing a 'text' key with the user's message
        
    Returns:
        Dict containing the agent's response
    """
    try:
        user_message = message.get("text", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message text is required")
            
        # Get response from the travel agent
        response = await travel_agent.process_message(user_message)
        
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
