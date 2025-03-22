"""
Search History model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class SearchHistory(Base, BaseModel):
    """Search History model representing a row in the search_history table."""
    __tablename__ = 'search_history'
    
    search_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    product_query = Column(String)
    location_query = Column(String)
    search_radius = Column(Float)
    results_count = Column(Integer)
    
    # Relationships
    user = relationship("User", 
                       back_populates="search_history",
                       primaryjoin="SearchHistory.user_id == User.user_id",
                       foreign_keys=[user_id])
    
    def __repr__(self):
        """String representation of the search history."""
        return f"<SearchHistory(search_id={self.search_id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert the search history to a dictionary.
        
        Returns:
            dict: Dictionary representation of the search history
        """
        return {
            "search_id": self.search_id,
            "user_id": self.user_id,
            "product_query": self.product_query,
            "location_query": self.location_query,
            "search_radius": self.search_radius,
            "results_count": self.results_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }