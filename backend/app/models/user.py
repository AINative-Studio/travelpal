from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base

class User(Base):
    """
    User model representing application users.
    
    Attributes:
        email: Unique email address of the user
        hashed_password: Hashed password (never store plain text passwords)
        full_name: User's full name
        is_active: Whether the user account is active
        is_superuser: Whether the user has superuser privileges
        items: Relationship to items owned by this user
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    full_name: Optional[str] = Column(String(100), index=True, nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now()
    )
    
    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}'>"
    
    def to_dict(self) -> dict:
        """Convert the user object to a dictionary.
        
        Returns:
            dict: A dictionary representation of the user
        """
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
    @property
    def is_authenticated(self) -> bool:
        """Return whether the user is authenticated."""
        return True
    
    @property
    def display_name(self) -> str:
        """Return a display name for the user."""
        return self.full_name or self.email.split("@")[0]
    
    def to_dict(self) -> dict:
        """Convert the user to a dictionary, excluding sensitive data."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
