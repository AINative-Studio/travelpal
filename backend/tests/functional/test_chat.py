"""
Functional tests for the chat API.

These tests verify the complete user flow for the chat functionality.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.services.langchain.agent import TravelAgent

# Import test fixtures
pytest_plugins = [
    "tests.async_db",  # This imports the async_db fixture from tests/async_db.py
]

# Helper function to get auth headers
def get_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestChatEndpoints:
    """Test cases for chat endpoints."""

    @pytest.mark.asyncio
    async def test_chat_endpoint_requires_auth(self, async_client) -> None:
        """
        Scenario: Access chat endpoint without authentication
        Given an unauthenticated user
        When a POST request is made to /api/v1/chat
        Then it should return a 401 Unauthorized status code
        """
        # Act
        response = await async_client.post(
            f"{settings.API_V1_STR}/chat",
            json={"text": "Hello"},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json().get("detail", "")

    @pytest.mark.asyncio
    @patch("app.services.langchain.agent.TravelAgent.process_message")
    async def test_chat_endpoint_with_valid_auth(
        self, mock_process_message: MagicMock, async_client, test_user: dict
    ) -> None:
        """
        Scenario: Send a chat message with valid authentication
        Given an authenticated user
        When a POST request is made to /api/v1/chat with a message
        Then it should return a 200 OK status code with a response
        """
        # Arrange
        mock_response = "I'm here to help with your travel plans!"
        mock_process_message.return_value = mock_response
        
        token = create_access_token(subject=str(test_user["id"]))
        message = "What can you do?"

        # Act
        response = await async_client.post(
            f"{settings.API_V1_STR}/chat",
            json={"text": message},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "response" in response_data
        assert response_data["response"] == mock_response
        mock_process_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_status,expected_detail", [
        ("", 422, [{"type": "string_too_short", "loc": ["body", "text"], "msg": "String should have at least 1 character", "input": "", "ctx": {"min_length": 1}}]),
    ])
    async def test_chat_endpoint_with_empty_message(
        self, message: str, expected_status: int, expected_detail: list,
        async_client, test_user: dict
    ) -> None:
        """
        Scenario: Send an empty chat message
        Given an authenticated user
        When a POST request is made to /api/v1/chat with an empty message
        Then it should return a 422 Unprocessable Entity status code with validation error
        """
        # Arrange
        token = create_access_token(subject=str(test_user["id"]))

        # Act
        response = await async_client.post(
            f"{settings.API_V1_STR}/chat",
            json={"text": message},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Assert
        assert response.status_code == expected_status
        assert response.json()["detail"] == expected_detail

    @pytest.mark.asyncio
    @patch("app.services.langchain.agent.TravelAgent.process_message")
    @pytest.mark.parametrize("message,expected_status,expected_response", [
        ("Hello!", 200, "I'm here to help!"),
        ("", 422, None),  # Empty string should return 422, not 400
    ])
    async def test_chat_endpoint_with_different_messages(
        self, mock_process_message: MagicMock, message: str, expected_status: int,
        expected_response: str, async_client, test_user: dict
    ) -> None:
        """
        Scenario: Test chat endpoint with different message inputs
        Given an authenticated user
        When a POST request is made to /api/v1/chat with different message inputs
        Then it should handle each case appropriately
        """
        # Arrange
        if expected_status == status.HTTP_200_OK:
            mock_process_message.return_value = expected_response
            
        token = create_access_token(subject=str(test_user["id"]))

        # Act
        response = await async_client.post(
            f"{settings.API_V1_STR}/chat",
            json={"text": message},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.json()["response"] == expected_response
            mock_process_message.assert_called_once_with(message)
        else:
            assert "detail" in response.json()
            
    @pytest.mark.asyncio
    @patch("app.services.langchain.agent.TravelAgent.process_message")
    async def test_chat_endpoint_with_agent_error(
        self, mock_process_message: MagicMock, async_client, test_user: dict
    ) -> None:
        """
        Scenario: Test chat endpoint when the agent raises an exception
        Given an authenticated user
        When the travel agent raises an exception
        Then it should return a 500 Internal Server Error
        """
        # Arrange
        mock_process_message.side_effect = Exception("Agent error")
        token = create_access_token(subject=str(test_user["id"]))
        
        # Act
        response = await async_client.post(
            f"{settings.API_V1_STR}/chat",
            json={"text": "Hello"},
            headers={"Authorization": f"Bearer {token}"},
        )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.json()
