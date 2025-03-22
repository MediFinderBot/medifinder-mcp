"""
Base model module for the MedifinderMCP Server.
"""
from sqlalchemy import Column, DateTime, func
from app.db.connection import Base

class BaseModel(object):
    """Base model with created and updated timestamps."""
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())