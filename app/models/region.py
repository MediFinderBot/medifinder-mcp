"""
Region model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class Region(Base, BaseModel):
    """Region model representing a row in the region table."""
    __tablename__ = 'regions'
    
    region_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String)
    
    # Relationships
    medical_centers = relationship("MedicalCenter", 
                                  back_populates="region", 
                                  primaryjoin="Region.region_id == MedicalCenter.region_id",
                                  foreign_keys="MedicalCenter.region_id")
    
    def __repr__(self):
        """String representation of the region."""
        return f"<Region(region_id={self.region_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert the region to a dictionary.
        
        Returns:
            dict: Dictionary representation of the region
        """
        return {
            "region_id": self.region_id,
            "name": self.name,
            "code": self.code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }