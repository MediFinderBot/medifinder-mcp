"""
User model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class User(Base, BaseModel):
    """User model representing a row in the user table."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=False, unique=True)
    name = Column(String)
    preferred_location = Column(String)
    
    # Relationships
    search_history = relationship("SearchHistory", 
                                 back_populates="user",
                                 primaryjoin="User.user_id == SearchHistory.user_id",
                                 foreign_keys="SearchHistory.user_id")
    
    def __repr__(self):
        """String representation of the user."""
        return f"<User(user_id={self.user_id}, phone_number='{self.phone_number}')>"
    
    def to_dict(self):
        """Convert the user to a dictionary.
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "name": self.name,
            "preferred_location": self.preferred_location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }