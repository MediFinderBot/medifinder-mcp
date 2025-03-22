#!/usr/bin/env python3
"""
MedifinderMCP Server - Main Entry Point
A Model Context Protocol server for medicine inventory queries.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("medifinder-mcp")

# Import the MCP server
from app.mcp.server import create_mcp_server

def main():
    """Main entry point for the application."""
    logger.info("Starting MedifinderMCP Server...")
    
    # Create and run the MCP server
    mcp_server = create_mcp_server()
    
    # Run the server
    try:
        mcp_server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete.")

if __name__ == "__main__":
    main()