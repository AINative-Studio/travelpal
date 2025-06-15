"""
CRUD operations for User model.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.models.user import User
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """
    CRUD operations for User model.
    """

    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_multi(
        db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get multiple users with pagination."""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, *, obj_in: Dict[str, Any]) -> User:
        """Create a new user."""
        db_obj = User(
            email=obj_in["email"],
            hashed_password=get_password_hash(obj_in["password"]),
            full_name=obj_in.get("full_name"),
            is_superuser=obj_in.get("is_superuser", False),
            is_active=obj_in.get("is_active", True),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(
        db: AsyncSession, *, db_obj: User, obj_in: Dict[str, Any]
    ) -> User:
        """Update a user."""
        update_data = obj_in.copy()
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def remove(db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Delete a user."""
        user = await CRUDUser.get(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
        return user

    @staticmethod
    async def authenticate(
        db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user."""
        user = await CRUDUser.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# Create a singleton instance
user = CRUDUser()
