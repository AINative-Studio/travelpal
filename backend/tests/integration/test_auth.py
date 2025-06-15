"""
Integration tests for authentication endpoints.

These tests verify the interaction between the authentication endpoints
and the database.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_login_access_token(self, client: TestClient, test_user: dict) -> None:
        """
        Scenario: Login with valid credentials
        Given a registered user
        When a POST request is made to /api/v1/auth/login/access-token with valid credentials
        Then it should return a valid access token
        """
        # Arrange
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"],
        }

        # Act
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    def test_login_access_token_invalid_credentials(self, client: TestClient) -> None:
        """
        Scenario: Login with invalid credentials
        Given a non-existent user
        When a POST request is made to /api/v1/auth/login/access-token with invalid credentials
        Then it should return a 400 status code with an error message
        """
        # Arrange
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        # Act
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect email or password" in response.json()["detail"]

    def test_test_token_valid_token(self, client: TestClient, test_user: dict) -> None:
        """
        Scenario: Test a valid access token
        Given a valid access token
        When a POST request is made to /api/v1/auth/test-token
        Then it should return the user information
        """
        # Arrange
        token = create_access_token(subject=test_user["email"])

        # Act
        response = client.post(
            f"{settings.API_V1_STR}/auth/test-token",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["email"] == test_user["email"]
        assert user_data["is_active"] is True
        assert "hashed_password" not in user_data  # Sensitive data should not be included

    def test_test_token_invalid_token(self, client: TestClient) -> None:
        """
        Scenario: Test an invalid access token
        Given an invalid access token
        When a POST request is made to /api/v1/auth/test-token
        Then it should return a 401 status code with an error message
        """
        # Act
        response = client.post(
            f"{settings.API_V1_STR}/auth/test-token",
            headers={"Authorization": "Bearer invalidtoken"},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["detail"]
