"""
Medical Center model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class MedicalCenter(Base, BaseModel):
    """Medical Center model representing a row in the medical_center table."""
    __tablename__ = 'medical_centers'
    
    center_id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('region.region_id'))
    category = Column(String)
    reporter_name = Column(String)
    institution_type = Column(String)
    reporter_type = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    region = relationship("Region", 
                         back_populates="medical_centers",
                         primaryjoin="MedicalCenter.region_id == Region.region_id",
                         foreign_keys=[region_id])
    inventories = relationship("Inventory", 
                              back_populates="medical_center",
                              primaryjoin="MedicalCenter.center_id == Inventory.center_id",
                              foreign_keys="Inventory.center_id")
    
    def __repr__(self):
        """String representation of the medical center."""
        return f"<MedicalCenter(center_id={self.center_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert the medical center to a dictionary.
        
        Returns:
            dict: Dictionary representation of the medical center
        """
        return {
            "center_id": self.center_id,
            "code": self.code,
            "name": self.name,
            "region_id": self.region_id,
            "region_name": self.region.name if self.region else None,
            "category": self.category,
            "reporter_name": self.reporter_name,
            "institution_type": self.institution_type,
            "reporter_type": self.reporter_type,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }