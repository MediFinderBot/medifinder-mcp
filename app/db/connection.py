"""
Database connection module for the MedifinderMCP Server.
"""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Base class for SQLAlchemy models
Base = declarative_base()

@contextmanager
def db_session():
    """Context manager for database sessions.
    
    This ensures that sessions are properly closed and rolled back in case of exceptions.
    
    Yields:
        SQLAlchemy session: A database session
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def get_connection():
    """Get a raw database connection.
    
    Returns:
        Connection: A database connection object
    """
    return engine.raw_connection()

def init_db():
    """Initialize the database by creating all tables."""
    # Import all models to ensure they're registered with Base
    from app.models.medicines import Medicine
    
    Base.metadata.create_all(engine)
    logger.info("Database initialized")