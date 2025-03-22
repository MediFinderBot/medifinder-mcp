"""
Product model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class Product(Base, BaseModel):
    """Product model representing a row in the product table."""
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey('product_type.type_id'))
    description = Column(String)
    dosage_form = Column(String)
    strength = Column(String)
    
    # Relationships
    product_type = relationship("ProductType", 
                               back_populates="products",
                               primaryjoin="Product.type_id == ProductType.type_id",
                               foreign_keys=[type_id])
    inventories = relationship("Inventory", 
                              back_populates="product",
                              primaryjoin="Product.product_id == Inventory.product_id",
                              foreign_keys="Inventory.product_id")
    
    def __repr__(self):
        """String representation of the product."""
        return f"<Product(product_id={self.product_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert the product to a dictionary.
        
        Returns:
            dict: Dictionary representation of the product
        """
        result = {
            "product_id": self.product_id,
            "code": self.code,
            "name": self.name,
            "type_id": self.type_id,
            "description": self.description,
            "dosage_form": self.dosage_form,
            "strength": self.strength,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Safely add type_name if product_type is already loaded
        try:
            if self.product_type:
                result["type_name"] = self.product_type.name
        except:
            # Ignore if product_type is not loaded or session is closed
            result["type_name"] = None
            
        return result