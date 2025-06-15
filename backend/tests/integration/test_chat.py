"""
Integration tests for the chat endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_travel_agent():
    """Mock the travel agent for testing."""
    with patch('app.api.endpoints.chat.travel_agent') as mock_agent:
        yield mock_agent

def test_chat_endpoint_authenticated(mock_travel_agent, test_user, user_token_headers):
    """Test the chat endpoint with authentication."""
    # Setup mock
    mock_response = "Test response from agent"
    mock_travel_agent.process_message.return_value = mock_response
    
    # Make request
    response = client.post(
        "/api/v1/chat",
        headers=user_token_headers,
        json={"text": "Hello, test!"}
    )
    
    # Verify
    assert response.status_code == 200
    assert response.json() == {"response": mock_response}
    mock_travel_agent.process_message.assert_called_once_with("Hello, test!")

def test_chat_endpoint_unauthenticated():
    """Test the chat endpoint without authentication."""
    response = client.post(
        "/api/v1/chat",
        json={"text": "Hello, test!"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_chat_endpoint_empty_message(mock_travel_agent, user_token_headers):
    """Test the chat endpoint with an empty message."""
    response = client.post(
        "/api/v1/chat",
        headers=user_token_headers,
        json={"text": ""}
    )
    assert response.status_code == 422  # Validation error
    assert "String should have at least 1 character" in str(response.content)
