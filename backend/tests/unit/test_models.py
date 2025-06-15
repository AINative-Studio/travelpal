"""
Unit tests for database models.

These tests verify the behavior of the SQLAlchemy models in isolation.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestUserModel:
    """Test cases for the User model."""

    @pytest.fixture
    async def test_user(self, db: AsyncSession) -> User:
        """Create a test user."""
        user = User(
            email=f"test_{id(self)}@example.com",
            hashed_password="hashedpassword123",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
        
    @pytest.fixture
    def cleanup(self, db: AsyncSession):
        """Cleanup test data after each test."""
        yield
        # This will run after each test
        async def _cleanup():
            from sqlalchemy import text
            await db.execute(text("DELETE FROM users"))
            await db.commit()
        
        import asyncio
        asyncio.get_event_loop().run_until_complete(_cleanup())

    @pytest.mark.asyncio
    async def test_create_user(self, db: AsyncSession, cleanup) -> None:
        """
        Scenario: Create a new user
        Given a valid email and hashed password
        When a new User is created
        Then the user should be saved to the database with the correct attributes
        """
        # Arrange
        email = f"test_create_{id(self)}@example.com"
        hashed_password = "hashedpassword123"
        full_name = "Test User"

        # Act
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Assert
        assert user.id is not None
        assert user.email == email
        assert user.hashed_password == hashed_password
        assert user.full_name == full_name
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_to_dict(self, db: AsyncSession, test_user: User) -> None:
        """
        Scenario: Convert user to dictionary
        Given a user exists in the database
        When to_dict() is called on the user
        Then it should return a dictionary with the correct keys and values
        """
        # Arrange - using test_user fixture
        user = test_user

        # Act
        user_dict = user.to_dict()

        # Assert
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == user.id
        assert user_dict["email"] == user.email
        assert user_dict["full_name"] == user.full_name
        assert user_dict["is_active"] is True
        assert user_dict["is_superuser"] is False
        assert "hashed_password" not in user_dict  # Sensitive data should not be included
        assert "created_at" in user_dict
        assert "updated_at" in user_dict

    @pytest.mark.asyncio
    async def test_user_repr(self, db: AsyncSession, test_user: User) -> None:
        """
        Scenario: Get string representation of a user
        Given a user exists in the database
        When repr() is called on the user
        Then it should return a string containing the user's id and email
        """
        # Arrange - using test_user fixture
        user = test_user

        # Act
        user_repr = repr(user)

        # Assert
        assert f"id={user.id}" in user_repr
        assert f"email='{user.email}'" in user_repr

    @pytest.mark.parametrize("full_name,expected_display,email_prefix", [
        ("John Doe", "John Doe", "test_display_1"),
        (None, "test_display_2", "test_display_2"),
    ])
    @pytest.mark.asyncio
    async def test_display_name_property(
        self, db: AsyncSession, full_name: str, expected_display: str, email_prefix: str
    ) -> None:
        """
        Scenario: Get user's display name
        Given a user with or without a full name
        When the display_name property is accessed
        Then it should return the full name if available, otherwise the email username
        """
        # Create a new user with the specified full_name
        email = f"{email_prefix}_{id(self)}@example.com"
        user = User(
            email=email,
            hashed_password="hashedpassword123",
            full_name=full_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Act
        display_name = user.display_name

        # Assert
        if full_name is not None:
            assert display_name == expected_display
        else:
            # When full_name is None, display_name should be the part before @ in email
            assert display_name == email.split('@')[0]
