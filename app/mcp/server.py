"""
MCP server module for the MedifinderMCP Server.
"""
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context

from app.config import MCP_SERVER_NAME, MCP_SERVER_DESCRIPTION, SERVER_VERSION
from app.db.connection import init_db

logger = logging.getLogger(__name__)

@dataclass
class AppContext:
    """Application context for lifespan management."""
    initialized: bool = False


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context.
    
    Args:
        server (FastMCP): The MCP server
        
    Yields:
        AppContext: The application context
    """
    # Initialize on startup
    logger.info("Initializing MCP server...")
    
    try:
        # Initialize the database
        init_db()
        
        # Create and yield the application context
        yield AppContext(initialized=True)
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        yield AppContext(initialized=False)
        
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down MCP server...")


def create_mcp_server():
    """Create the MCP server.
    
    Returns:
        FastMCP: The configured MCP server
    """
    # Create the MCP server
    mcp = FastMCP(
        MCP_SERVER_NAME,
        description=MCP_SERVER_DESCRIPTION,
        version=SERVER_VERSION,
        lifespan=app_lifespan,
        dependencies=["psycopg2-binary", "sqlalchemy"]
    )
    
    # Import and register tools
    from app.mcp.tools import register_tools
    register_tools(mcp)
    
    # Import and register resources
    from app.mcp.resources import register_resources
    register_resources(mcp)
    
    # Import and register prompts
    from app.mcp.prompts import register_prompts
    register_prompts(mcp)
    
    logger.info(f"MCP server '{MCP_SERVER_NAME}' created with version {SERVER_VERSION}")
    return mcp