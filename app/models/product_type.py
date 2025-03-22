"""
Product Type model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class ProductType(Base, BaseModel):
    """Product Type model representing a row in the product_type table."""
    __tablename__ = 'product_types'
    
    type_id = Column(Integer, primary_key=True)
    code = Column(String(1))
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Relationships
    products = relationship("Product", 
                           back_populates="product_type",
                           primaryjoin="ProductType.type_id == Product.type_id",
                           foreign_keys="Product.type_id")
    
    def __repr__(self):
        """String representation of the product type."""
        return f"<ProductType(type_id={self.type_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert the product type to a dictionary.
        
        Returns:
            dict: Dictionary representation of the product type
        """
        return {
            "type_id": self.type_id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }