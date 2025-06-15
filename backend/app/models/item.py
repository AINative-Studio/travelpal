from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base

class Item(Base):
    """
    Item model representing user-owned items in the system.
    
    Attributes:
        title: The title of the item
        description: Detailed description of the item
        owner_id: Foreign key to the user who owns this item
        owner: Relationship to the User model
        created_at: Timestamp when the item was created
        updated_at: Timestamp when the item was last updated
    """
    __tablename__ = "items"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(200), index=True, nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    owner_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now()
    )
    
    # Relationships
    owner = relationship("User", back_populates="items")
    
    def __repr__(self) -> str:
        return f"<Item id={self.id} title='{self.title}'>"
    
    def to_dict(self) -> dict:
        """Convert the item to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
