"""
Inventory model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.db.connection import Base
from app.models.base import BaseModel

class Inventory(Base, BaseModel):
    """Inventory model representing a row in the inventory table."""
    __tablename__ = 'inventory'
    
    inventory_id = Column(Integer, primary_key=True)
    center_id = Column(Integer, ForeignKey('medical_center.center_id'))
    product_id = Column(Integer, ForeignKey('product.product_id'))
    current_stock = Column(Integer)
    avg_monthly_consumption = Column(Float)
    accumulated_consumption_4m = Column(Integer)
    measurement = Column(Float)
    last_month_consumption = Column(Integer)
    last_month_stock = Column(Integer)
    status_indicator = Column(String)
    cpma_12_months_ago = Column(Float)
    cpma_24_months_ago = Column(Float)
    cpma_36_months_ago = Column(Float)
    accumulated_consumption_12m = Column(Integer)
    report_date = Column(Date)
    status = Column(String)
    
    # Relationships
    medical_center = relationship("MedicalCenter", 
                                 back_populates="inventories",
                                 primaryjoin="Inventory.center_id == MedicalCenter.center_id",
                                 foreign_keys=[center_id])
    product = relationship("Product", 
                          back_populates="inventories",
                          primaryjoin="Inventory.product_id == Product.product_id",
                          foreign_keys=[product_id])
    
    def __repr__(self):
        """String representation of the inventory."""
        return f"<Inventory(inventory_id={self.inventory_id}, product_id={self.product_id}, center_id={self.center_id})>"
    
    def to_dict(self):
        """Convert the inventory to a dictionary.
        
        Returns:
            dict: Dictionary representation of the inventory
        """
        return {
            "inventory_id": self.inventory_id,
            "center_id": self.center_id,
            "product_id": self.product_id,
            "current_stock": self.current_stock,
            "avg_monthly_consumption": self.avg_monthly_consumption,
            "accumulated_consumption_4m": self.accumulated_consumption_4m,
            "measurement": self.measurement,
            "last_month_consumption": self.last_month_consumption,
            "last_month_stock": self.last_month_stock,
            "status_indicator": self.status_indicator,
            "cpma_12_months_ago": self.cpma_12_months_ago,
            "cpma_24_months_ago": self.cpma_24_months_ago,
            "cpma_36_months_ago": self.cpma_36_months_ago,
            "accumulated_consumption_12m": self.accumulated_consumption_12m,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "status": self.status,
            "center_name": self.medical_center.name if self.medical_center else None,
            "product_name": self.product.name if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }